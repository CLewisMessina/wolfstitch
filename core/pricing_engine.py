# core/pricing_engine.py
"""
Dynamic Pricing Engine for Real-time Cloud GPU Pricing
Fetches current pricing from multiple cloud providers with robust fallbacks
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading

from .cost_calculator import GPUType

class ProviderStatus(Enum):
    ACTIVE = "active"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"

@dataclass
class PricingData:
    provider: str
    gpu_type: GPUType
    hourly_rate: float
    currency: str = "USD"
    timestamp: float = None
    confidence: float = 1.0  # 0-1 confidence in pricing accuracy
    spot_price: bool = False  # Whether this is spot pricing
    availability: str = "available"  # available, limited, unavailable

@dataclass
class ProviderInfo:
    name: str
    api_endpoint: Optional[str]
    rate_limit: int  # requests per hour
    timeout_seconds: int
    status: ProviderStatus
    last_success: Optional[float] = None
    error_count: int = 0

class DynamicPricingEngine:
    """Main coordinator for dynamic cloud GPU pricing"""
    
    def __init__(self):
        self.cache = PricingCache()
        self.providers = self._initialize_providers()
        self.fallback_data = self._load_fallback_data()
        self.rate_limiter = RateLimiter()
        self._lock = threading.Lock()
        logging.info("Dynamic Pricing Engine initialized")
    
    def _initialize_providers(self) -> Dict[str, ProviderInfo]:
        """Initialize cloud provider configurations"""
        return {
            'lambda_labs': ProviderInfo(
                name="Lambda Labs",
                api_endpoint="https://cloud.lambdalabs.com/api/v1/instance-types",
                rate_limit=100,  # requests per hour
                timeout_seconds=5,
                status=ProviderStatus.ACTIVE
            ),
            'vast_ai': ProviderInfo(
                name="Vast.ai",
                api_endpoint="https://console.vast.ai/api/v0/instances",
                rate_limit=1000,  # requests per day
                timeout_seconds=5,
                status=ProviderStatus.ACTIVE
            ),
            'runpod': ProviderInfo(
                name="RunPod",
                api_endpoint=None,  # No public API, use estimates
                rate_limit=0,
                timeout_seconds=0,
                status=ProviderStatus.ACTIVE
            )
        }
    
    def _load_fallback_data(self) -> Dict[str, Any]:
        """Load static fallback pricing data"""
        return {
            'cloud_hourly_rates': {
                GPUType.RTX_3090: {
                    "vast_ai": 0.25,
                    "runpod": 0.30
                },
                GPUType.RTX_4090: {
                    "vast_ai": 0.40,
                    "lambda_labs": 0.50,
                    "runpod": 0.45
                },
                GPUType.A100: {
                    "lambda_labs": 1.10,
                    "vast_ai": 0.90,
                    "runpod": 1.00
                },
                GPUType.H100: {
                    "lambda_labs": 2.50,
                    "runpod": 2.20
                },
                GPUType.V100: {
                    "vast_ai": 0.35,
                    "runpod": 0.40
                }
            },
            'local_hardware_costs': {
                GPUType.RTX_3090: {
                    "electricity_per_hour": 0.042,  # 350W * $0.12/kWh
                    "depreciation_per_hour": 0.038,  # $1200 / 3 years
                    "total_per_hour": 0.08
                },
                GPUType.RTX_4090: {
                    "electricity_per_hour": 0.054,  # 450W * $0.12/kWh
                    "depreciation_per_hour": 0.066,  # $1600 / 3 years
                    "total_per_hour": 0.12
                },
                GPUType.A100: {
                    "electricity_per_hour": 0.048,  # 400W * $0.12/kWh
                    "depreciation_per_hour": 0.570,  # $15000 / 3 years
                    "total_per_hour": 0.62
                }
            },
            'last_updated': time.time()
        }
    
    def get_current_rates(self, gpu_type: GPUType, 
                         providers: Optional[List[str]] = None) -> Dict[str, PricingData]:
        """
        Get current GPU pricing rates from multiple providers
        
        Args:
            gpu_type: GPU type to get pricing for
            providers: Optional list of specific providers to query
            
        Returns:
            Dictionary mapping provider names to pricing data
        """
        
        if providers is None:
            providers = list(self.providers.keys())
        
        # Check cache first
        cached_rates = {}
        for provider in providers:
            cached_data = self.cache.get_pricing(provider, gpu_type)
            if cached_data:
                cached_rates[provider] = cached_data
        
        # If we have fresh cached data for all providers, return it
        if len(cached_rates) == len(providers):
            logging.info(f"Returning cached pricing for {gpu_type.value}")
            return cached_rates
        
        # Fetch fresh data for providers not in cache
        fresh_rates = self._fetch_fresh_rates(gpu_type, providers)
        
        # Combine cached and fresh data
        all_rates = {**cached_rates, **fresh_rates}
        
        # If no providers returned data, use fallback
        if not all_rates:
            logging.warning(f"No pricing data available, using fallback for {gpu_type.value}")
            return self._get_fallback_rates(gpu_type)
        
        return all_rates
    
    def _fetch_fresh_rates(self, gpu_type: GPUType, 
                          providers: List[str]) -> Dict[str, PricingData]:
        """Fetch fresh pricing data from providers"""
        
        rates = {}
        
        for provider in providers:
            # Check rate limiting
            if not self.rate_limiter.can_request(provider):
                logging.warning(f"Rate limited for provider {provider}")
                continue
            
            try:
                pricing_data = self._fetch_provider_pricing(provider, gpu_type)
                if pricing_data:
                    rates[provider] = pricing_data
                    # Cache the result
                    self.cache.set_pricing(provider, gpu_type, pricing_data)
                    # Update provider status
                    self.providers[provider].status = ProviderStatus.ACTIVE
                    self.providers[provider].last_success = time.time()
                    self.providers[provider].error_count = 0
                    
            except Exception as e:
                logging.error(f"Failed to fetch pricing from {provider}: {e}")
                self.providers[provider].error_count += 1
                if self.providers[provider].error_count > 3:
                    self.providers[provider].status = ProviderStatus.ERROR
        
        return rates
    
    def _fetch_provider_pricing(self, provider: str, gpu_type: GPUType) -> Optional[PricingData]:
        """Fetch pricing from a specific provider"""
        
        provider_info = self.providers.get(provider)
        if not provider_info or provider_info.status != ProviderStatus.ACTIVE:
            return None
        
        if provider == 'lambda_labs':
            return self._fetch_lambda_labs_pricing(gpu_type)
        elif provider == 'vast_ai':
            return self._fetch_vast_ai_pricing(gpu_type)
        elif provider == 'runpod':
            return self._fetch_runpod_pricing(gpu_type)
        else:
            logging.warning(f"Unknown provider: {provider}")
            return None
    
    def _fetch_lambda_labs_pricing(self, gpu_type: GPUType) -> Optional[PricingData]:
        """Fetch pricing from Lambda Labs API"""
        
        # GPU type mapping for Lambda Labs
        gpu_mapping = {
            GPUType.RTX_4090: "gpu_1x_rtx4090",
            GPUType.A100: "gpu_1x_a100",
            GPUType.H100: "gpu_1x_h100"
        }
        
        lambda_gpu_type = gpu_mapping.get(gpu_type)
        if not lambda_gpu_type:
            return None
        
        try:
            # Simulate API call (replace with actual implementation)
            # In real implementation, use aiohttp or requests here
            import requests
            
            provider_info = self.providers['lambda_labs']
            response = requests.get(
                provider_info.api_endpoint,
                timeout=provider_info.timeout_seconds
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract pricing for the specific GPU type
                for instance in data.get('data', []):
                    if instance.get('name') == lambda_gpu_type:
                        price_cents_per_hour = instance.get('price_cents_per_hour', 0)
                        hourly_rate = price_cents_per_hour / 100  # Convert cents to dollars
                        
                        return PricingData(
                            provider='lambda_labs',
                            gpu_type=gpu_type,
                            hourly_rate=hourly_rate,
                            timestamp=time.time(),
                            confidence=0.95,  # Lambda Labs has reliable pricing
                            availability=instance.get('regions_with_capacity_available', {})
                        )
            
        except requests.RequestException as e:
            logging.error(f"Lambda Labs API error: {e}")
        except Exception as e:
            logging.error(f"Lambda Labs parsing error: {e}")
        
        return None
    
    def _fetch_vast_ai_pricing(self, gpu_type: GPUType) -> Optional[PricingData]:
        """Fetch pricing from Vast.ai API"""
        
        # GPU type mapping for Vast.ai
        gpu_mapping = {
            GPUType.RTX_3090: "RTX 3090",
            GPUType.RTX_4090: "RTX 4090",
            GPUType.A100: "A100",
            GPUType.V100: "V100"
        }
        
        vast_gpu_type = gpu_mapping.get(gpu_type)
        if not vast_gpu_type:
            return None
        
        try:
            # Simulate Vast.ai API call
            # In practice, Vast.ai has complex spot pricing
            # This would require searching available instances
            
            # For now, return spot pricing estimate with lower confidence
            fallback_rates = self.fallback_data['cloud_hourly_rates'].get(gpu_type, {})
            vast_rate = fallback_rates.get('vast_ai')
            
            if vast_rate:
                # Add some variance to simulate spot pricing
                import random
                spot_multiplier = random.uniform(0.7, 1.3)  # ±30% variance
                spot_rate = vast_rate * spot_multiplier
                
                return PricingData(
                    provider='vast_ai',
                    gpu_type=gpu_type,
                    hourly_rate=spot_rate,
                    timestamp=time.time(),
                    confidence=0.7,  # Lower confidence for spot pricing
                    spot_price=True,
                    availability="variable"
                )
                
        except Exception as e:
            logging.error(f"Vast.ai pricing error: {e}")
        
        return None
    
    def _fetch_runpod_pricing(self, gpu_type: GPUType) -> Optional[PricingData]:
        """Get RunPod pricing estimates (no public API)"""
        
        # RunPod doesn't have a public API, so use educated estimates
        # based on their typical pricing structure
        
        fallback_rates = self.fallback_data['cloud_hourly_rates'].get(gpu_type, {})
        runpod_rate = fallback_rates.get('runpod')
        
        if runpod_rate:
            return PricingData(
                provider='runpod',
                gpu_type=gpu_type,
                hourly_rate=runpod_rate,
                timestamp=time.time(),
                confidence=0.8,  # Reasonable confidence in estimates
                spot_price=False,
                availability="community"
            )
        
        return None
    
    def _get_fallback_rates(self, gpu_type: GPUType) -> Dict[str, PricingData]:
        """Get fallback pricing when all providers fail"""
        
        fallback_rates = {}
        gpu_rates = self.fallback_data['cloud_hourly_rates'].get(gpu_type, {})
        
        for provider, rate in gpu_rates.items():
            fallback_rates[provider] = PricingData(
                provider=provider,
                gpu_type=gpu_type,
                hourly_rate=rate,
                timestamp=time.time(),
                confidence=0.5,  # Lower confidence for fallback data
                spot_price=False,
                availability="unknown"
            )
        
        return fallback_rates
    
    def get_local_hardware_costs(self, gpu_type: GPUType) -> Optional[PricingData]:
        """Calculate local hardware costs (electricity + depreciation)"""
        
        local_costs = self.fallback_data['local_hardware_costs'].get(gpu_type)
        if not local_costs:
            return None
        
        return PricingData(
            provider='local_hardware',
            gpu_type=gpu_type,
            hourly_rate=local_costs['total_per_hour'],
            timestamp=time.time(),
            confidence=0.9,  # High confidence in local calculations
            spot_price=False,
            availability="owned"
        )
    
    def estimate_cloud_training_cost(self, model_params: int, dataset_tokens: int, 
                                   provider: str, gpu_type: GPUType,
                                   gpu_count: int = 1) -> Dict[str, Any]:
        """
        Estimate complete cloud training cost for a model
        
        Args:
            model_params: Number of model parameters
            dataset_tokens: Training dataset size in tokens
            provider: Cloud provider name
            gpu_type: GPU type to use
            gpu_count: Number of GPUs
            
        Returns:
            Detailed cost breakdown
        """
        
        # Get current pricing
        rates = self.get_current_rates(gpu_type, [provider])
        pricing_data = rates.get(provider)
        
        if not pricing_data:
            raise ValueError(f"No pricing available for {provider} {gpu_type.value}")
        
        # Calculate training time (simplified Chinchilla scaling)
        # This would integrate with the cost calculator's more sophisticated estimates
        compute_budget = 6 * model_params * dataset_tokens  # FLOPs
        
        # GPU performance estimates (TFLOPS)
        gpu_performance = {
            GPUType.RTX_3090: 35.6,
            GPUType.RTX_4090: 83.0,
            GPUType.A100: 312.0,
            GPUType.H100: 989.0,
            GPUType.V100: 125.0
        }
        
        total_tflops = gpu_performance.get(gpu_type, 50.0) * gpu_count
        efficiency_factor = 0.4  # 40% efficiency is realistic
        effective_flops_per_second = total_tflops * 1e12 * efficiency_factor
        
        training_hours = max(compute_budget / effective_flops_per_second / 3600, 0.5)
        
        # Calculate costs
        compute_cost = pricing_data.hourly_rate * gpu_count * training_hours
        overhead_cost = compute_cost * 0.15  # 15% for storage, networking
        total_cost = compute_cost + overhead_cost
        
        return {
            'provider': provider,
            'gpu_type': gpu_type.value,
            'gpu_count': gpu_count,
            'training_hours': round(training_hours, 2),
            'hourly_rate': pricing_data.hourly_rate,
            'compute_cost': round(compute_cost, 2),
            'overhead_cost': round(overhead_cost, 2),
            'total_cost': round(total_cost, 2),
            'confidence': pricing_data.confidence,
            'spot_pricing': pricing_data.spot_price,
            'pricing_timestamp': pricing_data.timestamp,
            'notes': [
                f"Based on {provider} pricing",
                f"Includes 15% overhead for storage/networking",
                f"Efficiency factor: {efficiency_factor*100}%"
            ]
        }
    
    def get_pricing_trends(self, provider: str, gpu_type: GPUType, 
                          days: int = 7) -> Dict[str, Any]:
        """Get historical pricing trends (placeholder for future implementation)"""
        
        # This would query historical data from cache or database
        # For now, return placeholder data
        
        current_rate = self.get_current_rates(gpu_type, [provider]).get(provider)
        if not current_rate:
            return {"error": "No current pricing available"}
        
        # Simulate trend data
        import random
        trend_data = []
        base_rate = current_rate.hourly_rate
        
        for day in range(days):
            # Simulate daily price variations
            daily_rate = base_rate * random.uniform(0.9, 1.1)
            trend_data.append({
                'date': time.time() - (days - day) * 86400,
                'rate': round(daily_rate, 3)
            })
        
        return {
            'provider': provider,
            'gpu_type': gpu_type.value,
            'days': days,
            'current_rate': current_rate.hourly_rate,
            'average_rate': round(sum(d['rate'] for d in trend_data) / len(trend_data), 3),
            'trend_data': trend_data,
            'note': "Historical trends coming in future update"
        }
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get current status of all providers"""
        
        status_report = {}
        
        for name, provider in self.providers.items():
            status_report[name] = {
                'name': provider.name,
                'status': provider.status.value,
                'last_success': provider.last_success,
                'error_count': provider.error_count,
                'rate_limit': provider.rate_limit,
                'can_request': self.rate_limiter.can_request(name)
            }
        
        return {
            'providers': status_report,
            'cache_stats': self.cache.get_stats(),
            'last_updated': time.time()
        }


class PricingCache:
    """Simple in-memory cache for pricing data with TTL"""
    
    def __init__(self, ttl_seconds: int = 3600):  # 1 hour TTL
        self.cache = {}
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
    
    def _cache_key(self, provider: str, gpu_type: GPUType) -> str:
        return f"{provider}:{gpu_type.value}"
    
    def get_pricing(self, provider: str, gpu_type: GPUType) -> Optional[PricingData]:
        """Get cached pricing data if still valid"""
        
        with self._lock:
            key = self._cache_key(provider, gpu_type)
            entry = self.cache.get(key)
            
            if entry:
                data, timestamp = entry
                if time.time() - timestamp < self.ttl_seconds:
                    return data
                else:
                    # Remove expired entry
                    del self.cache[key]
        
        return None
    
    def set_pricing(self, provider: str, gpu_type: GPUType, data: PricingData):
        """Cache pricing data with timestamp"""
        
        with self._lock:
            key = self._cache_key(provider, gpu_type)
            self.cache[key] = (data, time.time())
    
    def clear_cache(self):
        """Clear all cached data"""
        with self._lock:
            self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_entries = len(self.cache)
            current_time = time.time()
            valid_entries = sum(1 for _, timestamp in self.cache.values() 
                              if current_time - timestamp < self.ttl_seconds)
            
            return {
                'total_entries': total_entries,
                'valid_entries': valid_entries,
                'expired_entries': total_entries - valid_entries,
                'ttl_seconds': self.ttl_seconds
            }


class RateLimiter:
    """Simple rate limiter to prevent API abuse"""
    
    def __init__(self):
        self.requests = {}  # provider -> list of request timestamps
        self._lock = threading.Lock()
    
    def can_request(self, provider: str) -> bool:
        """Check if we can make a request to provider without exceeding rate limit"""
        
        with self._lock:
            current_time = time.time()
            
            # Clean old requests (older than 1 hour)
            if provider in self.requests:
                self.requests[provider] = [
                    req_time for req_time in self.requests[provider]
                    if current_time - req_time < 3600
                ]
            else:
                self.requests[provider] = []
            
            # Check rate limits
            provider_info = {
                'lambda_labs': 100,  # per hour
                'vast_ai': 42,       # 1000 per day ≈ 42 per hour
                'runpod': 1000       # No API, high limit
            }
            
            limit = provider_info.get(provider, 10)  # Default to 10/hour
            current_count = len(self.requests[provider])
            
            return current_count < limit
    
    def record_request(self, provider: str):
        """Record a request for rate limiting"""
        with self._lock:
            if provider not in self.requests:
                self.requests[provider] = []
            self.requests[provider].append(time.time())


# Convenience functions for easy integration
def get_gpu_pricing(gpu_type: GPUType, providers: List[str] = None) -> Dict[str, PricingData]:
    """Quick function to get current GPU pricing"""
    engine = DynamicPricingEngine()
    return engine.get_current_rates(gpu_type, providers)


def estimate_training_cost(model_params: int, dataset_tokens: int, 
                          gpu_type: GPUType = GPUType.RTX_4090) -> Dict[str, Any]:
    """Quick function to estimate training cost across providers"""
    engine = DynamicPricingEngine()
    
    results = {}
    providers = ['lambda_labs', 'vast_ai', 'runpod']
    
    for provider in providers:
        try:
            cost_estimate = engine.estimate_cloud_training_cost(
                model_params, dataset_tokens, provider, gpu_type
            )
            results[provider] = cost_estimate
        except Exception as e:
            logging.warning(f"Failed to estimate cost for {provider}: {e}")
    
    return results


# Export main classes and functions
__all__ = [
    'DynamicPricingEngine',
    'PricingData',
    'ProviderStatus',
    'get_gpu_pricing',
    'estimate_training_cost'
]