# core/cost_calculator_integration.py
"""
Integration layer for Enhanced Cost Calculator with ROI and Optimization
This file provides the unified interface that the controller will use
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

# Import the main components
from .cost_calculator import EnhancedCostCalculator, TrainingApproach, GPUType
from .pricing_engine import DynamicPricingEngine, PricingData
from .roi_calculator import ROICalculator, CostOptimizer, UsagePattern, TimeHorizon
from .model_database import get_model_database, ModelInfo

@dataclass
class ComprehensiveCostAnalysis:
    """Complete cost analysis result with all components"""
    model_info: Dict[str, Any]
    dataset_info: Dict[str, Any]
    cost_estimates: List[Dict[str, Any]]
    roi_analysis: Dict[str, Any]
    optimization_recommendations: List[Dict[str, Any]]
    pricing_context: Dict[str, Any]
    efficiency_analysis: Dict[str, Any]
    calculation_metadata: Dict[str, Any]

class ComprehensiveCostAnalyzer:
    """
    Unified interface for complete cost analysis combining all components
    """
    
    def __init__(self):
        self.cost_calculator = EnhancedCostCalculator()
        self.pricing_engine = DynamicPricingEngine()
        self.roi_calculator = ROICalculator(self.pricing_engine)
        self.cost_optimizer = CostOptimizer(self.roi_calculator)
        self.model_db = get_model_database()
        logging.info("Comprehensive Cost Analyzer initialized")
    
    def analyze_comprehensive_costs(self,
                                  dataset_tokens: int,
                                  target_model: str = "llama-2-7b",
                                  monthly_api_usage: int = 100000,
                                  user_constraints: Optional[Dict[str, Any]] = None,
                                  usage_pattern: UsagePattern = UsagePattern.MODERATE) -> ComprehensiveCostAnalysis:
        """
        Perform comprehensive cost analysis with ROI and optimization
        
        Args:
            dataset_tokens: Training dataset size in tokens
            target_model: Target model name
            monthly_api_usage: Monthly API usage for ROI calculation
            user_constraints: User constraints (budget, time, quality)
            usage_pattern: User's usage pattern category
            
        Returns:
            Complete cost analysis with all insights
        """
        
        user_constraints = user_constraints or {}
        
        # Step 1: Get basic cost estimates from enhanced calculator
        basic_analysis = self.cost_calculator.calculate_comprehensive_costs(
            dataset_tokens=dataset_tokens,
            target_model=target_model,
            api_usage_monthly=monthly_api_usage
        )
        
        # Convert cost estimates to CostEstimate objects for ROI analysis
        cost_estimates = []
        for est_dict in basic_analysis["cost_estimates"]:
            cost_estimate = self._dict_to_cost_estimate(est_dict)
            cost_estimates.append(cost_estimate)
        
        # Step 2: Enhanced ROI analysis
        roi_analysis = self.roi_calculator.analyze_roi_comprehensive(
            cost_estimates=cost_estimates,
            monthly_token_usage=monthly_api_usage,
            usage_pattern=usage_pattern,
            target_model=target_model,
            time_horizon=user_constraints.get('time_horizon', TimeHorizon.MEDIUM_TERM)
        )
        
        # Step 3: Generate optimization recommendations
        optimization_recommendations = self.cost_optimizer.generate_optimization_recommendations(
            cost_estimates=cost_estimates,
            user_constraints=user_constraints
        )
        
        # Step 4: Efficiency analysis
        efficiency_analysis = self.cost_optimizer.analyze_cost_efficiency(cost_estimates)
        
        # Step 5: Get current pricing context
        pricing_context = self._get_pricing_context(target_model)
        
        # Step 6: Combine everything into comprehensive analysis
        return ComprehensiveCostAnalysis(
            model_info=basic_analysis["model_info"],
            dataset_info=basic_analysis["dataset_info"],
            cost_estimates=basic_analysis["cost_estimates"],
            roi_analysis=roi_analysis,
            optimization_recommendations=[self._optimization_rec_to_dict(rec) for rec in optimization_recommendations],
            pricing_context=pricing_context,
            efficiency_analysis=efficiency_analysis,
            calculation_metadata={
                **basic_analysis["calculation_metadata"],
                "usage_pattern": usage_pattern.value,
                "user_constraints": user_constraints,
                "analysis_type": "comprehensive"
            }
        )
    
    def quick_cost_estimate(self,
                           dataset_tokens: int,
                           target_model: str = "llama-2-7b",
                           approach: Optional[str] = None) -> Dict[str, Any]:
        """
        Quick cost estimate for simple use cases
        
        Args:
            dataset_tokens: Training dataset size in tokens
            target_model: Target model name
            approach: Specific approach to estimate (optional)
            
        Returns:
            Simplified cost estimate
        """
        
        try:
            # Get basic cost analysis
            basic_analysis = self.cost_calculator.calculate_comprehensive_costs(
                dataset_tokens=dataset_tokens,
                target_model=target_model
            )
            
            cost_estimates = basic_analysis["cost_estimates"]
            
            if approach:
                # Filter to specific approach
                filtered_estimates = [
                    est for est in cost_estimates 
                    if approach.lower() in est["approach_name"].lower()
                ]
                if filtered_estimates:
                    cost_estimates = filtered_estimates
            
            # Get best (lowest cost) estimate
            best_estimate = min(cost_estimates, key=lambda x: x["total_cost_usd"])
            
            # Quick ROI calculation with default usage
            monthly_usage = 50000  # Default moderate usage
            api_costs = self.roi_calculator._calculate_api_costs(target_model, monthly_usage)
            break_even_months = (
                best_estimate["total_cost_usd"] / api_costs["monthly_savings_potential"] 
                if api_costs["monthly_savings_potential"] > 0 else float('inf')
            )
            
            return {
                "model": target_model,
                "dataset_tokens": dataset_tokens,
                "best_approach": best_estimate["approach_name"],
                "training_cost": best_estimate["total_cost_usd"],
                "training_hours": best_estimate["training_hours"],
                "break_even_months": round(break_even_months, 1) if break_even_months != float('inf') else None,
                "monthly_api_savings": api_costs["monthly_savings_potential"],
                "confidence": best_estimate["confidence"],
                "quick_recommendation": self._generate_quick_recommendation(
                    best_estimate, break_even_months
                )
            }
            
        except Exception as e:
            logging.error(f"Quick cost estimate failed: {e}")
            return {
                "error": str(e),
                "model": target_model,
                "dataset_tokens": dataset_tokens
            }
    
    def compare_training_approaches(self,
                                  dataset_tokens: int,
                                  target_model: str = "llama-2-7b",
                                  approaches: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Compare specific training approaches side-by-side
        
        Args:
            dataset_tokens: Training dataset size in tokens
            target_model: Target model name
            approaches: List of approaches to compare
            
        Returns:
            Side-by-side comparison of approaches
        """
        
        # Get comprehensive analysis
        analysis = self.cost_calculator.calculate_comprehensive_costs(
            dataset_tokens=dataset_tokens,
            target_model=target_model
        )
        
        cost_estimates = analysis["cost_estimates"]
        
        # Filter to requested approaches if specified
        if approaches:
            filtered_estimates = []
            for approach in approaches:
                matching = [
                    est for est in cost_estimates 
                    if approach.lower() in est["approach_name"].lower()
                ]
                filtered_estimates.extend(matching)
            cost_estimates = filtered_estimates
        
        if not cost_estimates:
            return {"error": "No matching approaches found"}
        
        # Sort by cost for comparison
        cost_estimates.sort(key=lambda x: x["total_cost_usd"])
        
        # Calculate comparison metrics
        cheapest = cost_estimates[0]
        fastest = min(cost_estimates, key=lambda x: x["training_hours"])
        
        comparisons = []
        for estimate in cost_estimates:
            cost_vs_cheapest = estimate["total_cost_usd"] - cheapest["total_cost_usd"]
            time_vs_fastest = estimate["training_hours"] - fastest["training_hours"]
            
            comparisons.append({
                **estimate,
                "cost_vs_cheapest": round(cost_vs_cheapest, 2),
                "cost_vs_cheapest_pct": round((cost_vs_cheapest / cheapest["total_cost_usd"]) * 100, 1),
                "time_vs_fastest": round(time_vs_fastest, 1),
                "time_vs_fastest_pct": round((time_vs_fastest / fastest["training_hours"]) * 100, 1) if fastest["training_hours"] > 0 else 0,
                "value_score": self._calculate_value_score(estimate, cheapest, fastest)
            })
        
        return {
            "model": target_model,
            "dataset_tokens": dataset_tokens,
            "approaches_compared": len(comparisons),
            "cheapest_approach": cheapest["approach_name"],
            "fastest_approach": fastest["approach_name"],
            "comparison_table": comparisons,
            "summary": {
                "cost_range": {
                    "min": cheapest["total_cost_usd"],
                    "max": max(est["total_cost_usd"] for est in cost_estimates)
                },
                "time_range": {
                    "min": fastest["training_hours"],
                    "max": max(est["training_hours"] for est in cost_estimates)
                }
            }
        }
    
    def get_optimization_suggestions(self,
                                   dataset_tokens: int,
                                   target_model: str = "llama-2-7b",
                                   current_approach: Optional[str] = None,
                                   constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get specific optimization suggestions for a use case
        
        Args:
            dataset_tokens: Training dataset size in tokens
            target_model: Target model name
            current_approach: Current training approach (if any)
            constraints: User constraints and preferences
            
        Returns:
            Targeted optimization suggestions
        """
        
        constraints = constraints or {}
        
        # Get cost estimates
        analysis = self.cost_calculator.calculate_comprehensive_costs(
            dataset_tokens=dataset_tokens,
            target_model=target_model
        )
        
        # Convert to CostEstimate objects
        cost_estimates = [
            self._dict_to_cost_estimate(est_dict) 
            for est_dict in analysis["cost_estimates"]
        ]
        
        # Generate optimization recommendations
        recommendations = self.cost_optimizer.generate_optimization_recommendations(
            cost_estimates=cost_estimates,
            user_constraints=constraints
        )
        
        # Filter recommendations based on current approach
        if current_approach:
            # Add specific recommendations for improving current approach
            current_specific = self._get_current_approach_optimizations(
                current_approach, cost_estimates, constraints
            )
            recommendations.extend(current_specific)
        
        # Get efficiency analysis
        efficiency = self.cost_optimizer.analyze_cost_efficiency(cost_estimates)
        
        return {
            "target_model": target_model,
            "dataset_tokens": dataset_tokens,
            "current_approach": current_approach,
            "optimization_recommendations": [
                self._optimization_rec_to_dict(rec) for rec in recommendations
            ],
            "efficiency_analysis": efficiency,
            "quick_wins": self._identify_quick_wins(recommendations),
            "major_optimizations": self._identify_major_optimizations(recommendations),
            "constraints_applied": constraints
        }
    
    def estimate_scaling_costs(self,
                             target_model: str = "llama-2-7b",
                             dataset_sizes: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Estimate how costs scale with dataset size
        
        Args:
            target_model: Target model name
            dataset_sizes: List of dataset sizes to analyze
            
        Returns:
            Scaling analysis across dataset sizes
        """
        
        if dataset_sizes is None:
            dataset_sizes = [10000, 50000, 100000, 500000, 1000000]
        
        scaling_results = []
        
        for size in dataset_sizes:
            try:
                quick_estimate = self.quick_cost_estimate(size, target_model)
                scaling_results.append({
                    "dataset_tokens": size,
                    "training_cost": quick_estimate.get("training_cost", 0),
                    "training_hours": quick_estimate.get("training_hours", 0),
                    "best_approach": quick_estimate.get("best_approach", "unknown"),
                    "cost_per_token": quick_estimate.get("training_cost", 0) / size if size > 0 else 0
                })
            except Exception as e:
                logging.warning(f"Failed to calculate scaling for {size} tokens: {e}")
        
        if not scaling_results:
            return {"error": "No scaling data available"}
        
        # Calculate scaling metrics
        scaling_analysis = self._analyze_scaling_patterns(scaling_results)
        
        return {
            "model": target_model,
            "dataset_sizes_analyzed": len(scaling_results),
            "scaling_data": scaling_results,
            "scaling_analysis": scaling_analysis,
            "cost_efficiency_trends": self._calculate_efficiency_trends(scaling_results),
            "recommendations": self._generate_scaling_recommendations(scaling_analysis)
        }
    
    def get_provider_comparison(self,
                              dataset_tokens: int,
                              target_model: str = "llama-2-7b",
                              gpu_type: GPUType = GPUType.RTX_4090) -> Dict[str, Any]:
        """
        Compare costs across different cloud providers
        
        Args:
            dataset_tokens: Training dataset size in tokens
            target_model: Target model name
            gpu_type: GPU type for comparison
            
        Returns:
            Provider cost comparison
        """
        
        # Get current pricing from all providers
        provider_rates = self.pricing_engine.get_current_rates(gpu_type)
        
        # Get model info for calculations
        model_info = self.model_db.get_model_info(target_model)
        if not model_info:
            return {"error": f"Model {target_model} not found"}
        
        provider_comparisons = []
        
        for provider, pricing_data in provider_rates.items():
            try:
                # Estimate training cost for this provider
                cost_estimate = self.pricing_engine.estimate_cloud_training_cost(
                    model_params=model_info.parameters,
                    dataset_tokens=dataset_tokens,
                    provider=provider,
                    gpu_type=gpu_type
                )
                
                provider_comparisons.append({
                    "provider": provider,
                    "hourly_rate": pricing_data.hourly_rate,
                    "total_cost": cost_estimate["total_cost"],
                    "training_hours": cost_estimate["training_hours"],
                    "confidence": cost_estimate["confidence"],
                    "spot_pricing": getattr(pricing_data, 'spot_price', False),
                    "availability": getattr(pricing_data, 'availability', 'unknown')
                })
                
            except Exception as e:
                logging.warning(f"Failed to estimate cost for {provider}: {e}")
        
        if not provider_comparisons:
            return {"error": "No provider pricing available"}
        
        # Sort by total cost
        provider_comparisons.sort(key=lambda x: x["total_cost"])
        
        # Calculate savings opportunities
        cheapest = provider_comparisons[0]
        most_expensive = provider_comparisons[-1]
        max_savings = most_expensive["total_cost"] - cheapest["total_cost"]
        
        return {
            "model": target_model,
            "dataset_tokens": dataset_tokens,
            "gpu_type": gpu_type.value,
            "providers_compared": len(provider_comparisons),
            "provider_comparison": provider_comparisons,
            "best_provider": cheapest["provider"],
            "max_savings": round(max_savings, 2),
            "savings_percentage": round((max_savings / most_expensive["total_cost"]) * 100, 1) if most_expensive["total_cost"] > 0 else 0,
            "pricing_timestamp": provider_rates[list(provider_rates.keys())[0]].timestamp if provider_rates else None
        }
    
    # Helper methods
    def _dict_to_cost_estimate(self, est_dict: Dict[str, Any]):
        """Convert dictionary to CostEstimate object"""
        from .cost_calculator import CostEstimate
        
        return CostEstimate(
            approach_name=est_dict["approach_name"],
            total_cost_usd=est_dict["total_cost_usd"],
            training_hours=est_dict["training_hours"],
            gpu_hours=est_dict["gpu_hours"],
            cost_breakdown=est_dict["cost_breakdown"],
            confidence=est_dict["confidence"],
            notes=est_dict["notes"],
            hardware_requirements=est_dict["hardware_requirements"]
        )
    
    def _optimization_rec_to_dict(self, rec) -> Dict[str, Any]:
        """Convert OptimizationRecommendation to dictionary"""
        return {
            "category": rec.category,
            "title": rec.title,
            "description": rec.description,
            "impact": rec.impact,
            "effort": rec.effort,
            "estimated_savings": rec.estimated_savings,
            "estimated_time_savings": rec.estimated_time_savings,
            "confidence": rec.confidence
        }
    
    def _get_pricing_context(self, target_model: str) -> Dict[str, Any]:
        """Get current pricing context and market conditions"""
        
        try:
            # Get provider status
            provider_status = self.pricing_engine.get_provider_status()
            
            # Get sample pricing for popular GPU types
            gpu_pricing_samples = {}
            for gpu_type in [GPUType.RTX_4090, GPUType.A100]:
                try:
                    rates = self.pricing_engine.get_current_rates(gpu_type)
                    if rates:
                        avg_rate = sum(data.hourly_rate for data in rates.values()) / len(rates)
                        gpu_pricing_samples[gpu_type.value] = {
                            "average_hourly_rate": round(avg_rate, 3),
                            "providers_available": len(rates),
                            "rate_range": {
                                "min": round(min(data.hourly_rate for data in rates.values()), 3),
                                "max": round(max(data.hourly_rate for data in rates.values()), 3)
                            }
                        }
                except Exception as e:
                    logging.warning(f"Failed to get pricing for {gpu_type.value}: {e}")
            
            return {
                "provider_status": provider_status,
                "gpu_pricing_samples": gpu_pricing_samples,
                "market_conditions": self._assess_market_conditions(provider_status),
                "pricing_reliability": self._assess_pricing_reliability(provider_status)
            }
            
        except Exception as e:
            logging.error(f"Failed to get pricing context: {e}")
            return {
                "error": "Pricing context unavailable",
                "fallback_mode": True
            }
    
    def _assess_market_conditions(self, provider_status: Dict[str, Any]) -> str:
        """Assess current market conditions based on provider status"""
        
        providers = provider_status.get("providers", {})
        active_providers = sum(1 for p in providers.values() if p.get("status") == "active")
        total_providers = len(providers)
        
        if active_providers / total_providers > 0.8:
            return "Good - Most providers accessible"
        elif active_providers / total_providers > 0.5:
            return "Moderate - Some provider issues"
        else:
            return "Poor - Limited provider access"
    
    def _assess_pricing_reliability(self, provider_status: Dict[str, Any]) -> float:
        """Assess pricing reliability score (0-1)"""
        
        providers = provider_status.get("providers", {})
        if not providers:
            return 0.0
        
        reliability_scores = []
        for provider_info in providers.values():
            if provider_info.get("status") == "active":
                if provider_info.get("last_success"):
                    reliability_scores.append(0.9)
                else:
                    reliability_scores.append(0.7)
            else:
                reliability_scores.append(0.3)
        
        return sum(reliability_scores) / len(reliability_scores)
    
    def _generate_quick_recommendation(self, best_estimate: Dict[str, Any], break_even_months: float) -> str:
        """Generate a quick recommendation summary"""
        
        approach = best_estimate["approach_name"]
        cost = best_estimate["total_cost_usd"]
        
        if break_even_months <= 3:
            return f"Excellent ROI: {approach} (${cost:.2f}) pays for itself in {break_even_months:.1f} months"
        elif break_even_months <= 6:
            return f"Good investment: {approach} (${cost:.2f}) breaks even in {break_even_months:.1f} months"
        elif break_even_months <= 12:
            return f"Moderate ROI: {approach} (${cost:.2f}) takes {break_even_months:.1f} months to break even"
        else:
            return f"Poor ROI: {approach} (${cost:.2f}) may not be cost-effective at current usage levels"
    
    def _calculate_value_score(self, estimate: Dict[str, Any], cheapest: Dict[str, Any], fastest: Dict[str, Any]) -> float:
        """Calculate value score combining cost and time efficiency"""
        
        # Normalize cost and time (0-1 scale, where 1 is best)
        cost_efficiency = cheapest["total_cost_usd"] / estimate["total_cost_usd"]
        time_efficiency = fastest["training_hours"] / estimate["training_hours"] if estimate["training_hours"] > 0 else 0
        
        # Weight cost more heavily than time (70/30 split)
        value_score = (cost_efficiency * 0.7) + (time_efficiency * 0.3)
        
        return round(value_score, 3)
    
    def _get_current_approach_optimizations(self, current_approach: str, cost_estimates: List, constraints: Dict[str, Any]) -> List:
        """Get specific optimizations for the current approach"""
        
        # This would return approach-specific optimizations
        # For now, return empty list as this is approach-specific logic
        return []
    
    def _identify_quick_wins(self, recommendations: List) -> List[Dict[str, Any]]:
        """Identify quick win optimizations (high impact, low effort)"""
        
        quick_wins = []
        for rec in recommendations:
            rec_dict = self._optimization_rec_to_dict(rec) if hasattr(rec, 'category') else rec
            if rec_dict.get("impact") == "High" and rec_dict.get("effort") == "Low":
                quick_wins.append(rec_dict)
        
        return quick_wins[:3]  # Top 3 quick wins
    
    def _identify_major_optimizations(self, recommendations: List) -> List[Dict[str, Any]]:
        """Identify major optimizations (high impact, any effort)"""
        
        major_opts = []
        for rec in recommendations:
            rec_dict = self._optimization_rec_to_dict(rec) if hasattr(rec, 'category') else rec
            if rec_dict.get("impact") == "High":
                major_opts.append(rec_dict)
        
        return major_opts[:5]  # Top 5 major optimizations
    
    def _analyze_scaling_patterns(self, scaling_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in scaling data"""
        
        if len(scaling_results) < 2:
            return {"error": "Insufficient data for scaling analysis"}
        
        # Calculate scaling efficiency
        cost_per_tokens = [r["cost_per_token"] for r in scaling_results]
        
        # Check if cost per token decreases with scale (economy of scale)
        has_economy_of_scale = cost_per_tokens[0] > cost_per_tokens[-1]
        
        # Calculate scaling factor (linear, sublinear, superlinear)
        import math
        
        log_sizes = [math.log10(r["dataset_tokens"]) for r in scaling_results]
        log_costs = [math.log10(r["training_cost"]) for r in scaling_results if r["training_cost"] > 0]
        
        if len(log_sizes) == len(log_costs) and len(log_costs) > 1:
            # Simple linear regression to find scaling exponent
            n = len(log_sizes)
            sum_x = sum(log_sizes)
            sum_y = sum(log_costs)
            sum_xy = sum(x * y for x, y in zip(log_sizes, log_costs))
            sum_x2 = sum(x * x for x in log_sizes)
            
            scaling_exponent = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        else:
            scaling_exponent = 1.0  # Linear fallback
        
        scaling_type = (
            "sublinear" if scaling_exponent < 0.9 else
            "linear" if scaling_exponent < 1.1 else
            "superlinear"
        )
        
        return {
            "has_economy_of_scale": has_economy_of_scale,
            "scaling_exponent": round(scaling_exponent, 2),
            "scaling_type": scaling_type,
            "cost_per_token_trend": "decreasing" if cost_per_tokens[0] > cost_per_tokens[-1] else "increasing",
            "optimal_dataset_size": self._find_optimal_dataset_size(scaling_results)
        }
    
    def _find_optimal_dataset_size(self, scaling_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find optimal dataset size based on cost efficiency"""
        
        # Find the size with best cost per token
        best_efficiency = min(scaling_results, key=lambda x: x["cost_per_token"])
        
        return {
            "dataset_tokens": best_efficiency["dataset_tokens"],
            "cost_per_token": best_efficiency["cost_per_token"],
            "total_cost": best_efficiency["training_cost"],
            "rationale": "Best cost per token efficiency"
        }
    
    def _calculate_efficiency_trends(self, scaling_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate efficiency trends across scaling"""
        
        if len(scaling_results) < 2:
            return {}
        
        # Calculate percentage improvements
        first_result = scaling_results[0]
        last_result = scaling_results[-1]
        
        cost_per_token_change = (
            (last_result["cost_per_token"] - first_result["cost_per_token"]) / 
            first_result["cost_per_token"] * 100
        ) if first_result["cost_per_token"] > 0 else 0
        
        return {
            "cost_per_token_change_pct": round(cost_per_token_change, 1),
            "trend_direction": "improving" if cost_per_token_change < 0 else "worsening",
            "scale_factor": round(last_result["dataset_tokens"] / first_result["dataset_tokens"], 1),
            "efficiency_gain": "Yes" if cost_per_token_change < -10 else "No"
        }
    
    def _generate_scaling_recommendations(self, scaling_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on scaling analysis"""
        
        recommendations = []
        
        if scaling_analysis.get("has_economy_of_scale"):
            recommendations.append("Larger datasets show better cost efficiency - consider scaling up")
        
        scaling_type = scaling_analysis.get("scaling_type")
        if scaling_type == "sublinear":
            recommendations.append("Excellent scaling efficiency - costs grow slower than dataset size")
        elif scaling_type == "superlinear":
            recommendations.append("Poor scaling efficiency - costs grow faster than dataset size")
        
        optimal_size = scaling_analysis.get("optimal_dataset_size", {})
        if optimal_size:
            recommendations.append(
                f"Optimal dataset size appears to be around {optimal_size['dataset_tokens']:,} tokens"
            )
        
        return recommendations


# Convenience functions for easy integration
def analyze_training_costs(dataset_tokens: int, model_name: str = "llama-2-7b", 
                          monthly_usage: int = 100000) -> Dict[str, Any]:
    """Convenience function for quick cost analysis"""
    analyzer = ComprehensiveCostAnalyzer()
    analysis = analyzer.analyze_comprehensive_costs(
        dataset_tokens=dataset_tokens,
        target_model=model_name,
        monthly_api_usage=monthly_usage
    )
    
    # Convert to dictionary for easy use
    return {
        "model_info": analysis.model_info,
        "dataset_info": analysis.dataset_info,
        "cost_estimates": analysis.cost_estimates,
        "roi_analysis": analysis.roi_analysis,
        "optimization_recommendations": analysis.optimization_recommendations,
        "efficiency_analysis": analysis.efficiency_analysis
    }


def get_quick_estimate(dataset_tokens: int, model_name: str = "llama-2-7b") -> Dict[str, Any]:
    """Quick estimate for simple use cases"""
    analyzer = ComprehensiveCostAnalyzer()
    return analyzer.quick_cost_estimate(dataset_tokens, model_name)


# Export main classes and functions
__all__ = [
    'ComprehensiveCostAnalyzer',
    'ComprehensiveCostAnalysis',
    'analyze_training_costs',
    'get_quick_estimate'
]