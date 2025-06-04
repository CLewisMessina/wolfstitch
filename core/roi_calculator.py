# core/roi_calculator.py
"""
Advanced ROI Calculator and Cost Optimization Engine
Provides sophisticated ROI analysis and cost optimization recommendations
"""

import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import statistics

from .cost_calculator import CostEstimate, TrainingApproach, GPUType
from .pricing_engine import DynamicPricingEngine, PricingData

class UsagePattern(Enum):
    LIGHT = "light"           # <10K tokens/month
    MODERATE = "moderate"     # 10K-100K tokens/month  
    HEAVY = "heavy"          # 100K-1M tokens/month
    ENTERPRISE = "enterprise" # >1M tokens/month

class TimeHorizon(Enum):
    SHORT_TERM = "short_term"     # 3-6 months
    MEDIUM_TERM = "medium_term"   # 6-18 months
    LONG_TERM = "long_term"       # 18+ months

@dataclass
class ROIScenario:
    name: str
    training_cost: float
    monthly_api_cost_current: float
    monthly_api_cost_after_training: float
    monthly_savings: float
    break_even_months: float
    total_savings_12_months: float
    total_savings_24_months: float
    confidence: float
    assumptions: List[str]

@dataclass
class OptimizationRecommendation:
    category: str  # cost_reduction, speed_optimization, quality_improvement, etc.
    title: str
    description: str
    impact: str  # Low, Medium, High
    effort: str  # Low, Medium, High
    estimated_savings: Optional[float] = None
    estimated_time_savings: Optional[float] = None
    confidence: float = 0.8

class ROICalculator:
    """Advanced ROI analysis for AI training investments"""
    
    def __init__(self, pricing_engine: Optional[DynamicPricingEngine] = None):
        self.pricing_engine = pricing_engine or DynamicPricingEngine()
        self.api_pricing = self._initialize_api_pricing()
        logging.info("ROI Calculator initialized")
    
    def _initialize_api_pricing(self) -> Dict[str, Dict[str, float]]:
        """Initialize API pricing for different models and providers"""
        return {
            # OpenAI API pricing (USD per 1K tokens)
            'openai': {
                'gpt-4': {'input': 0.03, 'output': 0.06},
                'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
                'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002}
            },
            # Anthropic API pricing
            'anthropic': {
                'claude-3-opus': {'input': 0.015, 'output': 0.075},
                'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
                'claude-3-haiku': {'input': 0.00025, 'output': 0.00125}
            },
            # Other providers
            'together': {
                'llama-2-7b': {'input': 0.0008, 'output': 0.0008},
                'llama-2-13b': {'input': 0.0022, 'output': 0.0022},
                'mistral-7b': {'input': 0.0008, 'output': 0.0008}
            }
        }
    
    def analyze_roi_comprehensive(self, 
                                cost_estimates: List[CostEstimate],
                                monthly_token_usage: int,
                                usage_pattern: UsagePattern = UsagePattern.MODERATE,
                                target_model: str = "llama-2-7b",
                                time_horizon: TimeHorizon = TimeHorizon.MEDIUM_TERM) -> Dict[str, Any]:
        """
        Comprehensive ROI analysis with multiple scenarios
        
        Args:
            cost_estimates: List of training cost estimates
            monthly_token_usage: Expected monthly token usage
            usage_pattern: User's usage pattern category
            target_model: Target model for comparison
            time_horizon: Analysis time horizon
            
        Returns:
            Comprehensive ROI analysis
        """
        
        if not cost_estimates:
            raise ValueError("No cost estimates provided for ROI analysis")
        
        # Sort cost estimates by total cost
        sorted_estimates = sorted(cost_estimates, key=lambda x: x.total_cost_usd)
        best_estimate = sorted_estimates[0]
        
        # Calculate API costs for comparison
        api_costs = self._calculate_api_costs(target_model, monthly_token_usage)
        
        # Generate multiple ROI scenarios
        scenarios = self._generate_roi_scenarios(
            cost_estimates, api_costs, monthly_token_usage, usage_pattern
        )
        
        # Calculate break-even analysis
        break_even_analysis = self._calculate_break_even_analysis(
            best_estimate, api_costs, monthly_token_usage
        )
        
        # Generate time-based projections
        projections = self._generate_time_projections(
            best_estimate.total_cost_usd, 
            api_costs['monthly_savings_potential'],
            time_horizon
        )
        
        # Risk analysis
        risk_analysis = self._analyze_risks(
            best_estimate, usage_pattern, monthly_token_usage
        )
        
        # Sensitivity analysis
        sensitivity = self._perform_sensitivity_analysis(
            best_estimate, api_costs, monthly_token_usage
        )
        
        return {
            'summary': {
                'best_approach': best_estimate.approach_name,
                'training_investment': best_estimate.total_cost_usd,
                'monthly_savings_potential': api_costs['monthly_savings_potential'],
                'break_even_months': break_even_analysis['months_to_break_even'],
                'roi_12_months': projections['roi_12_months'],
                'confidence_score': min(best_estimate.confidence, 0.9)
            },
            'scenarios': [self._scenario_to_dict(s) for s in scenarios],
            'break_even_analysis': break_even_analysis,
            'time_projections': projections,
            'risk_analysis': risk_analysis,
            'sensitivity_analysis': sensitivity,
            'recommendations': self._generate_roi_recommendations(
                best_estimate, usage_pattern, break_even_analysis
            ),
            'api_cost_comparison': api_costs,
            'usage_pattern_analysis': self._analyze_usage_pattern(
                usage_pattern, monthly_token_usage
            )
        }
    
    def _calculate_api_costs(self, target_model: str, monthly_tokens: int) -> Dict[str, Any]:
        """Calculate API costs for comparison models"""
        
        # Determine API pricing based on model
        model_lower = target_model.lower()
        
        if 'gpt-4' in model_lower and 'turbo' not in model_lower:
            api_family = 'openai'
            api_model = 'gpt-4'
        elif 'gpt-4-turbo' in model_lower:
            api_family = 'openai'
            api_model = 'gpt-4-turbo'
        elif 'gpt-3.5' in model_lower:
            api_family = 'openai'
            api_model = 'gpt-3.5-turbo'
        elif 'claude-3-opus' in model_lower:
            api_family = 'anthropic'
            api_model = 'claude-3-opus'
        elif 'claude-3-sonnet' in model_lower:
            api_family = 'anthropic'
            api_model = 'claude-3-sonnet'
        elif 'claude-3-haiku' in model_lower:
            api_family = 'anthropic'
            api_model = 'claude-3-haiku'
        elif 'llama-2-7b' in model_lower:
            api_family = 'together'
            api_model = 'llama-2-7b'
        elif 'llama-2-13b' in model_lower:
            api_family = 'together'
            api_model = 'llama-2-13b'
        elif 'mistral-7b' in model_lower:
            api_family = 'together'
            api_model = 'mistral-7b'
        else:
            # Default to GPT-3.5 pricing
            api_family = 'openai'
            api_model = 'gpt-3.5-turbo'
        
        pricing = self.api_pricing[api_family][api_model]
        
        # Assume 50/50 input/output token split
        input_tokens = monthly_tokens * 0.5
        output_tokens = monthly_tokens * 0.5
        
        monthly_cost = (
            (input_tokens / 1000) * pricing['input'] +
            (output_tokens / 1000) * pricing['output']
        )
        
        # Calculate potential savings (assume 90% reduction after training)
        monthly_savings_potential = monthly_cost * 0.9
        
        return {
            'api_family': api_family,
            'api_model': api_model,
            'monthly_tokens': monthly_tokens,
            'monthly_cost': monthly_cost,
            'monthly_savings_potential': monthly_savings_potential,
            'input_cost_per_1k': pricing['input'],
            'output_cost_per_1k': pricing['output'],
            'assumptions': [
                '50/50 input/output token split',
                '90% cost reduction after training',
                f'Based on {api_family} {api_model} pricing'
            ]
        }
    
    def _generate_roi_scenarios(self, 
                               cost_estimates: List[CostEstimate],
                               api_costs: Dict[str, Any],
                               monthly_tokens: int,
                               usage_pattern: UsagePattern) -> List[ROIScenario]:
        """Generate multiple ROI scenarios for comparison"""
        
        scenarios = []
        monthly_api_cost = api_costs['monthly_cost']
        monthly_savings = api_costs['monthly_savings_potential']
        
        # Scenario 1: Best cost approach
        best_estimate = min(cost_estimates, key=lambda x: x.total_cost_usd)
        scenarios.append(self._create_roi_scenario(
            "Best Cost Option",
            best_estimate,
            monthly_api_cost,
            monthly_savings,
            usage_pattern
        ))
        
        # Scenario 2: Fastest training approach
        fastest_estimate = min(cost_estimates, key=lambda x: x.training_hours)
        if fastest_estimate != best_estimate:
            scenarios.append(self._create_roi_scenario(
                "Fastest Training",
                fastest_estimate,
                monthly_api_cost,
                monthly_savings,
                usage_pattern
            ))
        
        # Scenario 3: Local training (if available)
        local_estimates = [e for e in cost_estimates if "local" in e.approach_name.lower()]
        if local_estimates:
            best_local = min(local_estimates, key=lambda x: x.total_cost_usd)
            scenarios.append(self._create_roi_scenario(
                "Best Local Option",
                best_local,
                monthly_api_cost,
                monthly_savings,
                usage_pattern
            ))
        
        # Scenario 4: Cloud training (if available)
        cloud_estimates = [e for e in cost_estimates if "cloud" in e.approach_name.lower()]
        if cloud_estimates:
            best_cloud = min(cloud_estimates, key=lambda x: x.total_cost_usd)
            scenarios.append(self._create_roi_scenario(
                "Best Cloud Option",
                best_cloud,
                monthly_api_cost,
                monthly_savings,
                usage_pattern
            ))
        
        return scenarios[:4]  # Limit to 4 scenarios
    
    def _create_roi_scenario(self, 
                            name: str,
                            estimate: CostEstimate,
                            monthly_api_cost: float,
                            monthly_savings: float,
                            usage_pattern: UsagePattern) -> ROIScenario:
        """Create a single ROI scenario"""
        
        training_cost = estimate.total_cost_usd
        
        # Adjust savings based on usage pattern
        pattern_multiplier = {
            UsagePattern.LIGHT: 0.7,      # Less usage = less savings
            UsagePattern.MODERATE: 1.0,   # Baseline
            UsagePattern.HEAVY: 1.2,      # More usage = more savings
            UsagePattern.ENTERPRISE: 1.5  # Enterprise scale benefits
        }
        
        adjusted_savings = monthly_savings * pattern_multiplier[usage_pattern]
        
        # Calculate break-even
        if adjusted_savings > 0:
            break_even_months = training_cost / adjusted_savings
        else:
            break_even_months = float('inf')
        
        # Calculate long-term savings
        savings_12_months = (adjusted_savings * 12) - training_cost
        savings_24_months = (adjusted_savings * 24) - training_cost
        
        # Determine confidence based on approach and usage pattern
        base_confidence = estimate.confidence
        if usage_pattern in [UsagePattern.LIGHT]:
            base_confidence *= 0.8  # Lower confidence for light usage
        elif usage_pattern in [UsagePattern.ENTERPRISE]:
            base_confidence *= 1.1  # Higher confidence for enterprise
        
        confidence = min(base_confidence, 0.95)
        
        assumptions = [
            f"Monthly usage: {usage_pattern.value}",
            f"Training cost: ${training_cost:.2f}",
            f"Monthly API savings: ${adjusted_savings:.2f}",
            "90% cost reduction assumption"
        ]
        
        return ROIScenario(
            name=name,
            training_cost=training_cost,
            monthly_api_cost_current=monthly_api_cost,
            monthly_api_cost_after_training=monthly_api_cost * 0.1,  # 10% residual cost
            monthly_savings=adjusted_savings,
            break_even_months=break_even_months,
            total_savings_12_months=savings_12_months,
            total_savings_24_months=savings_24_months,
            confidence=confidence,
            assumptions=assumptions
        )
    
    def _calculate_break_even_analysis(self, 
                                     best_estimate: CostEstimate,
                                     api_costs: Dict[str, Any],
                                     monthly_tokens: int) -> Dict[str, Any]:
        """Calculate detailed break-even analysis"""
        
        training_cost = best_estimate.total_cost_usd
        monthly_savings = api_costs['monthly_savings_potential']
        
        if monthly_savings <= 0:
            return {
                'months_to_break_even': float('inf'),
                'message': 'No API cost savings - training not economically viable',
                'break_even_date': None
            }
        
        months_to_break_even = training_cost / monthly_savings
        
        # Calculate cumulative savings over time
        time_points = [1, 3, 6, 12, 18, 24]
        cumulative_analysis = []
        
        for months in time_points:
            cumulative_savings = (monthly_savings * months) - training_cost
            roi_percentage = (cumulative_savings / training_cost) * 100 if training_cost > 0 else 0
            
            cumulative_analysis.append({
                'months': months,
                'cumulative_savings': round(cumulative_savings, 2),
                'roi_percentage': round(roi_percentage, 1),
                'break_even_achieved': cumulative_savings > 0
            })
        
        return {
            'months_to_break_even': round(months_to_break_even, 2),
            'training_investment': training_cost,
            'monthly_savings': monthly_savings,
            'cumulative_analysis': cumulative_analysis,
            'break_even_category': self._categorize_break_even(months_to_break_even)
        }
    
    def _categorize_break_even(self, months: float) -> str:
        """Categorize break-even timeline"""
        if months <= 3:
            return "Excellent (≤3 months)"
        elif months <= 6:
            return "Good (3-6 months)"
        elif months <= 12:
            return "Acceptable (6-12 months)"
        elif months <= 24:
            return "Poor (12-24 months)"
        else:
            return "Not viable (>24 months)"
    
    def _generate_time_projections(self, 
                                  training_cost: float,
                                  monthly_savings: float,
                                  time_horizon: TimeHorizon) -> Dict[str, Any]:
        """Generate time-based financial projections"""
        
        horizons = {
            TimeHorizon.SHORT_TERM: [3, 6],
            TimeHorizon.MEDIUM_TERM: [6, 12, 18],
            TimeHorizon.LONG_TERM: [12, 18, 24, 36]
        }
        
        projection_months = horizons[time_horizon]
        projections = {}
        
        for months in projection_months:
            total_savings = (monthly_savings * months) - training_cost
            roi_percentage = (total_savings / training_cost) * 100 if training_cost > 0 else 0
            
            projections[f'months_{months}'] = {
                'total_savings': round(total_savings, 2),
                'roi_percentage': round(roi_percentage, 1),
                'monthly_average_savings': round(total_savings / months, 2) if months > 0 else 0
            }
        
        # Calculate ROI for standard periods
        roi_12_months = ((monthly_savings * 12) - training_cost) / training_cost * 100 if training_cost > 0 else 0
        roi_24_months = ((monthly_savings * 24) - training_cost) / training_cost * 100 if training_cost > 0 else 0
        
        return {
            'time_horizon': time_horizon.value,
            'projections': projections,
            'roi_12_months': round(roi_12_months, 1),
            'roi_24_months': round(roi_24_months, 1),
            'recommended_evaluation_period': self._recommend_evaluation_period(monthly_savings, training_cost)
        }
    
    def _recommend_evaluation_period(self, monthly_savings: float, training_cost: float) -> str:
        """Recommend appropriate evaluation period"""
        if monthly_savings <= 0:
            return "Not applicable - no savings projected"
        
        break_even_months = training_cost / monthly_savings
        
        if break_even_months <= 6:
            return "12 months (quick payback)"
        elif break_even_months <= 12:
            return "18 months (moderate payback)"
        else:
            return "24+ months (long-term investment)"
    
    def _analyze_risks(self, 
                      best_estimate: CostEstimate,
                      usage_pattern: UsagePattern,
                      monthly_tokens: int) -> Dict[str, Any]:
        """Analyze risks associated with training investment"""
        
        risks = []
        risk_factors = {}
        
        # Usage volatility risk
        if usage_pattern == UsagePattern.LIGHT:
            risks.append("Low usage may not justify training investment")
            risk_factors['usage_volatility'] = 'High'
        elif usage_pattern == UsagePattern.ENTERPRISE:
            risk_factors['usage_volatility'] = 'Low'
        else:
            risk_factors['usage_volatility'] = 'Medium'
        
        # Technology change risk
        if "local" in best_estimate.approach_name.lower():
            risks.append("Hardware may become obsolete")
            risk_factors['technology_obsolescence'] = 'Medium'
        else:
            risk_factors['technology_obsolescence'] = 'Low'
        
        # API pricing change risk
        risks.append("API prices may decrease, reducing savings")
        risk_factors['api_pricing_changes'] = 'Medium'
        
        # Model performance risk
        if "lora" in best_estimate.approach_name.lower() or "qlora" in best_estimate.approach_name.lower():
            risks.append("LoRA/QLoRA may provide lower quality than full fine-tuning")
            risk_factors['model_performance'] = 'Medium'
        else:
            risk_factors['model_performance'] = 'Low'
        
        # Training complexity risk
        if best_estimate.hardware_requirements.get('gpu_count', 1) > 1:
            risks.append("Multi-GPU setup increases complexity and failure risk")
            risk_factors['technical_complexity'] = 'High'
        else:
            risk_factors['technical_complexity'] = 'Low'
        
        # Calculate overall risk score
        risk_weights = {
            'usage_volatility': 0.3,
            'technology_obsolescence': 0.2,
            'api_pricing_changes': 0.2,
            'model_performance': 0.2,
            'technical_complexity': 0.1
        }
        
        risk_values = {'Low': 1, 'Medium': 2, 'High': 3}
        
        weighted_risk = sum(
            risk_weights.get(factor, 0) * risk_values.get(level, 2)
            for factor, level in risk_factors.items()
        )
        
        overall_risk = 'Low' if weighted_risk < 1.5 else 'Medium' if weighted_risk < 2.5 else 'High'
        
        return {
            'overall_risk_level': overall_risk,
            'risk_factors': risk_factors,
            'specific_risks': risks,
            'risk_score': round(weighted_risk, 2),
            'mitigation_strategies': self._suggest_risk_mitigations(risk_factors)
        }
    
    def _suggest_risk_mitigations(self, risk_factors: Dict[str, str]) -> List[str]:
        """Suggest risk mitigation strategies"""
        mitigations = []
        
        if risk_factors.get('usage_volatility') == 'High':
            mitigations.append("Start with smaller models to test usage patterns")
        
        if risk_factors.get('technology_obsolescence') == 'Medium':
            mitigations.append("Consider cloud training to avoid hardware ownership")
        
        if risk_factors.get('technical_complexity') == 'High':
            mitigations.append("Begin with single-GPU setups and scale gradually")
        
        mitigations.append("Monitor API pricing trends for timing decisions")
        mitigations.append("Start with LoRA training to minimize initial investment")
        
        return mitigations
    
    def _perform_sensitivity_analysis(self, 
                                    best_estimate: CostEstimate,
                                    api_costs: Dict[str, Any],
                                    monthly_tokens: int) -> Dict[str, Any]:
        """Perform sensitivity analysis on key variables"""
        
        base_training_cost = best_estimate.total_cost_usd
        base_monthly_savings = api_costs['monthly_savings_potential']
        base_break_even = base_training_cost / base_monthly_savings if base_monthly_savings > 0 else float('inf')
        
        # Test sensitivity to various factors
        sensitivity_tests = {
            'usage_volume': {
                'low_usage': {'multiplier': 0.5, 'description': '50% less usage'},
                'high_usage': {'multiplier': 2.0, 'description': '2x more usage'}
            },
            'api_pricing': {
                'api_price_drop': {'multiplier': 0.7, 'description': '30% API price reduction'},
                'api_price_increase': {'multiplier': 1.3, 'description': '30% API price increase'}
            },
            'training_cost': {
                'cost_overrun': {'multiplier': 1.5, 'description': '50% training cost overrun'},
                'cost_savings': {'multiplier': 0.8, 'description': '20% training cost reduction'}
            }
        }
        
        sensitivity_results = {}
        
        for category, tests in sensitivity_tests.items():
            category_results = {}
            
            for test_name, test_config in tests.items():
                multiplier = test_config['multiplier']
                
                if category == 'usage_volume':
                    adjusted_savings = base_monthly_savings * multiplier
                    adjusted_cost = base_training_cost
                elif category == 'api_pricing':
                    adjusted_savings = base_monthly_savings * multiplier
                    adjusted_cost = base_training_cost
                elif category == 'training_cost':
                    adjusted_savings = base_monthly_savings
                    adjusted_cost = base_training_cost * multiplier
                
                new_break_even = adjusted_cost / adjusted_savings if adjusted_savings > 0 else float('inf')
                impact_percentage = ((new_break_even - base_break_even) / base_break_even * 100) if base_break_even != float('inf') else 0
                
                category_results[test_name] = {
                    'description': test_config['description'],
                    'new_break_even_months': round(new_break_even, 2) if new_break_even != float('inf') else None,
                    'impact_percentage': round(impact_percentage, 1),
                    'impact_assessment': self._assess_sensitivity_impact(impact_percentage)
                }
            
            sensitivity_results[category] = category_results
        
        return {
            'base_break_even_months': round(base_break_even, 2) if base_break_even != float('inf') else None,
            'sensitivity_tests': sensitivity_results,
            'most_sensitive_factor': self._identify_most_sensitive_factor(sensitivity_results),
            'sensitivity_summary': self._summarize_sensitivity(sensitivity_results)
        }
    
    def _assess_sensitivity_impact(self, impact_percentage: float) -> str:
        """Assess the impact of sensitivity changes"""
        abs_impact = abs(impact_percentage)
        if abs_impact < 10:
            return "Low sensitivity"
        elif abs_impact < 25:
            return "Medium sensitivity"
        else:
            return "High sensitivity"
    
    def _identify_most_sensitive_factor(self, sensitivity_results: Dict[str, Any]) -> str:
        """Identify the factor with highest sensitivity"""
        max_impact = 0
        most_sensitive = "usage_volume"
        
        for category, tests in sensitivity_results.items():
            for test_name, results in tests.items():
                impact = abs(results.get('impact_percentage', 0))
                if impact > max_impact:
                    max_impact = impact
                    most_sensitive = category
        
        return most_sensitive
    
    def _summarize_sensitivity(self, sensitivity_results: Dict[str, Any]) -> List[str]:
        """Summarize key sensitivity insights"""
        summary = []
        
        # Check usage volume sensitivity
        usage_tests = sensitivity_results.get('usage_volume', {})
        low_usage_impact = usage_tests.get('low_usage', {}).get('impact_percentage', 0)
        if abs(low_usage_impact) > 50:
            summary.append("ROI highly sensitive to usage volume - ensure stable usage patterns")
        
        # Check API pricing sensitivity
        pricing_tests = sensitivity_results.get('api_pricing', {})
        price_drop_impact = pricing_tests.get('api_price_drop', {}).get('impact_percentage', 0)
        if abs(price_drop_impact) > 30:
            summary.append("Vulnerable to API price reductions - monitor market trends")
        
        # Check training cost sensitivity
        cost_tests = sensitivity_results.get('training_cost', {})
        cost_overrun_impact = cost_tests.get('cost_overrun', {}).get('impact_percentage', 0)
        if abs(cost_overrun_impact) > 25:
            summary.append("Sensitive to training cost overruns - budget conservatively")
        
        if not summary:
            summary.append("ROI relatively stable across key variables")
        
        return summary
    
    def _generate_roi_recommendations(self, 
                                    best_estimate: CostEstimate,
                                    usage_pattern: UsagePattern,
                                    break_even_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable ROI recommendations"""
        
        recommendations = []
        break_even_months = break_even_analysis.get('months_to_break_even', float('inf'))
        
        # Break-even based recommendations
        if break_even_months <= 3:
            recommendations.append("Excellent ROI - proceed with training immediately")
        elif break_even_months <= 6:
            recommendations.append("Good ROI - training is economically justified")
        elif break_even_months <= 12:
            recommendations.append("Moderate ROI - consider if you have long-term usage plans")
        else:
            recommendations.append("Poor ROI - training may not be economically justified")
        
        # Usage pattern recommendations
        if usage_pattern == UsagePattern.LIGHT:
            recommendations.append("Light usage - consider starting with smaller models or LoRA training")
        elif usage_pattern == UsagePattern.HEAVY:
            recommendations.append("Heavy usage - training investment highly recommended")
        elif usage_pattern == UsagePattern.ENTERPRISE:
            recommendations.append("Enterprise scale - training provides significant cost advantages")
        
        # Approach-specific recommendations
        if "lora" in best_estimate.approach_name.lower():
            recommendations.append("LoRA approach offers good balance of cost and quality")
        elif "local" in best_estimate.approach_name.lower():
            recommendations.append("Local training provides best long-term economics")
        elif "cloud" in best_estimate.approach_name.lower():
            recommendations.append("Cloud training offers flexibility without hardware investment")
        
        # Risk-based recommendations
        if best_estimate.confidence < 0.7:
            recommendations.append("Cost estimates have uncertainty - consider starting small")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _analyze_usage_pattern(self, 
                             usage_pattern: UsagePattern,
                             monthly_tokens: int) -> Dict[str, Any]:
        """Analyze the user's usage pattern"""
        
        pattern_characteristics = {
            UsagePattern.LIGHT: {
                'description': 'Light usage (development, testing)',
                'typical_range': 'Under 10K tokens/month',
                'training_suitability': 'Limited - consider API-only approach',
                'recommendations': ['Start with smaller models', 'Monitor usage growth']
            },
            UsagePattern.MODERATE: {
                'description': 'Moderate usage (small business, personal projects)',
                'typical_range': '10K-100K tokens/month',
                'training_suitability': 'Good - training becomes cost-effective',
                'recommendations': ['LoRA training recommended', 'Monitor ROI closely']
            },
            UsagePattern.HEAVY: {
                'description': 'Heavy usage (established business, high-volume)',
                'typical_range': '100K-1M tokens/month',
                'training_suitability': 'Excellent - training highly recommended',
                'recommendations': ['Full fine-tuning justified', 'Consider multiple models']
            },
            UsagePattern.ENTERPRISE: {
                'description': 'Enterprise usage (large organization)',
                'typical_range': 'Over 1M tokens/month',
                'training_suitability': 'Critical - training essential for cost control',
                'recommendations': ['Multi-model strategy', 'Dedicated infrastructure']
            }
        }
        
        characteristics = pattern_characteristics[usage_pattern]
        
        # Calculate usage efficiency metrics
        tokens_per_day = monthly_tokens / 30
        usage_consistency = "High" if usage_pattern in [UsagePattern.HEAVY, UsagePattern.ENTERPRISE] else "Medium"
        
        return {
            'pattern': usage_pattern.value,
            'monthly_tokens': monthly_tokens,
            'daily_average': round(tokens_per_day, 0),
            'characteristics': characteristics,
            'usage_consistency': usage_consistency,
            'growth_potential': self._assess_growth_potential(usage_pattern),
            'cost_optimization_priority': self._assess_cost_priority(usage_pattern)
        }
    
    def _assess_growth_potential(self, usage_pattern: UsagePattern) -> str:
        """Assess potential for usage growth"""
        growth_map = {
            UsagePattern.LIGHT: "High potential for growth",
            UsagePattern.MODERATE: "Moderate growth expected",
            UsagePattern.HEAVY: "Stable with gradual growth",
            UsagePattern.ENTERPRISE: "Predictable enterprise growth"
        }
        return growth_map[usage_pattern]
    
    def _assess_cost_priority(self, usage_pattern: UsagePattern) -> str:
        """Assess priority level for cost optimization"""
        priority_map = {
            UsagePattern.LIGHT: "Low priority",
            UsagePattern.MODERATE: "Medium priority",
            UsagePattern.HEAVY: "High priority",
            UsagePattern.ENTERPRISE: "Critical priority"
        }
        return priority_map[usage_pattern]
    
    def _scenario_to_dict(self, scenario: ROIScenario) -> Dict[str, Any]:
        """Convert ROI scenario to dictionary"""
        return {
            'name': scenario.name,
            'training_cost': round(scenario.training_cost, 2),
            'monthly_api_cost_current': round(scenario.monthly_api_cost_current, 2),
            'monthly_api_cost_after_training': round(scenario.monthly_api_cost_after_training, 2),
            'monthly_savings': round(scenario.monthly_savings, 2),
            'break_even_months': round(scenario.break_even_months, 2) if scenario.break_even_months != float('inf') else None,
            'total_savings_12_months': round(scenario.total_savings_12_months, 2),
            'total_savings_24_months': round(scenario.total_savings_24_months, 2),
            'confidence': scenario.confidence,
            'assumptions': scenario.assumptions
        }


class CostOptimizer:
    """Advanced cost optimization engine with intelligent recommendations"""
    
    def __init__(self, roi_calculator: Optional[ROICalculator] = None):
        self.roi_calculator = roi_calculator or ROICalculator()
        self.optimization_strategies = self._initialize_optimization_strategies()
        logging.info("Cost Optimizer initialized")
    
    def _initialize_optimization_strategies(self) -> Dict[str, Any]:
        """Initialize optimization strategy database"""
        return {
            'training_approaches': {
                'full_finetuning': {
                    'cost_multiplier': 1.0,
                    'quality_score': 1.0,
                    'complexity': 'High',
                    'best_for': ['Production models', 'Maximum quality']
                },
                'lora': {
                    'cost_multiplier': 0.3,
                    'quality_score': 0.85,
                    'complexity': 'Medium',
                    'best_for': ['Cost optimization', 'Quick iteration']
                },
                'qlora': {
                    'cost_multiplier': 0.2,
                    'quality_score': 0.8,
                    'complexity': 'Medium',
                    'best_for': ['Memory constraints', 'Budget optimization']
                }
            },
            'hardware_strategies': {
                'single_gpu': {
                    'cost_multiplier': 1.0,
                    'speed_multiplier': 1.0,
                    'complexity': 'Low'
                },
                'multi_gpu': {
                    'cost_multiplier': 2.5,  # Not linear due to overhead
                    'speed_multiplier': 1.8,
                    'complexity': 'High'
                }
            }
        }
    

    def generate_optimization_recommendations(self, 
                                            cost_estimates: List[CostEstimate],
                                            user_constraints: Dict[str, Any] = None) -> List[OptimizationRecommendation]:
        """
        Generate comprehensive optimization recommendations
        
        Args:
            cost_estimates: Available training cost estimates
            user_constraints: User constraints (budget, time, quality requirements)
            
        Returns:
            List of prioritized optimization recommendations
        """
        
        if not cost_estimates:
            return []
        
        user_constraints = user_constraints or {}
        recommendations = []
        
        # Sort estimates for analysis
        sorted_by_cost = sorted(cost_estimates, key=lambda x: x.total_cost_usd)
        sorted_by_time = sorted(cost_estimates, key=lambda x: x.training_hours)
        
        best_cost = sorted_by_cost[0]
        fastest = sorted_by_time[0]
        
        # Generate cost reduction recommendations
        recommendations.extend(self._generate_cost_reduction_recommendations(
            cost_estimates, user_constraints
        ))
        
        # Generate speed optimization recommendations
        recommendations.extend(self._generate_speed_optimization_recommendations(
            cost_estimates, user_constraints
        ))
        
        # Generate quality optimization recommendations
        recommendations.extend(self._generate_quality_optimization_recommendations(
            cost_estimates, user_constraints
        ))
        
        # Generate hardware optimization recommendations
        recommendations.extend(self._generate_hardware_recommendations(
            cost_estimates, user_constraints
        ))
        
        # Generate provider selection recommendations
        recommendations.extend(self._generate_provider_recommendations(
            cost_estimates, user_constraints
        ))
        
        # Score and sort recommendations
        scored_recommendations = self._score_recommendations(recommendations, user_constraints)
        
        return scored_recommendations[:10]  # Return top 10 recommendations
    
    def _generate_cost_reduction_recommendations(self, 
                                               cost_estimates: List[CostEstimate],
                                               constraints: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate cost reduction focused recommendations"""
        
        recommendations = []
        budget = constraints.get('max_budget')
        
        # Find cost savings opportunities
        sorted_estimates = sorted(cost_estimates, key=lambda x: x.total_cost_usd)
        cheapest = sorted_estimates[0]
        most_expensive = sorted_estimates[-1]
        
        potential_savings = most_expensive.total_cost_usd - cheapest.total_cost_usd
        
        if potential_savings > 0:
            savings_percentage = (potential_savings / most_expensive.total_cost_usd) * 100
            
            recommendations.append(OptimizationRecommendation(
                category="cost_reduction",
                title=f"Switch to {cheapest.approach_name}",
                description=f"Save ${potential_savings:.2f} ({savings_percentage:.0f}%) by using the most cost-effective approach",
                impact="High" if savings_percentage > 50 else "Medium" if savings_percentage > 20 else "Low",
                effort="Low",
                estimated_savings=potential_savings,
                confidence=min(cheapest.confidence, 0.9)
            ))
        
        # LoRA vs full fine-tuning recommendations
        lora_estimates = [e for e in cost_estimates if "lora" in e.approach_name.lower()]
        full_estimates = [e for e in cost_estimates if "full" in e.approach_name.lower() and "lora" not in e.approach_name.lower()]
        
        if lora_estimates and full_estimates:
            best_lora = min(lora_estimates, key=lambda x: x.total_cost_usd)
            best_full = min(full_estimates, key=lambda x: x.total_cost_usd)
            
            lora_savings = best_full.total_cost_usd - best_lora.total_cost_usd
            if lora_savings > 0:
                recommendations.append(OptimizationRecommendation(
                    category="cost_reduction",
                    title="Use LoRA instead of full fine-tuning",
                    description=f"LoRA training saves ${lora_savings:.2f} with minimal quality loss (typically 5-15%)",
                    impact="High",
                    effort="Low",
                    estimated_savings=lora_savings,
                    confidence=0.85
                ))
        
        # QLoRA recommendations for memory-constrained scenarios
        qlora_estimates = [e for e in cost_estimates if "qlora" in e.approach_name.lower()]
        if qlora_estimates:
            best_qlora = min(qlora_estimates, key=lambda x: x.total_cost_usd)
            
            # Compare with other approaches
            other_estimates = [e for e in cost_estimates if "qlora" not in e.approach_name.lower()]
            if other_estimates:
                best_other = min(other_estimates, key=lambda x: x.total_cost_usd)
                qlora_savings = best_other.total_cost_usd - best_qlora.total_cost_usd
                
                if qlora_savings > 0:
                    recommendations.append(OptimizationRecommendation(
                        category="cost_reduction",
                        title="Consider QLoRA for maximum cost savings",
                        description=f"QLoRA saves ${qlora_savings:.2f} through 4-bit quantization with 10-20% quality trade-off",
                        impact="Medium",
                        effort="Medium",
                        estimated_savings=qlora_savings,
                        confidence=0.75
                    ))
        
        # Budget-specific recommendations
        if budget:
            over_budget = [e for e in cost_estimates if e.total_cost_usd > budget]
            within_budget = [e for e in cost_estimates if e.total_cost_usd <= budget]
            
            if over_budget and within_budget:
                recommendations.append(OptimizationRecommendation(
                    category="cost_reduction",
                    title="Stay within budget constraints",
                    description=f"Choose from {len(within_budget)} approaches that fit your ${budget:.2f} budget",
                    impact="High",
                    effort="Low",
                    confidence=0.95
                ))
        
        return recommendations
    
    def _generate_speed_optimization_recommendations(self, 
                                                   cost_estimates: List[CostEstimate],
                                                   constraints: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate speed optimization recommendations"""
        
        recommendations = []
        max_time = constraints.get('max_training_hours')
        
        # Find speed improvement opportunities
        sorted_by_time = sorted(cost_estimates, key=lambda x: x.training_hours)
        fastest = sorted_by_time[0]
        slowest = sorted_by_time[-1]
        
        time_savings = slowest.training_hours - fastest.training_hours
        
        if time_savings > 0:
            recommendations.append(OptimizationRecommendation(
                category="speed_optimization",
                title=f"Use {fastest.approach_name} for fastest training",
                description=f"Save {time_savings:.1f} hours ({(time_savings/slowest.training_hours)*100:.0f}%) training time",
                impact="High" if time_savings > 10 else "Medium",
                effort="Low",
                estimated_time_savings=time_savings,
                confidence=fastest.confidence
            ))
        
        # GPU upgrade recommendations
        cloud_estimates = [e for e in cost_estimates if "cloud" in e.approach_name.lower()]
        if cloud_estimates:
            # Find GPU type patterns
            gpu_performance = {}
            for estimate in cloud_estimates:
                gpu_type = estimate.hardware_requirements.get('gpu_type', 'unknown')
                if gpu_type not in gpu_performance:
                    gpu_performance[gpu_type] = []
                gpu_performance[gpu_type].append(estimate.training_hours)
            
            # Recommend faster GPUs
            if len(gpu_performance) > 1:
                avg_times = {gpu: sum(times)/len(times) for gpu, times in gpu_performance.items()}
                fastest_gpu = min(avg_times.keys(), key=lambda x: avg_times[x])
                slowest_gpu = max(avg_times.keys(), key=lambda x: avg_times[x])
                
                if fastest_gpu != slowest_gpu:
                    time_improvement = avg_times[slowest_gpu] - avg_times[fastest_gpu]
                    recommendations.append(OptimizationRecommendation(
                        category="speed_optimization",
                        title=f"Upgrade to {fastest_gpu.upper()} GPUs",
                        description=f"Reduce training time by {time_improvement:.1f} hours compared to {slowest_gpu.upper()}",
                        impact="Medium",
                        effort="Low",
                        estimated_time_savings=time_improvement,
                        confidence=0.8
                    ))
        
        # Multi-GPU recommendations for large models
        single_gpu_estimates = [e for e in cost_estimates if e.hardware_requirements.get('gpu_count', 1) == 1]
        multi_gpu_estimates = [e for e in cost_estimates if e.hardware_requirements.get('gpu_count', 1) > 1]
        
        if single_gpu_estimates and multi_gpu_estimates:
            best_single = min(single_gpu_estimates, key=lambda x: x.training_hours)
            best_multi = min(multi_gpu_estimates, key=lambda x: x.training_hours)
            
            if best_multi.training_hours < best_single.training_hours:
                time_savings = best_single.training_hours - best_multi.training_hours
                cost_increase = best_multi.total_cost_usd - best_single.total_cost_usd
                
                recommendations.append(OptimizationRecommendation(
                    category="speed_optimization",
                    title="Consider multi-GPU setup for speed",
                    description=f"Save {time_savings:.1f} hours with multi-GPU (${cost_increase:.2f} additional cost)",
                    impact="Medium",
                    effort="High",
                    estimated_time_savings=time_savings,
                    confidence=0.7
                ))
        
        # Time constraint recommendations
        if max_time:
            fast_enough = [e for e in cost_estimates if e.training_hours <= max_time]
            too_slow = [e for e in cost_estimates if e.training_hours > max_time]
            
            if too_slow and fast_enough:
                recommendations.append(OptimizationRecommendation(
                    category="speed_optimization",
                    title="Meet time constraints",
                    description=f"Choose from {len(fast_enough)} approaches that complete within {max_time} hours",
                    impact="High",
                    effort="Low",
                    confidence=0.95
                ))
        
        return recommendations
    
    def _generate_quality_optimization_recommendations(self, 
                                                     cost_estimates: List[CostEstimate],
                                                     constraints: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate quality optimization recommendations"""
        
        recommendations = []
        min_quality = constraints.get('min_quality_score', 0.8)
        
        # Quality vs cost trade-offs
        full_estimates = [e for e in cost_estimates if "full" in e.approach_name.lower() and "lora" not in e.approach_name.lower()]
        lora_estimates = [e for e in cost_estimates if "lora" in e.approach_name.lower() and "qlora" not in e.approach_name.lower()]
        qlora_estimates = [e for e in cost_estimates if "qlora" in e.approach_name.lower()]
        
        if full_estimates and lora_estimates:
            best_full = min(full_estimates, key=lambda x: x.total_cost_usd)
            best_lora = min(lora_estimates, key=lambda x: x.total_cost_usd)
            
            quality_cost_ratio = (best_full.total_cost_usd - best_lora.total_cost_usd) / best_full.total_cost_usd
            
            if quality_cost_ratio < 0.3:  # If full fine-tuning is less than 30% more expensive
                recommendations.append(OptimizationRecommendation(
                    category="quality_improvement",
                    title="Upgrade to full fine-tuning for maximum quality",
                    description=f"Only ${best_full.total_cost_usd - best_lora.total_cost_usd:.2f} more for 10-20% quality improvement",
                    impact="Medium",
                    effort="Low",
                    confidence=0.8
                ))
        
        # Dataset size recommendations
        recommendations.append(OptimizationRecommendation(
            category="quality_improvement",
            title="Optimize dataset size for quality",
            description="Ensure dataset size follows Chinchilla scaling laws for optimal quality/cost ratio",
            impact="Medium",
            effort="Medium",
            confidence=0.85
        ))
        
        # Model size recommendations
        if constraints.get('use_case') == 'production':
            recommendations.append(OptimizationRecommendation(
                category="quality_improvement",
                title="Consider larger model for production use",
                description="Production workloads benefit from higher quality models despite increased cost",
                impact="High",
                effort="Medium",
                confidence=0.7
            ))
        
        return recommendations
    
    def _generate_hardware_recommendations(self, 
                                         cost_estimates: List[CostEstimate],
                                         constraints: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate hardware optimization recommendations"""
        
        recommendations = []
        
        # Local vs cloud recommendations
        local_estimates = [e for e in cost_estimates if "local" in e.approach_name.lower()]
        cloud_estimates = [e for e in cost_estimates if "cloud" in e.approach_name.lower()]
        
        if local_estimates and cloud_estimates:
            best_local = min(local_estimates, key=lambda x: x.total_cost_usd)
            best_cloud = min(cloud_estimates, key=lambda x: x.total_cost_usd)
            
            if best_local.total_cost_usd < best_cloud.total_cost_usd:
                savings = best_cloud.total_cost_usd - best_local.total_cost_usd
                recommendations.append(OptimizationRecommendation(
                    category="hardware_optimization",
                    title="Use local hardware for cost savings",
                    description=f"Local training saves ${savings:.2f} vs cloud, with full control over hardware",
                    impact="High",
                    effort="Medium",
                    estimated_savings=savings,
                    confidence=0.8
                ))
            else:
                extra_cost = best_local.total_cost_usd - best_cloud.total_cost_usd
                recommendations.append(OptimizationRecommendation(
                    category="hardware_optimization",
                    title="Consider cloud training for convenience",
                    description=f"Cloud training costs only ${extra_cost:.2f} more but eliminates hardware management",
                    impact="Medium",
                    effort="Low",
                    confidence=0.8
                ))
        
        # GPU memory optimization
        high_memory_estimates = [e for e in cost_estimates 
                               if e.hardware_requirements.get('memory_required_gb', 0) > 24]
        
        if high_memory_estimates:
            recommendations.append(OptimizationRecommendation(
                category="hardware_optimization",
                title="Optimize memory usage",
                description="Large memory requirements detected - consider gradient checkpointing or model sharding",
                impact="Medium",
                effort="High",
                confidence=0.7
            ))
        
        # Power efficiency recommendations
        if local_estimates:
            recommendations.append(OptimizationRecommendation(
                category="hardware_optimization",
                title="Consider power efficiency",
                description="RTX 4090 offers best performance per watt for local training",
                impact="Low",
                effort="Low",
                confidence=0.8
            ))
        
        return recommendations
    
    def _generate_provider_recommendations(self, 
                                         cost_estimates: List[CostEstimate],
                                         constraints: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Generate cloud provider selection recommendations"""
        
        recommendations = []
        
        # Analyze cloud providers in cost estimates
        provider_costs = {}
        for estimate in cost_estimates:
            if "cloud" in estimate.approach_name.lower():
                # Extract provider from approach name or hardware requirements
                approach_lower = estimate.approach_name.lower()
                if "lambda" in approach_lower:
                    provider = "Lambda Labs"
                elif "vast" in approach_lower:
                    provider = "Vast.ai"
                elif "runpod" in approach_lower:
                    provider = "RunPod"
                else:
                    provider = "Generic Cloud"
                
                if provider not in provider_costs:
                    provider_costs[provider] = []
                provider_costs[provider].append(estimate)
        
        if len(provider_costs) > 1:
            # Find best provider by cost
            provider_best_costs = {}
            for provider, estimates in provider_costs.items():
                provider_best_costs[provider] = min(estimates, key=lambda x: x.total_cost_usd)
            
            best_provider = min(provider_best_costs.keys(), 
                              key=lambda x: provider_best_costs[x].total_cost_usd)
            worst_provider = max(provider_best_costs.keys(), 
                               key=lambda x: provider_best_costs[x].total_cost_usd)
            
            if best_provider != worst_provider:
                savings = (provider_best_costs[worst_provider].total_cost_usd - 
                          provider_best_costs[best_provider].total_cost_usd)
                
                recommendations.append(OptimizationRecommendation(
                    category="provider_selection",
                    title=f"Use {best_provider} for best pricing",
                    description=f"Save ${savings:.2f} compared to {worst_provider}",
                    impact="Medium",
                    effort="Low",
                    estimated_savings=savings,
                    confidence=0.8
                ))
        
        # Spot pricing recommendations
        spot_estimates = [e for e in cost_estimates if any("spot" in note.lower() for note in e.notes)]
        if spot_estimates:
            recommendations.append(OptimizationRecommendation(
                category="provider_selection",
                title="Consider spot instances for additional savings",
                description="Spot pricing can save 50-70% but may be interrupted",
                impact="Medium",
                effort="Medium",
                confidence=0.6
            ))
        
        return recommendations
    
    def _score_recommendations(self, 
                             recommendations: List[OptimizationRecommendation],
                             constraints: Dict[str, Any]) -> List[OptimizationRecommendation]:
        """Score and prioritize recommendations based on user constraints"""
        
        # Define scoring weights based on user priorities
        priority = constraints.get('priority', 'balanced')
        
        weight_profiles = {
            'cost': {'cost_reduction': 0.5, 'speed_optimization': 0.2, 'quality_improvement': 0.1, 
                    'hardware_optimization': 0.1, 'provider_selection': 0.1},
            'speed': {'cost_reduction': 0.1, 'speed_optimization': 0.5, 'quality_improvement': 0.2, 
                     'hardware_optimization': 0.1, 'provider_selection': 0.1},
            'quality': {'cost_reduction': 0.1, 'speed_optimization': 0.1, 'quality_improvement': 0.5, 
                       'hardware_optimization': 0.2, 'provider_selection': 0.1},
            'balanced': {'cost_reduction': 0.3, 'speed_optimization': 0.3, 'quality_improvement': 0.2, 
                        'hardware_optimization': 0.1, 'provider_selection': 0.1}
        }
        
        weights = weight_profiles.get(priority, weight_profiles['balanced'])
        
        # Score each recommendation
        for rec in recommendations:
            score = 0
            
            # Category weight
            score += weights.get(rec.category, 0.1) * 40
            
            # Impact score
            impact_scores = {'Low': 5, 'Medium': 15, 'High': 25}
            score += impact_scores.get(rec.impact, 10)
            
            # Effort score (lower effort = higher score)
            effort_scores = {'Low': 15, 'Medium': 10, 'High': 5}
            score += effort_scores.get(rec.effort, 10)
            
            # Confidence score
            score += rec.confidence * 20
            
            # Savings impact (if available)
            if rec.estimated_savings:
                # Normalize savings impact (higher savings = higher score)
                max_savings = max((r.estimated_savings for r in recommendations if r.estimated_savings), default=1)
                savings_score = (rec.estimated_savings / max_savings) * 10
                score += savings_score
            
            rec.score = score
        
        # Sort by score (descending)
        return sorted(recommendations, key=lambda x: getattr(x, 'score', 0), reverse=True)
    
    def analyze_cost_efficiency(self, cost_estimates: List[CostEstimate]) -> Dict[str, Any]:
        """Analyze cost efficiency across different approaches"""
        
        if not cost_estimates:
            return {'efficiency_score': 0, 'analysis': 'No estimates available'}
        
        # Calculate efficiency metrics
        costs = [e.total_cost_usd for e in cost_estimates]
        times = [e.training_hours for e in cost_estimates]
        
        # Cost efficiency = inverse of cost variance (lower variance = higher efficiency)
        cost_variance = statistics.variance(costs) if len(costs) > 1 else 0
        cost_efficiency = 1 / (1 + cost_variance / statistics.mean(costs)) if statistics.mean(costs) > 0 else 0
        
        # Time efficiency = inverse of time variance
        time_variance = statistics.variance(times) if len(times) > 1 else 0
        time_efficiency = 1 / (1 + time_variance / statistics.mean(times)) if statistics.mean(times) > 0 else 0
        
        # Overall efficiency score (0-100)
        efficiency_score = (cost_efficiency + time_efficiency) / 2 * 100
        
        # Find optimal cost/performance ratio
        cost_performance_ratios = []
        for estimate in cost_estimates:
            # Lower cost and time = better ratio
            ratio = estimate.total_cost_usd * estimate.training_hours
            cost_performance_ratios.append({
                'approach': estimate.approach_name,
                'ratio': ratio,
                'cost': estimate.total_cost_usd,
                'time': estimate.training_hours
            })
        
        cost_performance_ratios.sort(key=lambda x: x['ratio'])
        optimal_approach = cost_performance_ratios[0] if cost_performance_ratios else None
        
        return {
            'efficiency_score': round(efficiency_score, 1),
            'cost_efficiency': round(cost_efficiency * 100, 1),
            'time_efficiency': round(time_efficiency * 100, 1),
            'optimal_approach': optimal_approach,
            'cost_range': {
                'min': min(costs),
                'max': max(costs),
                'variance': round(cost_variance, 2)
            },
            'time_range': {
                'min': min(times),
                'max': max(times),
                'variance': round(time_variance, 2)
            },
            'recommendations': self._generate_efficiency_recommendations(
                efficiency_score, optimal_approach, cost_estimates
            )
        }
    
    def _generate_efficiency_recommendations(self, 
                                           efficiency_score: float,
                                           optimal_approach: Optional[Dict[str, Any]],
                                           cost_estimates: List[CostEstimate]) -> List[str]:
        """Generate efficiency-based recommendations"""
        
        recommendations = []
        
        if efficiency_score > 80:
            recommendations.append("Excellent efficiency - your options are well-optimized")
        elif efficiency_score > 60:
            recommendations.append("Good efficiency - consider minor optimizations")
        else:
            recommendations.append("Low efficiency - significant optimization opportunities exist")
        
        if optimal_approach:
            recommendations.append(
                f"Best cost/performance ratio: {optimal_approach['approach']} "
                f"(${optimal_approach['cost']:.2f}, {optimal_approach['time']:.1f}h)"
            )
        
        # Check for obvious inefficiencies
        costs = [e.total_cost_usd for e in cost_estimates]
        if max(costs) > min(costs) * 5:  # 5x cost difference
            recommendations.append("Large cost variations detected - review training approaches")
        
        times = [e.training_hours for e in cost_estimates]
        if max(times) > min(times) * 3:  # 3x time difference
            recommendations.append("Large time variations detected - consider hardware upgrades")
        
        return recommendations


# Export classes and convenience functions
__all__ = [
    'ROICalculator',
    'CostOptimizer', 
    'ROIScenario',
    'OptimizationRecommendation',
    'UsagePattern',
    'TimeHorizon'
]
