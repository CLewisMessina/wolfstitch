# core/cost_calculator.py
"""
Enhanced Cost Calculator Engine for AI Training Cost Analysis
Calculates training costs across multiple approaches and provides ROI analysis
"""

import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time

from .model_database import ModelParameterDatabase, ModelInfo, TrainingFeasibility, get_model_database

class TrainingApproach(Enum):
    LOCAL_FULL = "local_full"
    LOCAL_LORA = "local_lora"
    LOCAL_QLORA = "local_qlora"
    CLOUD_FULL = "cloud_full"
    CLOUD_LORA = "cloud_lora"
    API_FINETUNING = "api_finetuning"

class GPUType(Enum):
    RTX_3090 = "rtx_3090"
    RTX_4090 = "rtx_4090"
    A100 = "a100"
    H100 = "h100"
    V100 = "v100"

@dataclass
class GPUConfig:
    gpu_type: GPUType
    memory_gb: int
    compute_tflops: float  # Tensor TFLOPS for AI workloads
    power_watts: int
    market_price_usd: Optional[int] = None  # For local ownership calculations

@dataclass
class TrainingConfig:
    approach: TrainingApproach
    gpu_config: GPUConfig
    gpu_count: int = 1
    precision: str = "fp16"  # fp32, fp16, bf16, int8, int4
    batch_size_per_gpu: Optional[int] = None
    gradient_accumulation: int = 1

@dataclass
class CostEstimate:
    approach_name: str
    total_cost_usd: float
    training_hours: float
    gpu_hours: float
    cost_breakdown: Dict[str, float]
    confidence: float  # 0-1 confidence in estimate
    notes: List[str]
    hardware_requirements: Dict[str, Any]

@dataclass
class ROIAnalysis:
    training_investment: float
    monthly_api_cost_current: float
    monthly_savings: float
    break_even_months: float
    projections: Dict[str, float]  # 6_months, 12_months, 24_months
    scenarios: List[Dict[str, Any]]
    recommendation: str
    confidence: float

class EnhancedCostCalculator:
    """Comprehensive AI training cost calculator with multiple approaches"""
    
    def __init__(self):
        self.model_db = get_model_database()
        self.gpu_configs = self._initialize_gpu_configs()
        self.pricing_data = self._initialize_pricing_data()
        logging.info("Enhanced Cost Calculator initialized")
    
    def _initialize_gpu_configs(self) -> Dict[GPUType, GPUConfig]:
        """Initialize GPU configuration database"""
        return {
            GPUType.RTX_3090: GPUConfig(
                gpu_type=GPUType.RTX_3090,
                memory_gb=24,
                compute_tflops=35.6,  # Tensor performance
                power_watts=350,
                market_price_usd=1200
            ),
            GPUType.RTX_4090: GPUConfig(
                gpu_type=GPUType.RTX_4090,
                memory_gb=24,
                compute_tflops=83.0,  # Tensor performance
                power_watts=450,
                market_price_usd=1600
            ),
            GPUType.A100: GPUConfig(
                gpu_type=GPUType.A100,
                memory_gb=80,  # A100 80GB variant
                compute_tflops=312.0,  # Tensor performance
                power_watts=400,
                market_price_usd=15000
            ),
            GPUType.H100: GPUConfig(
                gpu_type=GPUType.H100,
                memory_gb=80,
                compute_tflops=989.0,  # Tensor performance
                power_watts=700,
                market_price_usd=30000
            ),
            GPUType.V100: GPUConfig(
                gpu_type=GPUType.V100,
                memory_gb=32,
                compute_tflops=125.0,  # Tensor performance
                power_watts=300,
                market_price_usd=8000
            )
        }
    
    def _initialize_pricing_data(self) -> Dict[str, Any]:
        """Initialize fallback pricing data"""
        return {
            # Cloud provider hourly rates (USD/hour)
            "cloud_hourly_rates": {
                GPUType.RTX_3090: {"vast_ai": 0.25, "runpod": 0.30},
                GPUType.RTX_4090: {"vast_ai": 0.40, "lambda_labs": 0.50, "runpod": 0.45},
                GPUType.A100: {"lambda_labs": 1.10, "vast_ai": 0.90, "runpod": 1.00},
                GPUType.H100: {"lambda_labs": 2.50, "runpod": 2.20},
                GPUType.V100: {"vast_ai": 0.35, "runpod": 0.40}
            },
            # Local electricity rates by region (USD/kWh)
            "electricity_rates": {
                "us_average": 0.12,
                "us_california": 0.25,
                "us_texas": 0.09,
                "eu_average": 0.20,
                "asia_average": 0.08
            },
            # API fine-tuning costs (USD per 1K tokens)
            "api_finetuning_costs": {
                "openai_gpt35": {"training": 0.008, "usage": 0.012},
                "openai_gpt4": {"training": 0.03, "usage": 0.06},
                "anthropic_claude": {"training": 0.025, "usage": 0.045}
            }
        }
    
    def calculate_comprehensive_costs(self, 
                                    dataset_tokens: int,
                                    target_model: str = "llama-2-7b",
                                    approaches: Optional[List[TrainingApproach]] = None,
                                    api_usage_monthly: int = 100000) -> Dict[str, Any]:
        """
        Calculate comprehensive training costs across multiple approaches
        
        Args:
            dataset_tokens: Size of training dataset in tokens
            target_model: Model to train (from model database)
            approaches: List of training approaches to evaluate
            api_usage_monthly: Monthly API usage in tokens for ROI analysis
            
        Returns:
            Comprehensive cost analysis with estimates and ROI
        """
        
        # Get model information
        model_info = self.model_db.get_model_info(target_model)
        if not model_info:
            raise ValueError(f"Model '{target_model}' not found in database")
        
        # Default approaches if not specified
        if approaches is None:
            approaches = self._get_recommended_approaches(model_info)
        
        # Calculate costs for each approach
        cost_estimates = []
        for approach in approaches:
            try:
                estimate = self._calculate_approach_cost(model_info, dataset_tokens, approach)
                cost_estimates.append(estimate)
            except Exception as e:
                logging.warning(f"Failed to calculate cost for {approach.value}: {e}")
        
        # Sort by total cost
        cost_estimates.sort(key=lambda x: x.total_cost_usd)
        
        # Generate ROI analysis
        roi_analysis = self._generate_roi_analysis(
            cost_estimates, model_info, api_usage_monthly
        )
        
        # Generate optimization recommendations
        recommendations = self._generate_optimization_recommendations(
            cost_estimates, model_info, dataset_tokens
        )
        
        return {
            "model_info": {
                "name": model_info.name,
                "display_name": model_info.display_name,
                "parameters": model_info.parameters,
                "training_feasibility": model_info.training_feasibility.value
            },
            "dataset_info": {
                "tokens": dataset_tokens,
                "optimal_tokens": self.model_db.estimate_chinchilla_tokens(model_info.parameters),
                "tokens_ratio": dataset_tokens / self.model_db.estimate_chinchilla_tokens(model_info.parameters)
            },
            "cost_estimates": [self._cost_estimate_to_dict(est) for est in cost_estimates],
            "roi_analysis": self._roi_analysis_to_dict(roi_analysis),
            "recommendations": recommendations,
            "calculation_metadata": {
                "timestamp": time.time(),
                "calculator_version": "1.0",
                "approaches_evaluated": len(cost_estimates)
            }
        }
    
    def _get_recommended_approaches(self, model_info: ModelInfo) -> List[TrainingApproach]:
        """Get recommended training approaches based on model characteristics"""
        approaches = []
        
        # Always include API fine-tuning if available
        if model_info.api_cost_per_1k_tokens:
            approaches.append(TrainingApproach.API_FINETUNING)
        
        # Local approaches for feasible models
        if model_info.training_feasibility in [TrainingFeasibility.LOCAL_FEASIBLE]:
            approaches.extend([
                TrainingApproach.LOCAL_FULL,
                TrainingApproach.LOCAL_LORA,
                TrainingApproach.LOCAL_QLORA
            ])
        
        # Cloud approaches for larger models
        if model_info.training_feasibility in [TrainingFeasibility.LOCAL_FEASIBLE, TrainingFeasibility.CLOUD_ONLY]:
            approaches.extend([
                TrainingApproach.CLOUD_FULL,
                TrainingApproach.CLOUD_LORA
            ])
        
        return approaches
    
    def _calculate_approach_cost(self, model_info: ModelInfo, dataset_tokens: int, approach: TrainingApproach) -> CostEstimate:
        """Calculate cost for a specific training approach"""
        
        if approach == TrainingApproach.API_FINETUNING:
            return self._calculate_api_finetuning_cost(model_info, dataset_tokens)
        elif approach.value.startswith("local_"):
            return self._calculate_local_training_cost(model_info, dataset_tokens, approach)
        elif approach.value.startswith("cloud_"):
            return self._calculate_cloud_training_cost(model_info, dataset_tokens, approach)
        else:
            raise ValueError(f"Unknown training approach: {approach}")
    
    def _calculate_local_training_cost(self, model_info: ModelInfo, dataset_tokens: int, approach: TrainingApproach) -> CostEstimate:
        """Calculate local training costs"""
        
        # Determine optimal GPU configuration
        gpu_config, gpu_count = self._select_optimal_gpu_config(model_info, approach)
        
        # Calculate memory requirements
        memory_required = self._calculate_memory_requirements(model_info, approach)
        
        # Calculate training time
        training_hours = self._calculate_training_time(
            model_info, dataset_tokens, gpu_config, gpu_count, approach
        )
        
        # Calculate costs
        electricity_cost = self._calculate_electricity_cost(gpu_config, gpu_count, training_hours)
        depreciation_cost = self._calculate_hardware_depreciation(gpu_config, gpu_count, training_hours)
        
        total_cost = electricity_cost + depreciation_cost
        
        # Build cost breakdown
        cost_breakdown = {
            "electricity": electricity_cost,
            "hardware_depreciation": depreciation_cost,
            "total_hardware_hours": training_hours * gpu_count
        }
        
        # Generate notes
        notes = []
        if memory_required > gpu_config.memory_gb * gpu_count:
            notes.append(f"Requires {math.ceil(memory_required/(gpu_config.memory_gb * gpu_count))}x more GPUs for memory")
        
        if approach == TrainingApproach.LOCAL_LORA:
            notes.append("LoRA training uses ~10% of parameters, faster but may reduce quality")
        elif approach == TrainingApproach.LOCAL_QLORA:
            notes.append("QLoRA uses 4-bit quantization, most memory efficient")
        
        return CostEstimate(
            approach_name=self._get_approach_display_name(approach, gpu_config),
            total_cost_usd=total_cost,
            training_hours=training_hours,
            gpu_hours=training_hours * gpu_count,
            cost_breakdown=cost_breakdown,
            confidence=0.8,  # Local estimates are fairly reliable
            notes=notes,
            hardware_requirements={
                "gpu_type": gpu_config.gpu_type.value,
                "gpu_count": gpu_count,
                "memory_required_gb": memory_required,
                "power_consumption_watts": gpu_config.power_watts * gpu_count
            }
        )
    
    def _calculate_cloud_training_cost(self, model_info: ModelInfo, dataset_tokens: int, approach: TrainingApproach) -> CostEstimate:
        """Calculate cloud training costs"""
        
        # Select optimal GPU for cloud training (prioritize performance)
        gpu_config, gpu_count = self._select_optimal_gpu_config(model_info, approach, cloud=True)
        
        # Calculate training time
        training_hours = self._calculate_training_time(
            model_info, dataset_tokens, gpu_config, gpu_count, approach
        )
        
        # Get cloud pricing (use average of available providers)
        hourly_rates = self.pricing_data["cloud_hourly_rates"].get(gpu_config.gpu_type, {})
        if not hourly_rates:
            raise ValueError(f"No cloud pricing available for {gpu_config.gpu_type.value}")
        
        avg_hourly_rate = sum(hourly_rates.values()) / len(hourly_rates)
        
        # Calculate costs
        compute_cost = avg_hourly_rate * gpu_count * training_hours
        
        # Add cloud overhead (storage, networking, etc.)
        overhead_cost = compute_cost * 0.15  # 15% overhead estimate
        
        total_cost = compute_cost + overhead_cost
        
        cost_breakdown = {
            "compute_hours": compute_cost,
            "cloud_overhead": overhead_cost,
            "total_gpu_hours": training_hours * gpu_count,
            "hourly_rate_per_gpu": avg_hourly_rate
        }
        
        notes = [
            f"Based on average pricing from {len(hourly_rates)} providers",
            f"Includes 15% overhead for storage and networking"
        ]
        
        if approach == TrainingApproach.CLOUD_LORA:
            notes.append("LoRA reduces training time and cost significantly")
        
        return CostEstimate(
            approach_name=self._get_approach_display_name(approach, gpu_config),
            total_cost_usd=total_cost,
            training_hours=training_hours,
            gpu_hours=training_hours * gpu_count,
            cost_breakdown=cost_breakdown,
            confidence=0.6,  # Cloud pricing varies
            notes=notes,
            hardware_requirements={
                "gpu_type": gpu_config.gpu_type.value,
                "gpu_count": gpu_count,
                "estimated_hourly_rate": avg_hourly_rate
            }
        )
    
    def _calculate_api_finetuning_cost(self, model_info: ModelInfo, dataset_tokens: int) -> CostEstimate:
        """Calculate API fine-tuning costs"""
        
        if not model_info.api_cost_per_1k_tokens:
            raise ValueError(f"No API pricing available for {model_info.name}")
        
        # Determine API service
        if "gpt-4" in model_info.name.lower():
            api_key = "openai_gpt4"
        elif "gpt-3.5" in model_info.name.lower():
            api_key = "openai_gpt35"
        elif "claude" in model_info.name.lower():
            api_key = "anthropic_claude"
        else:
            # Use model's API cost directly
            training_cost = (dataset_tokens / 1000) * model_info.api_cost_per_1k_tokens
            return CostEstimate(
                approach_name=f"API Fine-tuning ({model_info.display_name})",
                total_cost_usd=training_cost,
                training_hours=24,  # Typical API fine-tuning time
                gpu_hours=0,  # Managed service
                cost_breakdown={"api_training": training_cost},
                confidence=0.9,  # API pricing is reliable
                notes=["Managed service, no hardware required"],
                hardware_requirements={"gpu_type": "managed", "gpu_count": 0}
            )
        
        # Use detailed API pricing
        api_pricing = self.pricing_data["api_finetuning_costs"][api_key]
        training_cost = (dataset_tokens / 1000) * api_pricing["training"]
        
        cost_breakdown = {
            "training_cost": training_cost,
            "cost_per_1k_tokens": api_pricing["training"]
        }
        
        notes = [
            "Managed service with guaranteed uptime",
            "No hardware setup or maintenance required",
            f"Usage cost: ${api_pricing['usage']}/1K tokens"
        ]
        
        return CostEstimate(
            approach_name=f"API Fine-tuning ({model_info.display_name})",
            total_cost_usd=training_cost,
            training_hours=24,  # Estimated
            gpu_hours=0,
            cost_breakdown=cost_breakdown,
            confidence=0.95,
            notes=notes,
            hardware_requirements={"gpu_type": "managed", "gpu_count": 0}
        )
    
    def _select_optimal_gpu_config(self, model_info: ModelInfo, approach: TrainingApproach, cloud: bool = False) -> Tuple[GPUConfig, int]:
        """Select optimal GPU configuration for training"""
        
        memory_required = self._calculate_memory_requirements(model_info, approach)
        
        # For cloud, prioritize performance; for local, balance cost/performance
        if cloud:
            # Prefer A100 for cloud training
            gpu_configs = [self.gpu_configs[GPUType.A100], self.gpu_configs[GPUType.H100], self.gpu_configs[GPUType.RTX_4090]]
        else:
            # Prefer consumer GPUs for local training
            gpu_configs = [self.gpu_configs[GPUType.RTX_4090], self.gpu_configs[GPUType.RTX_3090], self.gpu_configs[GPUType.A100]]
        
        for gpu_config in gpu_configs:
            # Calculate minimum GPU count needed
            gpu_count = max(1, math.ceil(memory_required / gpu_config.memory_gb))
            
            # Check if configuration is reasonable
            if gpu_count <= 8:  # Reasonable multi-GPU setup
                return gpu_config, gpu_count
        
        # Fallback to best available option
        best_gpu = gpu_configs[0]
        gpu_count = math.ceil(memory_required / best_gpu.memory_gb)
        return best_gpu, gpu_count
    
    def _calculate_memory_requirements(self, model_info: ModelInfo, approach: TrainingApproach) -> float:
        """Calculate memory requirements in GB"""
        
        base_memory = model_info.gpu_memory_required
        
        if approach == TrainingApproach.LOCAL_FULL or approach == TrainingApproach.CLOUD_FULL:
            # Full fine-tuning requires 4x memory (model + gradients + optimizer states + activations)
            return base_memory * model_info.training_memory_multiplier
        elif approach == TrainingApproach.LOCAL_LORA or approach == TrainingApproach.CLOUD_LORA:
            # LoRA only trains ~0.1% of parameters
            return base_memory * 1.5  # Modest increase for LoRA parameters
        elif approach == TrainingApproach.LOCAL_QLORA:
            # QLoRA uses 4-bit quantization
            return base_memory * 0.7  # Reduced memory due to quantization
        else:
            return base_memory * model_info.training_memory_multiplier
    
    def _calculate_training_time(self, model_info: ModelInfo, dataset_tokens: int, 
                                gpu_config: GPUConfig, gpu_count: int, approach: TrainingApproach) -> float:
        """Calculate training time in hours"""
        
        # Calculate compute budget using Chinchilla scaling
        compute_budget = 6 * model_info.parameters * dataset_tokens  # FLOPs
        
        # Adjust for training approach
        if approach == TrainingApproach.LOCAL_LORA or approach == TrainingApproach.CLOUD_LORA:
            # LoRA typically requires 50% of full training time
            compute_budget *= 0.5
        elif approach == TrainingApproach.LOCAL_QLORA:
            # QLoRA is slower due to quantization overhead but trains fewer parameters
            compute_budget *= 0.6
        
        # Calculate effective compute capacity
        total_tflops = gpu_config.compute_tflops * gpu_count
        
        # Convert TFLOPS to FLOPS and calculate hours
        total_flops_per_second = total_tflops * 1e12
        
        # Add efficiency factor (real-world performance is lower than peak)
        efficiency_factor = 0.4  # 40% of peak performance is realistic
        effective_flops_per_second = total_flops_per_second * efficiency_factor
        
        training_seconds = compute_budget / effective_flops_per_second
        training_hours = training_seconds / 3600
        
        # Minimum training time (setup, checkpointing, etc.)
        return max(training_hours, 0.5)
    
    def _calculate_electricity_cost(self, gpu_config: GPUConfig, gpu_count: int, hours: float) -> float:
        """Calculate electricity cost for local training"""
        
        # System power = GPU power + 30% overhead for CPU, RAM, cooling
        system_power_watts = gpu_config.power_watts * gpu_count * 1.3
        
        # Convert to kWh
        kwh_used = (system_power_watts * hours) / 1000
        
        # Use average US electricity rate
        electricity_rate = self.pricing_data["electricity_rates"]["us_average"]
        
        return kwh_used * electricity_rate
    
    def _calculate_hardware_depreciation(self, gpu_config: GPUConfig, gpu_count: int, hours: float) -> float:
        """Calculate hardware depreciation cost for local training"""
        
        if not gpu_config.market_price_usd:
            return 0.0
        
        # Assume 3-year depreciation schedule with 20% residual value
        annual_depreciation = gpu_config.market_price_usd * 0.8 / 3
        hourly_depreciation = annual_depreciation / (365 * 24)
        
        return hourly_depreciation * gpu_count * hours
    
    def _generate_roi_analysis(self, cost_estimates: List[CostEstimate], 
                              model_info: ModelInfo, api_usage_monthly: int) -> ROIAnalysis:
        """Generate ROI analysis comparing training vs API usage"""
        
        if not cost_estimates:
            raise ValueError("No cost estimates available for ROI analysis")
        
        # Use the lowest cost option for ROI calculation
        best_estimate = cost_estimates[0]
        training_cost = best_estimate.total_cost_usd
        
        # Calculate current monthly API cost
        if model_info.api_cost_per_1k_tokens:
            monthly_api_cost = (api_usage_monthly / 1000) * model_info.api_cost_per_1k_tokens
        else:
            # Use average API cost for comparison
            monthly_api_cost = (api_usage_monthly / 1000) * 0.01  # $0.01/1K tokens average
        
        # Calculate savings and break-even
        monthly_savings = monthly_api_cost * 0.9  # Assume 90% savings after training
        
        if monthly_savings > 0:
            break_even_months = training_cost / monthly_savings
        else:
            break_even_months = float('inf')
        
        # Calculate projections
        projections = {
            "6_months": (monthly_savings * 6) - training_cost,
            "12_months": (monthly_savings * 12) - training_cost,
            "24_months": (monthly_savings * 24) - training_cost
        }
        
        # Generate recommendation
        if break_even_months < 2:
            recommendation = f"Excellent ROI - training pays for itself in {break_even_months:.1f} months"
        elif break_even_months < 6:
            recommendation = f"Good ROI - break-even in {break_even_months:.1f} months"
        elif break_even_months < 12:
            recommendation = f"Moderate ROI - break-even in {break_even_months:.1f} months"
        else:
            recommendation = "Training cost may not be justified for current usage level"
        
        return ROIAnalysis(
            training_investment=training_cost,
            monthly_api_cost_current=monthly_api_cost,
            monthly_savings=monthly_savings,
            break_even_months=break_even_months,
            projections=projections,
            scenarios=[],  # Will be populated with detailed scenarios
            recommendation=recommendation,
            confidence=0.8
        )
    
    def _generate_optimization_recommendations(self, cost_estimates: List[CostEstimate], 
                                             model_info: ModelInfo, dataset_tokens: int) -> List[str]:
        """Generate cost optimization recommendations"""
        
        recommendations = []
        
        if not cost_estimates:
            return ["No cost estimates available"]
        
        best_estimate = cost_estimates[0]
        
        # Cost-based recommendations
        if len(cost_estimates) > 1:
            savings_vs_most_expensive = ((cost_estimates[-1].total_cost_usd - best_estimate.total_cost_usd) / 
                                       cost_estimates[-1].total_cost_usd * 100)
            recommendations.append(
                f"Best approach saves {savings_vs_most_expensive:.0f}% vs most expensive option"
            )
        
        # Approach-specific recommendations
        if "lora" in best_estimate.approach_name.lower():
            recommendations.append("LoRA training offers excellent cost-performance balance")
        elif "qlora" in best_estimate.approach_name.lower():
            recommendations.append("QLoRA is most memory-efficient for large models")
        elif "local" in best_estimate.approach_name.lower():
            recommendations.append("Local training provides best long-term value")
        
        # Dataset size recommendations
        optimal_tokens = self.model_db.estimate_chinchilla_tokens(model_info.parameters)
        token_ratio = dataset_tokens / optimal_tokens
        
        if token_ratio < 0.1:
            recommendations.append("Dataset is quite small - consider data augmentation")
        elif token_ratio > 5:
            recommendations.append("Large dataset detected - excellent for model quality")
        
        # Hardware recommendations
        if best_estimate.hardware_requirements.get("gpu_count", 1) > 1:
            recommendations.append(
                f"Multi-GPU setup required ({best_estimate.hardware_requirements['gpu_count']} GPUs)"
            )
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _get_approach_display_name(self, approach: TrainingApproach, gpu_config: GPUConfig = None) -> str:
        """Get user-friendly display name for training approach"""
        
        approach_names = {
            TrainingApproach.LOCAL_FULL: "Local Full Fine-tuning",
            TrainingApproach.LOCAL_LORA: "Local LoRA",
            TrainingApproach.LOCAL_QLORA: "Local QLoRA",
            TrainingApproach.CLOUD_FULL: "Cloud Full Fine-tuning",
            TrainingApproach.CLOUD_LORA: "Cloud LoRA",
            TrainingApproach.API_FINETUNING: "API Fine-tuning"
        }
        
        base_name = approach_names[approach]
        
        if gpu_config and approach != TrainingApproach.API_FINETUNING:
            gpu_name = gpu_config.gpu_type.value.upper().replace("_", " ")
            return f"{base_name} ({gpu_name})"
        
        return base_name
    
    def _cost_estimate_to_dict(self, estimate: CostEstimate) -> Dict[str, Any]:
        """Convert CostEstimate to dictionary for JSON serialization"""
        return {
            "approach_name": estimate.approach_name,
            "total_cost_usd": round(estimate.total_cost_usd, 2),
            "training_hours": round(estimate.training_hours, 1),
            "gpu_hours": round(estimate.gpu_hours, 1),
            "cost_breakdown": {k: round(v, 2) for k, v in estimate.cost_breakdown.items()},
            "confidence": estimate.confidence,
            "notes": estimate.notes,
            "hardware_requirements": estimate.hardware_requirements
        }
    
    def _roi_analysis_to_dict(self, roi: ROIAnalysis) -> Dict[str, Any]:
        """Convert ROIAnalysis to dictionary for JSON serialization"""
        return {
            "training_investment": round(roi.training_investment, 2),
            "monthly_api_cost_current": round(roi.monthly_api_cost_current, 2),
            "monthly_savings": round(roi.monthly_savings, 2),
            "break_even_months": round(roi.break_even_months, 2) if roi.break_even_months != float('inf') else None,
            "projections": {k: round(v, 2) for k, v in roi.projections.items()},
            "recommendation": roi.recommendation,
            "confidence": roi.confidence
        }

# Convenience functions
def calculate_training_cost(dataset_tokens: int, model_name: str = "llama-2-7b") -> Dict[str, Any]:
    """Convenience function for quick cost calculation"""
    calculator = EnhancedCostCalculator()
    return calculator.calculate_comprehensive_costs(dataset_tokens, model_name)


def estimate_roi(training_cost: float, monthly_api_usage: int, api_cost_per_1k: float = 0.002) -> Dict[str, float]:
    """Quick ROI estimation"""
    monthly_api_cost = (monthly_api_usage / 1000) * api_cost_per_1k
    monthly_savings = monthly_api_cost * 0.9
    break_even_months = training_cost / monthly_savings if monthly_savings > 0 else float('inf')
    
    return {
        "training_cost": training_cost,
        "monthly_savings": monthly_savings,
        "break_even_months": break_even_months
    }

# Export commonly used classes and functions
__all__ = [
    'EnhancedCostCalculator',
    'TrainingApproach',
    'GPUType',
    'GPUConfig',
    'TrainingConfig',
    'CostEstimate',
    'ROIAnalysis',
    'calculate_training_cost',
    'estimate_roi'
]

class CostOptimizer:
    """Advanced cost optimization utilities"""
    
    def __init__(self, calculator: EnhancedCostCalculator):
        self.calculator = calculator
    
    def find_optimal_approach(self, model_name: str, dataset_tokens: int, 
                             constraints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Find the optimal training approach given constraints
        
        Args:
            model_name: Target model name
            dataset_tokens: Dataset size in tokens
            constraints: Optional constraints dict with keys:
                - max_cost: Maximum training cost in USD
                - max_time: Maximum training time in hours
                - local_only: Only consider local training options
                - gpu_available: Available GPU types (list)
                
        Returns:
            Optimization results with recommended approach
        """
        
        constraints = constraints or {}
        
        # Get all cost estimates
        results = self.calculator.calculate_comprehensive_costs(dataset_tokens, model_name)
        estimates = results["cost_estimates"]
        
        # Apply constraints
        filtered_estimates = []
        for estimate in estimates:
            # Check cost constraint
            if "max_cost" in constraints and estimate["total_cost_usd"] > constraints["max_cost"]:
                continue
                
            # Check time constraint
            if "max_time" in constraints and estimate["training_hours"] > constraints["max_time"]:
                continue
                
            # Check local-only constraint
            if constraints.get("local_only", False) and not estimate["approach_name"].lower().startswith("local"):
                continue
                
            # Check GPU availability
            if "gpu_available" in constraints:
                gpu_type = estimate["hardware_requirements"].get("gpu_type", "").lower()
                available_gpus = [gpu.lower() for gpu in constraints["gpu_available"]]
                if gpu_type not in available_gpus and gpu_type != "managed":
                    continue
            
            filtered_estimates.append(estimate)
        
        if not filtered_estimates:
            return {
                "optimal_approach": None,
                "message": "No approaches meet the specified constraints",
                "alternatives": estimates[:3]  # Show top 3 alternatives
            }
        
        # Find optimal approach (lowest cost among constrained options)
        optimal = min(filtered_estimates, key=lambda x: x["total_cost_usd"])
        
        return {
            "optimal_approach": optimal,
            "alternatives": [est for est in filtered_estimates if est != optimal][:2],
            "constraints_applied": constraints,
            "total_approaches_evaluated": len(estimates),
            "approaches_meeting_constraints": len(filtered_estimates)
        }
    
    def compare_gpu_efficiency(self, model_name: str, dataset_tokens: int) -> Dict[str, Any]:
        """Compare efficiency across different GPU types"""
        
        model_info = self.calculator.model_db.get_model_info(model_name)
        if not model_info:
            raise ValueError(f"Model '{model_name}' not found")
        
        gpu_comparisons = []
        
        for gpu_type in [GPUType.RTX_3090, GPUType.RTX_4090, GPUType.A100]:
            try:
                gpu_config = self.calculator.gpu_configs[gpu_type]
                
                # Calculate for local LoRA (most practical approach)
                memory_required = self.calculator._calculate_memory_requirements(
                    model_info, TrainingApproach.LOCAL_LORA
                )
                gpu_count = max(1, math.ceil(memory_required / gpu_config.memory_gb))
                
                training_hours = self.calculator._calculate_training_time(
                    model_info, dataset_tokens, gpu_config, gpu_count, TrainingApproach.LOCAL_LORA
                )
                
                electricity_cost = self.calculator._calculate_electricity_cost(
                    gpu_config, gpu_count, training_hours
                )
                depreciation_cost = self.calculator._calculate_hardware_depreciation(
                    gpu_config, gpu_count, training_hours
                )
                
                total_cost = electricity_cost + depreciation_cost
                
                # Calculate efficiency metrics
                cost_per_hour = total_cost / training_hours
                cost_per_tflop_hour = cost_per_hour / (gpu_config.compute_tflops * gpu_count)
                
                gpu_comparisons.append({
                    "gpu_type": gpu_type.value,
                    "gpu_count": gpu_count,
                    "training_hours": round(training_hours, 2),
                    "total_cost": round(total_cost, 2),
                    "cost_per_hour": round(cost_per_hour, 2),
                    "cost_per_tflop_hour": round(cost_per_tflop_hour, 4),
                    "total_tflops": gpu_config.compute_tflops * gpu_count,
                    "memory_utilization": round(memory_required / (gpu_config.memory_gb * gpu_count), 2)
                })
                
            except Exception as e:
                logging.warning(f"Failed to calculate efficiency for {gpu_type.value}: {e}")
        
        # Sort by cost efficiency (cost per TFLOP-hour)
        gpu_comparisons.sort(key=lambda x: x["cost_per_tflop_hour"])
        
        return {
            "model": model_name,
            "dataset_tokens": dataset_tokens,
            "gpu_efficiency_ranking": gpu_comparisons,
            "most_efficient": gpu_comparisons[0] if gpu_comparisons else None
        }
    
    def estimate_scaling_costs(self, model_name: str, 
                              dataset_sizes: List[int] = None) -> Dict[str, Any]:
        """Estimate how costs scale with dataset size"""
        
        if dataset_sizes is None:
            dataset_sizes = [10000, 50000, 100000, 500000, 1000000]  # 10K to 1M tokens
        
        scaling_data = []
        
        for size in dataset_sizes:
            try:
                results = self.calculator.calculate_comprehensive_costs(size, model_name)
                
                # Get the best (lowest cost) option
                best_estimate = min(results["cost_estimates"], key=lambda x: x["total_cost_usd"])
                
                scaling_data.append({
                    "dataset_tokens": size,
                    "best_approach": best_estimate["approach_name"],
                    "cost_usd": best_estimate["total_cost_usd"],
                    "training_hours": best_estimate["training_hours"],
                    "cost_per_token": best_estimate["total_cost_usd"] / size
                })
                
            except Exception as e:
                logging.warning(f"Failed to calculate scaling for {size} tokens: {e}")
        
        # Calculate scaling efficiency
        if len(scaling_data) >= 2:
            # Linear regression to find cost scaling relationship
            import statistics
            
            log_tokens = [math.log10(d["dataset_tokens"]) for d in scaling_data]
            log_costs = [math.log10(d["cost_usd"]) for d in scaling_data]
            
            # Simple linear regression
            n = len(log_tokens)
            sum_x = sum(log_tokens)
            sum_y = sum(log_costs)
            sum_xy = sum(x * y for x, y in zip(log_tokens, log_costs))
            sum_x2 = sum(x * x for x in log_tokens)
            
            scaling_exponent = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            scaling_interpretation = "unknown"
            if scaling_exponent < 0.8:
                scaling_interpretation = "sublinear (excellent efficiency at scale)"
            elif scaling_exponent < 1.2:
                scaling_interpretation = "linear (proportional scaling)"
            else:
                scaling_interpretation = "superlinear (efficiency decreases at scale)"
        else:
            scaling_exponent = None
            scaling_interpretation = "insufficient data"
        
        return {
            "model": model_name,
            "scaling_data": scaling_data,
            "scaling_exponent": scaling_exponent,
            "scaling_interpretation": scaling_interpretation,
            "cost_per_token_range": {
                "min": min(d["cost_per_token"] for d in scaling_data) if scaling_data else 0,
                "max": max(d["cost_per_token"] for d in scaling_data) if scaling_data else 0
            }
        }

class BenchmarkValidator:
    """Validate cost calculations against known benchmarks"""
    
    def __init__(self, calculator: EnhancedCostCalculator):
        self.calculator = calculator
        self.benchmarks = self._load_validation_benchmarks()
    
    def _load_validation_benchmarks(self) -> Dict[str, Dict[str, Any]]:
        """Load known training cost benchmarks for validation"""
        return {
            "gpt-3.5-turbo": {
                "published_cost": 4_600_000,  # $4.6M
                "parameters": 175_000_000_000,
                "tolerance": 0.5,  # ±50% tolerance
                "source": "Industry estimates"
            },
            "gpt-4": {
                "published_cost": 78_000_000,  # $78M
                "parameters": 1_800_000_000_000,
                "tolerance": 0.6,  # ±60% tolerance (less certain)
                "source": "Industry estimates"
            },
            "llama-2-7b": {
                "published_cost": 2_500_000,  # $2.5M community estimate
                "parameters": 7_000_000_000,
                "tolerance": 0.8,  # ±80% tolerance (highly variable)
                "source": "Community estimates"
            }
        }
    
    def validate_estimates(self) -> Dict[str, Any]:
        """Validate calculator estimates against known benchmarks"""
        
        validation_results = {}
        
        for model_name, benchmark in self.benchmarks.items():
            try:
                # Use Chinchilla-optimal dataset size for validation
                optimal_tokens = self.calculator.model_db.estimate_chinchilla_tokens(
                    benchmark["parameters"]
                )
                
                # Calculate our estimate
                results = self.calculator.calculate_comprehensive_costs(
                    optimal_tokens, model_name
                )
                
                # Find the full training estimate (closest to benchmark scenario)
                full_training_estimates = [
                    est for est in results["cost_estimates"] 
                    if "full" in est["approach_name"].lower() and "cloud" in est["approach_name"].lower()
                ]
                
                if full_training_estimates:
                    our_estimate = full_training_estimates[0]["total_cost_usd"]
                else:
                    # Fallback to highest cost estimate
                    our_estimate = max(results["cost_estimates"], key=lambda x: x["total_cost_usd"])["total_cost_usd"]
                
                # Calculate error
                published_cost = benchmark["published_cost"]
                error_ratio = abs(our_estimate - published_cost) / published_cost
                within_tolerance = error_ratio <= benchmark["tolerance"]
                
                validation_results[model_name] = {
                    "our_estimate": our_estimate,
                    "published_cost": published_cost,
                    "error_ratio": error_ratio,
                    "error_percentage": error_ratio * 100,
                    "within_tolerance": within_tolerance,
                    "tolerance": benchmark["tolerance"] * 100,
                    "status": "PASS" if within_tolerance else "FAIL",
                    "source": benchmark["source"]
                }
                
            except Exception as e:
                validation_results[model_name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        
        # Calculate overall validation score
        passed_validations = sum(1 for r in validation_results.values() 
                               if r.get("status") == "PASS")
        total_validations = len([r for r in validation_results.values() 
                               if r.get("status") in ["PASS", "FAIL"]])
        
        validation_score = passed_validations / total_validations if total_validations > 0 else 0
        
        return {
            "validation_results": validation_results,
            "validation_score": validation_score,
            "passed_validations": passed_validations,
            "total_validations": total_validations,
            "overall_status": "PASS" if validation_score >= 0.7 else "NEEDS_IMPROVEMENT"
        }

class UsageAnalyzer:
    """Analyze usage patterns to provide personalized recommendations"""
    
    def __init__(self, calculator: EnhancedCostCalculator):
        self.calculator = calculator
    
    def analyze_usage_pattern(self, monthly_tokens: int, 
                             use_cases: List[str] = None,
                             budget_range: Tuple[int, int] = None) -> Dict[str, Any]:
        """
        Analyze usage pattern and provide personalized recommendations
        
        Args:
            monthly_tokens: Average monthly token usage
            use_cases: List of use cases (e.g., ['research', 'production', 'experimentation'])
            budget_range: Tuple of (min_budget, max_budget) in USD
            
        Returns:
            Personalized analysis and recommendations
        """
        
        # Categorize usage level
        if monthly_tokens < 10000:
            usage_category = "light"
        elif monthly_tokens < 100000:
            usage_category = "moderate"
        elif monthly_tokens < 1000000:
            usage_category = "heavy"
        else:
            usage_category = "enterprise"
        
        # Estimate API costs for comparison
        api_costs = {
            "gpt-3.5": (monthly_tokens / 1000) * 0.002,
            "gpt-4": (monthly_tokens / 1000) * 0.03,
            "claude": (monthly_tokens / 1000) * 0.008
        }
        
        # Recommend models based on usage pattern
        recommended_models = self._recommend_models_for_usage(
            monthly_tokens, use_cases, budget_range
        )
        
        # Generate training recommendations
        training_recommendations = []
        
        for model_name in recommended_models[:3]:  # Top 3 recommendations
            try:
                # Use monthly tokens as dataset size approximation
                dataset_size = min(monthly_tokens * 3, 1000000)  # 3 months of data, max 1M tokens
                
                results = self.calculator.calculate_comprehensive_costs(
                    dataset_size, model_name, api_usage_monthly=monthly_tokens
                )
                
                best_approach = min(results["cost_estimates"], key=lambda x: x["total_cost_usd"])
                roi_analysis = results["roi_analysis"]
                
                recommendation = {
                    "model": model_name,
                    "training_cost": best_approach["total_cost_usd"],
                    "best_approach": best_approach["approach_name"],
                    "break_even_months": roi_analysis.get("break_even_months"),
                    "annual_savings": roi_analysis.get("projections", {}).get("12_months", 0),
                    "recommendation_score": self._calculate_recommendation_score(
                        best_approach, roi_analysis, usage_category, budget_range
                    )
                }
                
                training_recommendations.append(recommendation)
                
            except Exception as e:
                logging.warning(f"Failed to analyze {model_name}: {e}")
        
        # Sort by recommendation score
        training_recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        # Generate personalized advice
        advice = self._generate_personalized_advice(
            usage_category, monthly_tokens, training_recommendations, api_costs
        )
        
        return {
            "usage_analysis": {
                "monthly_tokens": monthly_tokens,
                "usage_category": usage_category,
                "estimated_api_costs": api_costs,
                "use_cases": use_cases or []
            },
            "training_recommendations": training_recommendations,
            "personalized_advice": advice,
            "budget_assessment": self._assess_budget_fit(training_recommendations, budget_range)
        }
    
    def _recommend_models_for_usage(self, monthly_tokens: int, 
                                   use_cases: List[str] = None,
                                   budget_range: Tuple[int, int] = None) -> List[str]:
        """Recommend models based on usage pattern"""
        
        use_cases = use_cases or []
        
        # Base recommendations by usage level
        if monthly_tokens < 10000:  # Light usage
            candidates = ["llama-2-7b", "mistral-7b", "bert-base-uncased"]
        elif monthly_tokens < 100000:  # Moderate usage
            candidates = ["llama-2-7b", "llama-2-13b", "mistral-7b", "claude-3-haiku"]
        else:  # Heavy usage
            candidates = ["llama-2-13b", "llama-2-70b", "claude-3-sonnet", "gpt-3.5-turbo"]
        
        # Adjust based on use cases
        if "research" in use_cases:
            candidates.extend(["bert-base-uncased", "roberta-base"])
        if "production" in use_cases:
            candidates.extend(["gpt-3.5-turbo", "claude-3-sonnet"])
        if "coding" in use_cases:
            candidates.extend(["llama-2-7b", "mistral-7b"])
        
        # Remove duplicates and return top candidates
        return list(dict.fromkeys(candidates))[:5]
    
    def _calculate_recommendation_score(self, approach: Dict[str, Any], 
                                       roi_analysis: Dict[str, Any],
                                       usage_category: str,
                                       budget_range: Tuple[int, int] = None) -> float:
        """Calculate recommendation score (0-100)"""
        
        score = 50  # Base score
        
        # ROI factor (40% of score)
        break_even = roi_analysis.get("break_even_months", float('inf'))
        if break_even < 3:
            score += 20
        elif break_even < 6:
            score += 15
        elif break_even < 12:
            score += 10
        elif break_even < 24:
            score += 5
        
        # Cost factor (30% of score)
        training_cost = approach["total_cost_usd"]
        if budget_range:
            min_budget, max_budget = budget_range
            if min_budget <= training_cost <= max_budget:
                score += 15
            elif training_cost < min_budget:
                score += 10  # Under budget is good but maybe too simple
            else:
                score -= 20  # Over budget is bad
        else:
            # General cost assessment
            if training_cost < 100:
                score += 15
            elif training_cost < 1000:
                score += 10
            elif training_cost < 5000:
                score += 5
        
        # Complexity factor (20% of score)
        if "local" in approach["approach_name"].lower():
            score += 10  # Local training is more controllable
        if "lora" in approach["approach_name"].lower():
            score += 5   # LoRA is practical
        
        # Usage category alignment (10% of score)
        training_hours = approach.get("training_hours", 0)
        if usage_category == "light" and training_hours < 10:
            score += 5
        elif usage_category == "moderate" and 5 < training_hours < 50:
            score += 5
        elif usage_category in ["heavy", "enterprise"] and training_hours > 10:
            score += 5
        
        return max(0, min(100, score))  # Clamp to 0-100
    
    def _generate_personalized_advice(self, usage_category: str, 
                                     monthly_tokens: int,
                                     recommendations: List[Dict[str, Any]],
                                     api_costs: Dict[str, float]) -> List[str]:
        """Generate personalized advice based on analysis"""
        
        advice = []
        
        # Usage-specific advice
        if usage_category == "light":
            advice.append("For light usage, focus on learning and experimentation with smaller models")
            advice.append("Consider starting with LLaMA 2 7B for cost-effective local training")
        elif usage_category == "moderate":
            advice.append("Your moderate usage makes training economically viable")
            advice.append("LoRA fine-tuning offers excellent cost-performance balance")
        elif usage_category == "heavy":
            advice.append("Heavy usage strongly justifies training your own models")
            advice.append("Consider multiple model sizes for different use cases")
        else:  # enterprise
            advice.append("Enterprise usage requires robust training infrastructure")
            advice.append("Multi-GPU setups and cloud training become cost-effective")
        
        # ROI-specific advice
        if recommendations:
            best_rec = recommendations[0]
            break_even = best_rec.get("break_even_months")
            
            if break_even and break_even < 6:
                advice.append(f"Training pays for itself in {break_even:.1f} months - excellent ROI")
            elif break_even and break_even < 12:
                advice.append(f"Training breaks even in {break_even:.1f} months - good long-term value")
            else:
                advice.append("Training ROI is marginal - consider increasing usage or API efficiency")
        
        # Cost comparison advice
        lowest_api_cost = min(api_costs.values())
        if recommendations and recommendations[0]["training_cost"] < lowest_api_cost * 6:
            advice.append("Training cost is less than 6 months of API usage - highly recommended")
        
        return advice[:5]  # Limit to top 5 pieces of advice
    
    def _assess_budget_fit(self, recommendations: List[Dict[str, Any]], 
                          budget_range: Tuple[int, int] = None) -> Dict[str, Any]:
        """Assess how recommendations fit within budget constraints"""
        
        if not budget_range or not recommendations:
            return {"status": "no_constraints", "message": "No budget constraints specified"}
        
        min_budget, max_budget = budget_range
        
        within_budget = [r for r in recommendations if min_budget <= r["training_cost"] <= max_budget]
        under_budget = [r for r in recommendations if r["training_cost"] < min_budget]
        over_budget = [r for r in recommendations if r["training_cost"] > max_budget]
        
        if within_budget:
            status = "good_fit"
            message = f"{len(within_budget)} recommendations fit within your ${min_budget}-${max_budget} budget"
        elif under_budget:
            status = "under_budget"
            message = f"All recommendations are under budget - consider more ambitious projects"
        else:
            status = "over_budget"
            message = f"All recommendations exceed budget - consider smaller models or LoRA training"
        
        return {
            "status": status,
            "message": message,
            "within_budget_count": len(within_budget),
            "under_budget_count": len(under_budget),
            "over_budget_count": len(over_budget),
            "budget_range": budget_range
        }