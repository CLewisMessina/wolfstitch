# core/model_database.py
"""
Enhanced Model Parameter Database for AI Training Cost Analysis
Comprehensive database of popular AI models with training parameters
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ModelFamily(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    META = "meta"
    MISTRAL = "mistral"
    GOOGLE = "google"
    BERT = "bert"
    COHERE = "cohere"
    TOGETHER = "together"

class TrainingFeasibility(Enum):
    LOCAL_FEASIBLE = "local_feasible"      # Can train on consumer hardware
    CLOUD_ONLY = "cloud_only"             # Requires cloud infrastructure
    API_ONLY = "api_only"                 # Training not available, API only
    RESEARCH_ONLY = "research_only"       # Academic/research access only

@dataclass
class ModelInfo:
    name: str
    display_name: str
    family: ModelFamily
    parameters: int                        # Total parameter count
    context_length: int                   # Maximum context window
    training_tokens: Optional[int]        # Chinchilla-optimal training tokens
    compute_optimal_ratio: float          # Chinchilla scaling ratio (usually 20)
    training_feasibility: TrainingFeasibility
    gpu_memory_required: int              # GB VRAM for inference
    training_memory_multiplier: float     # Training memory = inference * multiplier
    estimated_training_cost: Optional[int] # USD for full training (reference models)
    api_cost_per_1k_tokens: Optional[float] # USD per 1K tokens for API
    use_cases: List[str]
    pricing_tier: str
    release_date: Optional[str]
    notes: Optional[str] = None

class ModelParameterDatabase:
    """Comprehensive database of AI models for training cost analysis"""
    
    def __init__(self):
        self.models = self._build_model_database()
        logging.info(f"Initialized model database with {len(self.models)} models")
    
    def _build_model_database(self) -> Dict[str, ModelInfo]:
        """Build comprehensive model database with accurate parameters"""
        
        models = {}
        
        # OpenAI Models
        models["gpt-4"] = ModelInfo(
            name="gpt-4",
            display_name="GPT-4",
            family=ModelFamily.OPENAI,
            parameters=1_800_000_000_000,  # ~1.8T parameters (estimated)
            context_length=8192,
            training_tokens=None,  # Not publicly disclosed
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.API_ONLY,
            gpu_memory_required=3600,  # Estimated for full model
            training_memory_multiplier=4.0,
            estimated_training_cost=78_000_000,  # $78M (industry estimates)
            api_cost_per_1k_tokens=0.03,  # $0.03/1K tokens
            use_cases=["general", "coding", "analysis", "creative"],
            pricing_tier="premium",
            release_date="2023-03",
            notes="Industry estimates for parameters and training cost"
        )
        
        models["gpt-4-turbo"] = ModelInfo(
            name="gpt-4-turbo",
            display_name="GPT-4 Turbo",
            family=ModelFamily.OPENAI,
            parameters=1_800_000_000_000,  # Similar to GPT-4
            context_length=128000,
            training_tokens=None,
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.API_ONLY,
            gpu_memory_required=3600,
            training_memory_multiplier=4.0,
            estimated_training_cost=85_000_000,  # Slightly higher due to improvements
            api_cost_per_1k_tokens=0.01,  # Lower cost per token
            use_cases=["general", "coding", "analysis", "creative", "long_context"],
            pricing_tier="premium",
            release_date="2023-11"
        )
        
        models["gpt-3.5-turbo"] = ModelInfo(
            name="gpt-3.5-turbo",
            display_name="GPT-3.5 Turbo",
            family=ModelFamily.OPENAI,
            parameters=175_000_000_000,  # ~175B parameters
            context_length=16385,
            training_tokens=300_000_000_000,  # Estimated
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.API_ONLY,
            gpu_memory_required=350,  # Estimated
            training_memory_multiplier=4.0,
            estimated_training_cost=4_600_000,  # $4.6M (industry estimates)
            api_cost_per_1k_tokens=0.002,  # $0.002/1K tokens
            use_cases=["general", "chatbots", "summarization"],
            pricing_tier="standard",
            release_date="2023-03"
        )
        
        # Anthropic Claude Models
        models["claude-3-opus"] = ModelInfo(
            name="claude-3-opus",
            display_name="Claude 3 Opus",
            family=ModelFamily.ANTHROPIC,
            parameters=175_000_000_000,  # Estimated similar to GPT-3.5
            context_length=200000,
            training_tokens=None,
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.API_ONLY,
            gpu_memory_required=350,
            training_memory_multiplier=4.0,
            estimated_training_cost=12_000_000,  # Estimated
            api_cost_per_1k_tokens=0.015,  # Input tokens
            use_cases=["analysis", "creative", "coding", "research"],
            pricing_tier="premium",
            release_date="2024-02"
        )
        
        models["claude-3-sonnet"] = ModelInfo(
            name="claude-3-sonnet",
            display_name="Claude 3 Sonnet",
            family=ModelFamily.ANTHROPIC,
            parameters=50_000_000_000,  # Estimated smaller than Opus
            context_length=200000,
            training_tokens=None,
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.API_ONLY,
            gpu_memory_required=100,
            training_memory_multiplier=4.0,
            estimated_training_cost=3_500_000,  # Estimated
            api_cost_per_1k_tokens=0.003,
            use_cases=["general", "analysis", "creative"],
            pricing_tier="standard",
            release_date="2024-02"
        )
        
        models["claude-3-haiku"] = ModelInfo(
            name="claude-3-haiku",
            display_name="Claude 3 Haiku",
            family=ModelFamily.ANTHROPIC,
            parameters=8_000_000_000,  # Estimated smaller model
            context_length=200000,
            training_tokens=None,
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.CLOUD_ONLY,
            gpu_memory_required=16,
            training_memory_multiplier=4.0,
            estimated_training_cost=800_000,  # Estimated
            api_cost_per_1k_tokens=0.00025,
            use_cases=["speed", "simple_tasks", "cost_effective"],
            pricing_tier="budget",
            release_date="2024-02"
        )
        
        # Meta LLaMA Models
        models["llama-2-7b"] = ModelInfo(
            name="llama-2-7b",
            display_name="LLaMA 2 7B",
            family=ModelFamily.META,
            parameters=7_000_000_000,
            context_length=4096,
            training_tokens=2_000_000_000_000,  # 2T tokens
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.LOCAL_FEASIBLE,
            gpu_memory_required=14,  # 13.5GB for inference
            training_memory_multiplier=4.0,
            estimated_training_cost=2_500_000,  # Community estimate
            api_cost_per_1k_tokens=None,  # Open source
            use_cases=["open_source", "local_deployment", "research"],
            pricing_tier="free",
            release_date="2023-07"
        )
        
        models["llama-2-13b"] = ModelInfo(
            name="llama-2-13b",
            display_name="LLaMA 2 13B",
            family=ModelFamily.META,
            parameters=13_000_000_000,
            context_length=4096,
            training_tokens=2_000_000_000_000,
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.LOCAL_FEASIBLE,
            gpu_memory_required=26,  # 25.6GB for inference
            training_memory_multiplier=4.0,
            estimated_training_cost=4_200_000,
            api_cost_per_1k_tokens=None,
            use_cases=["open_source", "local_deployment", "research"],
            pricing_tier="free",
            release_date="2023-07"
        )
        
        models["llama-2-70b"] = ModelInfo(
            name="llama-2-70b",
            display_name="LLaMA 2 70B",
            family=ModelFamily.META,
            parameters=70_000_000_000,
            context_length=4096,
            training_tokens=2_000_000_000_000,
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.CLOUD_ONLY,
            gpu_memory_required=140,  # ~140GB for inference
            training_memory_multiplier=4.0,
            estimated_training_cost=15_000_000,
            api_cost_per_1k_tokens=None,
            use_cases=["open_source", "high_quality", "research"],
            pricing_tier="free",
            release_date="2023-07"
        )
        
        # Mistral Models
        models["mistral-7b"] = ModelInfo(
            name="mistral-7b",
            display_name="Mistral 7B",
            family=ModelFamily.MISTRAL,
            parameters=7_300_000_000,
            context_length=8192,
            training_tokens=1_000_000_000_000,  # Estimated
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.LOCAL_FEASIBLE,
            gpu_memory_required=15,
            training_memory_multiplier=4.0,
            estimated_training_cost=2_200_000,
            api_cost_per_1k_tokens=0.0007,  # Via Together AI
            use_cases=["open_source", "multilingual", "local_deployment"],
            pricing_tier="free",
            release_date="2023-09"
        )
        
        models["mixtral-8x7b"] = ModelInfo(
            name="mixtral-8x7b",
            display_name="Mixtral 8x7B",
            family=ModelFamily.MISTRAL,
            parameters=56_000_000_000,  # 8 experts × 7B each
            context_length=32768,
            training_tokens=1_500_000_000_000,
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.CLOUD_ONLY,
            gpu_memory_required=90,  # Mixture of experts architecture
            training_memory_multiplier=4.0,
            estimated_training_cost=8_500_000,
            api_cost_per_1k_tokens=0.0006,
            use_cases=["open_source", "high_performance", "mixture_of_experts"],
            pricing_tier="free",
            release_date="2023-12"
        )
        
        # BERT Family
        models["bert-base-uncased"] = ModelInfo(
            name="bert-base-uncased",
            display_name="BERT Base Uncased",
            family=ModelFamily.BERT,
            parameters=110_000_000,
            context_length=512,
            training_tokens=3_300_000_000,  # BookCorpus + Wikipedia
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.LOCAL_FEASIBLE,
            gpu_memory_required=1,  # Very small
            training_memory_multiplier=3.0,  # Encoder-only is more efficient
            estimated_training_cost=50_000,
            api_cost_per_1k_tokens=None,
            use_cases=["classification", "embeddings", "understanding"],
            pricing_tier="free",
            release_date="2018-10"
        )
        
        models["roberta-base"] = ModelInfo(
            name="roberta-base",
            display_name="RoBERTa Base",
            family=ModelFamily.BERT,
            parameters=125_000_000,
            context_length=512,
            training_tokens=160_000_000_000,  # Much more data than BERT
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.LOCAL_FEASIBLE,
            gpu_memory_required=1,
            training_memory_multiplier=3.0,
            estimated_training_cost=150_000,
            api_cost_per_1k_tokens=None,
            use_cases=["classification", "embeddings", "nlp_tasks"],
            pricing_tier="free",
            release_date="2019-07"
        )
        
        models["distilbert-base-uncased"] = ModelInfo(
            name="distilbert-base-uncased",
            display_name="DistilBERT Base",
            family=ModelFamily.BERT,
            parameters=66_000_000,
            context_length=512,
            training_tokens=3_300_000_000,
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.LOCAL_FEASIBLE,
            gpu_memory_required=0.5,
            training_memory_multiplier=3.0,
            estimated_training_cost=25_000,
            api_cost_per_1k_tokens=None,
            use_cases=["fast_classification", "embeddings", "edge_deployment"],
            pricing_tier="free",
            release_date="2019-10"
        )
        
        # Google Models
        models["gemini-pro"] = ModelInfo(
            name="gemini-pro",
            display_name="Gemini Pro",
            family=ModelFamily.GOOGLE,
            parameters=175_000_000_000,  # Estimated
            context_length=32768,
            training_tokens=None,
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.API_ONLY,
            gpu_memory_required=350,
            training_memory_multiplier=4.0,
            estimated_training_cost=15_000_000,
            api_cost_per_1k_tokens=0.00025,
            use_cases=["multimodal", "general", "reasoning"],
            pricing_tier="standard",
            release_date="2023-12"
        )
        
        # Cohere Models
        models["command-r"] = ModelInfo(
            name="command-r",
            display_name="Cohere Command R",
            family=ModelFamily.COHERE,
            parameters=35_000_000_000,  # Estimated
            context_length=128000,
            training_tokens=None,
            compute_optimal_ratio=20,
            training_feasibility=TrainingFeasibility.API_ONLY,
            gpu_memory_required=70,
            training_memory_multiplier=4.0,
            estimated_training_cost=5_000_000,
            api_cost_per_1k_tokens=0.0015,
            use_cases=["rag", "enterprise", "search"],
            pricing_tier="standard",
            release_date="2024-03"
        )
        
        return models
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get detailed information for a specific model"""
        model_name_lower = model_name.lower().replace(" ", "-").replace("_", "-")
        return self.models.get(model_name_lower)
    
    def get_models_by_family(self, family: ModelFamily) -> List[ModelInfo]:
        """Get all models from a specific family"""
        return [model for model in self.models.values() if model.family == family]
    
    def get_trainable_models(self, local_only: bool = False) -> List[ModelInfo]:
        """Get models that can be trained (optionally filter to local-feasible only)"""
        if local_only:
            return [model for model in self.models.values() 
                   if model.training_feasibility == TrainingFeasibility.LOCAL_FEASIBLE]
        else:
            return [model for model in self.models.values() 
                   if model.training_feasibility in [TrainingFeasibility.LOCAL_FEASIBLE, 
                                                   TrainingFeasibility.CLOUD_ONLY]]
    
    def get_api_models(self) -> List[ModelInfo]:
        """Get models available via API"""
        return [model for model in self.models.values() 
               if model.api_cost_per_1k_tokens is not None]
    
    def estimate_chinchilla_tokens(self, parameters: int) -> int:
        """Estimate optimal training tokens using Chinchilla scaling laws"""
        # Chinchilla optimal: approximately 20 tokens per parameter
        return parameters * 20
    
    def estimate_compute_budget(self, parameters: int, training_tokens: Optional[int] = None) -> int:
        """Estimate compute budget in FLOPs using Chinchilla scaling"""
        if training_tokens is None:
            training_tokens = self.estimate_chinchilla_tokens(parameters)
        
        # Chinchilla compute: C ≈ 6 * N * D (FLOPs)
        # Where N = parameters, D = training tokens
        return 6 * parameters * training_tokens
    
    def get_models_by_feasibility(self, feasibility: TrainingFeasibility) -> List[ModelInfo]:
        """Get models by training feasibility"""
        return [model for model in self.models.values() 
               if model.training_feasibility == feasibility]
    
    def get_models_by_price_tier(self, pricing_tier: str) -> List[ModelInfo]:
        """Get models by pricing tier"""
        return [model for model in self.models.values() 
               if model.pricing_tier == pricing_tier]
    
    def search_models(self, query: str) -> List[ModelInfo]:
        """Search models by name, family, or use case"""
        query_lower = query.lower()
        results = []
        
        for model in self.models.values():
            if (query_lower in model.name.lower() or 
                query_lower in model.display_name.lower() or
                query_lower in model.family.value.lower() or
                any(query_lower in use_case.lower() for use_case in model.use_cases)):
                results.append(model)
        
        return results
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get summary statistics about the model database"""
        total_models = len(self.models)
        
        by_family = {}
        by_feasibility = {}
        by_tier = {}
        
        for model in self.models.values():
            # Count by family
            family_name = model.family.value
            by_family[family_name] = by_family.get(family_name, 0) + 1
            
            # Count by feasibility
            feasibility_name = model.training_feasibility.value
            by_feasibility[feasibility_name] = by_feasibility.get(feasibility_name, 0) + 1
            
            # Count by tier
            by_tier[model.pricing_tier] = by_tier.get(model.pricing_tier, 0) + 1
        
        return {
            "total_models": total_models,
            "by_family": by_family,
            "by_feasibility": by_feasibility,
            "by_pricing_tier": by_tier,
            "trainable_models": len(self.get_trainable_models()),
            "local_trainable": len(self.get_trainable_models(local_only=True)),
            "api_available": len(self.get_api_models())
        }
    
    def validate_database(self) -> Dict[str, Any]:
        """Validate the model database for consistency"""
        issues = []
        warnings = []
        
        for model_name, model in self.models.items():
            # Check for required fields
            if model.parameters <= 0:
                issues.append(f"{model_name}: Invalid parameter count")
            
            if model.context_length <= 0:
                issues.append(f"{model_name}: Invalid context length")
            
            if model.gpu_memory_required <= 0:
                issues.append(f"{model_name}: Invalid GPU memory requirement")
            
            # Check for reasonable values
            if model.parameters > 10_000_000_000_000:  # > 10T parameters
                warnings.append(f"{model_name}: Unusually large parameter count")
            
            if model.training_feasibility == TrainingFeasibility.LOCAL_FEASIBLE and model.gpu_memory_required > 80:
                warnings.append(f"{model_name}: May not be feasible on consumer hardware")
            
            # Check Chinchilla scaling
            if model.training_tokens:
                optimal_tokens = self.estimate_chinchilla_tokens(model.parameters)
                ratio = model.training_tokens / optimal_tokens
                if ratio < 0.1 or ratio > 10:
                    warnings.append(f"{model_name}: Training tokens far from Chinchilla optimal")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_models_validated": len(self.models)
        }

# Convenience function for easy access
def get_model_database() -> ModelParameterDatabase:
    """Get a singleton instance of the model database"""
    if not hasattr(get_model_database, '_instance'):
        get_model_database._instance = ModelParameterDatabase()
    return get_model_database._instance

# Export commonly used classes
__all__ = [
    'ModelParameterDatabase',
    'ModelInfo', 
    'ModelFamily',
    'TrainingFeasibility',
    'get_model_database'
]