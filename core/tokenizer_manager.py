# core/tokenizer_manager.py - Enhanced with Model Compatibility System
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import re

# Try importing premium tokenizer libraries
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available - premium OpenAI tokenizers disabled")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("sentence-transformers not available - embedding tokenizers disabled")

# Always available - fallback tokenizer
try:
    from transformers import AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.error("transformers library not available - core functionality compromised")

class PerformanceLevel(Enum):
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"

class AccuracyLevel(Enum):
    EXACT = "exact"
    ESTIMATED = "estimated"

class CompatibilityLevel(Enum):
    PERFECT = "perfect"      # ✅ Exact match
    GOOD = "good"            # ✅ Compatible
    ACCEPTABLE = "acceptable" # ⚠️ Usable but not optimal
    POOR = "poor"            # ❌ Not recommended

@dataclass
class TokenizerInfo:
    name: str
    display_name: str
    description: str
    is_premium: bool
    performance: PerformanceLevel
    accuracy: AccuracyLevel
    compatible_models: List[str]
    available: bool
    error_message: Optional[str] = None

@dataclass
class ModelCompatibility:
    model_name: str
    compatibility: CompatibilityLevel
    confidence: float  # 0-1 confidence in the compatibility assessment
    recommendation: str
    warnings: List[str]
    icon: str  # Unicode icon for UI display

class TokenizerManager:
    def __init__(self):
        self._tokenizers = {}
        self._compatibility_matrix = self._build_compatibility_matrix()
        self._model_database = self._build_model_database()
        self._initialize_tokenizers()

    def _build_model_database(self) -> Dict[str, Dict[str, Any]]:
        """Comprehensive database of popular AI models and their tokenizer requirements"""
        return {
            # OpenAI Models
            'gpt-4': {
                'family': 'openai',
                'optimal_tokenizer': 'tiktoken_gpt4',
                'acceptable_tokenizers': ['tiktoken_gpt35', 'gpt2'],
                'context_window': 8192,
                'training_data_cutoff': '2021-09',
                'use_cases': ['general', 'coding', 'analysis', 'creative'],
                'pricing_tier': 'premium'
            },
            'gpt-4-turbo': {
                'family': 'openai',
                'optimal_tokenizer': 'tiktoken_gpt4',
                'acceptable_tokenizers': ['tiktoken_gpt35', 'gpt2'],
                'context_window': 128000,
                'training_data_cutoff': '2023-12',
                'use_cases': ['general', 'coding', 'analysis', 'creative', 'long_context'],
                'pricing_tier': 'premium'
            },
            'gpt-4o': {
                'family': 'openai',
                'optimal_tokenizer': 'tiktoken_gpt4',
                'acceptable_tokenizers': ['tiktoken_gpt35', 'gpt2'],
                'context_window': 128000,
                'training_data_cutoff': '2023-10',
                'use_cases': ['multimodal', 'general', 'coding', 'analysis'],
                'pricing_tier': 'premium'
            },
            'gpt-3.5-turbo': {
                'family': 'openai',
                'optimal_tokenizer': 'tiktoken_gpt35',
                'acceptable_tokenizers': ['tiktoken_gpt4', 'gpt2'],
                'context_window': 16385,
                'training_data_cutoff': '2021-09',
                'use_cases': ['general', 'chatbots', 'summarization'],
                'pricing_tier': 'standard'
            },
            'gpt-3.5-turbo-16k': {
                'family': 'openai',
                'optimal_tokenizer': 'tiktoken_gpt35',
                'acceptable_tokenizers': ['tiktoken_gpt4', 'gpt2'],
                'context_window': 16385,
                'training_data_cutoff': '2021-09',
                'use_cases': ['general', 'long_context', 'summarization'],
                'pricing_tier': 'standard'
            },
            
            # Anthropic Models  
            'claude-3-opus': {
                'family': 'anthropic',
                'optimal_tokenizer': 'claude_estimator',
                'acceptable_tokenizers': ['tiktoken_gpt4', 'gpt2'],
                'context_window': 200000,
                'training_data_cutoff': '2023-08',
                'use_cases': ['analysis', 'creative', 'coding', 'research'],
                'pricing_tier': 'premium'
            },
            'claude-3-sonnet': {
                'family': 'anthropic',
                'optimal_tokenizer': 'claude_estimator',
                'acceptable_tokenizers': ['tiktoken_gpt4', 'gpt2'],
                'context_window': 200000,
                'training_data_cutoff': '2023-08',
                'use_cases': ['general', 'analysis', 'creative'],
                'pricing_tier': 'standard'
            },
            'claude-3-haiku': {
                'family': 'anthropic',
                'optimal_tokenizer': 'claude_estimator',
                'acceptable_tokenizers': ['tiktoken_gpt4', 'gpt2'],
                'context_window': 200000,
                'training_data_cutoff': '2023-08',
                'use_cases': ['speed', 'simple_tasks', 'cost_effective'],
                'pricing_tier': 'budget'
            },
            'claude-3.5-sonnet': {
                'family': 'anthropic',
                'optimal_tokenizer': 'claude_estimator',
                'acceptable_tokenizers': ['tiktoken_gpt4', 'gpt2'],
                'context_window': 200000,
                'training_data_cutoff': '2024-04',
                'use_cases': ['general', 'coding', 'analysis', 'creative'],
                'pricing_tier': 'standard'
            },
            
            # BERT Family
            'bert-base-uncased': {
                'family': 'bert',
                'optimal_tokenizer': 'sentence_transformer',
                'acceptable_tokenizers': ['gpt2'],
                'context_window': 512,
                'training_data_cutoff': 'pre-2019',
                'use_cases': ['classification', 'embeddings', 'understanding'],
                'pricing_tier': 'free'
            },
            'bert-large-uncased': {
                'family': 'bert',
                'optimal_tokenizer': 'sentence_transformer',
                'acceptable_tokenizers': ['gpt2'],
                'context_window': 512,
                'training_data_cutoff': 'pre-2019',
                'use_cases': ['classification', 'embeddings', 'understanding'],
                'pricing_tier': 'free'
            },
            'roberta-base': {
                'family': 'bert',
                'optimal_tokenizer': 'sentence_transformer',
                'acceptable_tokenizers': ['gpt2'],
                'context_window': 512,
                'training_data_cutoff': 'pre-2019',
                'use_cases': ['classification', 'embeddings', 'nlp_tasks'],
                'pricing_tier': 'free'
            },
            'distilbert-base-uncased': {
                'family': 'bert',
                'optimal_tokenizer': 'sentence_transformer',
                'acceptable_tokenizers': ['gpt2'],
                'context_window': 512,
                'training_data_cutoff': 'pre-2019',
                'use_cases': ['fast_classification', 'embeddings', 'edge_deployment'],
                'pricing_tier': 'free'
            },
            
            # LLaMA Family
            'llama-2-7b': {
                'family': 'meta',
                'optimal_tokenizer': 'gpt2',
                'acceptable_tokenizers': ['tiktoken_gpt4', 'tiktoken_gpt35'],
                'context_window': 4096,
                'training_data_cutoff': '2023-07',
                'use_cases': ['open_source', 'local_deployment', 'research'],
                'pricing_tier': 'free'
            },
            'llama-2-13b': {
                'family': 'meta',
                'optimal_tokenizer': 'gpt2',
                'acceptable_tokenizers': ['tiktoken_gpt4', 'tiktoken_gpt35'],
                'context_window': 4096,
                'training_data_cutoff': '2023-07',
                'use_cases': ['open_source', 'local_deployment', 'research'],
                'pricing_tier': 'free'
            },
            'llama-2-70b': {
                'family': 'meta',
                'optimal_tokenizer': 'gpt2',
                'acceptable_tokenizers': ['tiktoken_gpt4', 'tiktoken_gpt35'],
                'context_window': 4096,
                'training_data_cutoff': '2023-07',
                'use_cases': ['open_source', 'high_quality', 'research'],
                'pricing_tier': 'free'
            },
            
            # Mistral Models
            'mistral-7b': {
                'family': 'mistral',
                'optimal_tokenizer': 'gpt2',
                'acceptable_tokenizers': ['tiktoken_gpt4', 'tiktoken_gpt35'],
                'context_window': 8192,
                'training_data_cutoff': '2023-09',
                'use_cases': ['open_source', 'multilingual', 'local_deployment'],
                'pricing_tier': 'free'
            },
            'mixtral-8x7b': {
                'family': 'mistral',
                'optimal_tokenizer': 'gpt2',
                'acceptable_tokenizers': ['tiktoken_gpt4', 'tiktoken_gpt35'],
                'context_window': 32768,
                'training_data_cutoff': '2023-09',
                'use_cases': ['open_source', 'high_performance', 'mixture_of_experts'],
                'pricing_tier': 'free'
            }
        }

    def _build_compatibility_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Build comprehensive model compatibility matrix"""
        return {
            'gpt2': {
                'info': TokenizerInfo(
                    name='gpt2',
                    display_name='GPT-2 (Free)',
                    description='Basic tokenizer - good for general estimation',
                    is_premium=False,
                    performance=PerformanceLevel.FAST,
                    accuracy=AccuracyLevel.ESTIMATED,
                    compatible_models=['GPT-2', 'General estimation'],
                    available=TRANSFORMERS_AVAILABLE,
                    error_message=None if TRANSFORMERS_AVAILABLE else "transformers library not installed"
                ),
                'models': ['gpt-2', 'gpt2-medium', 'gpt2-large', 'gpt2-xl'],
                'use_cases': ['General estimation', 'Development testing', 'Free tier usage']
            },
            
            'tiktoken_gpt4': {
                'info': TokenizerInfo(
                    name='tiktoken_gpt4',
                    display_name='🔒 GPT-4 (Premium)',
                    description='Exact tokenization for GPT-4 models',
                    is_premium=True,
                    performance=PerformanceLevel.FAST,
                    accuracy=AccuracyLevel.EXACT,
                    compatible_models=['GPT-4', 'GPT-4-turbo', 'GPT-4o'],
                    available=TIKTOKEN_AVAILABLE,
                    error_message=None if TIKTOKEN_AVAILABLE else "tiktoken library not installed"
                ),
                'models': ['gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-4-32k'],
                'use_cases': ['GPT-4 fine-tuning', 'Exact cost estimation', 'Production training']
            },
            
            'tiktoken_gpt35': {
                'info': TokenizerInfo(
                    name='tiktoken_gpt35',
                    display_name='🔒 GPT-3.5-turbo (Premium)',
                    description='Exact tokenization for GPT-3.5 models',
                    is_premium=True,
                    performance=PerformanceLevel.FAST,
                    accuracy=AccuracyLevel.EXACT,
                    compatible_models=['GPT-3.5-turbo', 'GPT-3.5-turbo-16k'],
                    available=TIKTOKEN_AVAILABLE,
                    error_message=None if TIKTOKEN_AVAILABLE else "tiktoken library not installed"
                ),
                'models': ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-instruct'],
                'use_cases': ['GPT-3.5 fine-tuning', 'Cost optimization', 'API usage planning']
            },
            
            'sentence_transformer': {
                'info': TokenizerInfo(
                    name='sentence_transformer',
                    display_name='🔒 BERT/RoBERTa (Premium)',
                    description='Tokenization for embedding and encoder models',
                    is_premium=True,
                    performance=PerformanceLevel.MEDIUM,
                    accuracy=AccuracyLevel.EXACT,
                    compatible_models=['BERT', 'RoBERTa', 'DistilBERT', 'SentenceTransformers'],
                    available=SENTENCE_TRANSFORMERS_AVAILABLE,
                    error_message=None if SENTENCE_TRANSFORMERS_AVAILABLE else "sentence-transformers library not installed"
                ),
                'models': ['bert-base-uncased', 'roberta-base', 'distilbert-base', 'all-MiniLM-L6-v2'],
                'use_cases': ['Embedding model training', 'Semantic search', 'Classification tasks']
            },
            
            'claude_estimator': {
                'info': TokenizerInfo(
                    name='claude_estimator',
                    display_name='🔒 Claude Estimator (Premium)',
                    description='Estimated tokenization for Claude models',
                    is_premium=True,
                    performance=PerformanceLevel.FAST,
                    accuracy=AccuracyLevel.ESTIMATED,
                    compatible_models=['Claude-3', 'Claude-3.5', 'Claude-2'],
                    available=True,  # Always available (uses word-based estimation)
                    error_message=None
                ),
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku', 'claude-3.5-sonnet'],
                'use_cases': ['Claude API usage estimation', 'Anthropic model preparation', 'Cost planning']
            }
        }

    def _initialize_tokenizers(self):
        """Initialize available tokenizers"""
        # GPT-2 (Free) - Always try to load
        if TRANSFORMERS_AVAILABLE:
            try:
                self._tokenizers['gpt2'] = AutoTokenizer.from_pretrained("gpt2")
                logging.info("GPT-2 tokenizer loaded successfully")
            except Exception as e:
                logging.error(f"Failed to load GPT-2 tokenizer: {e}")
                self._compatibility_matrix['gpt2']['info'].available = False
                self._compatibility_matrix['gpt2']['info'].error_message = str(e)

        # tiktoken tokenizers (Premium)
        if TIKTOKEN_AVAILABLE:
            try:
                self._tokenizers['tiktoken_gpt4'] = tiktoken.encoding_for_model("gpt-4")
                self._tokenizers['tiktoken_gpt35'] = tiktoken.encoding_for_model("gpt-3.5-turbo")
                logging.info("tiktoken tokenizers loaded successfully")
            except Exception as e:
                logging.error(f"Failed to load tiktoken tokenizers: {e}")
                for tokenizer_name in ['tiktoken_gpt4', 'tiktoken_gpt35']:
                    self._compatibility_matrix[tokenizer_name]['info'].available = False
                    self._compatibility_matrix[tokenizer_name]['info'].error_message = str(e)

        # Sentence transformer tokenizer (Premium)
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Use a lightweight model for tokenization
                model = SentenceTransformer('all-MiniLM-L6-v2')
                self._tokenizers['sentence_transformer'] = model.tokenizer
                logging.info("SentenceTransformer tokenizer loaded successfully")
            except Exception as e:
                logging.error(f"Failed to load SentenceTransformer tokenizer: {e}")
                self._compatibility_matrix['sentence_transformer']['info'].available = False
                self._compatibility_matrix['sentence_transformer']['info'].error_message = str(e)

    def get_available_tokenizers(self) -> List[TokenizerInfo]:
        """Get list of all tokenizers with their availability status"""
        return [info['info'] for info in self._compatibility_matrix.values()]

    def get_token_count(self, text: str, tokenizer_name: str = 'gpt2') -> Tuple[int, Dict[str, Any]]:
        """
        Get token count for text using specified tokenizer
        
        Returns:
            Tuple of (token_count, metadata)
            metadata includes: accuracy, performance, model_compatibility, error
        """
        if not text or not text.strip():
            return 0, {'accuracy': 'exact', 'performance': 'fast', 'error': None}

        tokenizer_info = self._compatibility_matrix.get(tokenizer_name, {}).get('info')
        if not tokenizer_info:
            # Fallback to GPT-2
            return self.get_token_count(text, 'gpt2')

        if not tokenizer_info.available:
            error_msg = f"Tokenizer {tokenizer_name} not available: {tokenizer_info.error_message}"
            logging.warning(error_msg)
            # Fallback to GPT-2 if available
            if tokenizer_name != 'gpt2':
                return self.get_token_count(text, 'gpt2')
            else:
                # Last resort: word-based estimation
                return self._word_based_estimate(text), {
                    'accuracy': 'estimated',
                    'performance': 'fast',
                    'error': error_msg,
                    'method': 'word_estimation'
                }

        try:
            if tokenizer_name == 'claude_estimator':
                count = self._claude_estimate(text)
            elif tokenizer_name.startswith('tiktoken_'):
                tokenizer = self._tokenizers[tokenizer_name]
                count = len(tokenizer.encode(text))
            elif tokenizer_name == 'sentence_transformer':
                tokenizer = self._tokenizers[tokenizer_name]
                tokens = tokenizer.encode(text, add_special_tokens=True)
                count = len(tokens)
            else:  # gpt2 and others
                tokenizer = self._tokenizers[tokenizer_name]
                count = len(tokenizer.encode(text, truncation=False))

            metadata = {
                'accuracy': tokenizer_info.accuracy.value,
                'performance': tokenizer_info.performance.value,
                'model_compatibility': tokenizer_info.compatible_models,
                'error': None
            }

            return count, metadata

        except Exception as e:
            error_msg = f"Error counting tokens with {tokenizer_name}: {str(e)}"
            logging.error(error_msg)
            
            # Fallback to word estimation
            count = self._word_based_estimate(text)
            metadata = {
                'accuracy': 'estimated',
                'performance': 'fast',
                'error': error_msg,
                'method': 'fallback_estimation'
            }
            return count, metadata

    def _claude_estimate(self, text: str) -> int:
        """Estimate Claude tokens using word-based approximation"""
        # Claude roughly: 1 token ≈ 0.75 words (more efficient than GPT)
        words = len(text.split())
        return int(words * 1.33)  # Slightly more conservative estimate

    def _word_based_estimate(self, text: str) -> int:
        """Fallback word-based token estimation"""
        # General estimation: 1 token ≈ 0.75 words
        words = len(text.split())
        return int(words * 1.33)

    def get_compatibility_info(self, tokenizer_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed compatibility information for a tokenizer"""
        return self._compatibility_matrix.get(tokenizer_name)

    def is_premium_tokenizer(self, tokenizer_name: str) -> bool:
        """Check if tokenizer requires premium license"""
        tokenizer_info = self._compatibility_matrix.get(tokenizer_name, {}).get('info')
        return tokenizer_info.is_premium if tokenizer_info else False

    def get_recommended_tokenizer(self, model_name: str) -> Optional[str]:
        """Get recommended tokenizer for a specific model"""
        model_name_lower = model_name.lower()
        
        # Check model database first
        model_info = None
        for db_model, info in self._model_database.items():
            if model_name_lower == db_model.lower():
                model_info = info
                break
        
        if model_info:
            optimal_tokenizer = model_info['optimal_tokenizer']
            if self._compatibility_matrix[optimal_tokenizer]['info'].available:
                return optimal_tokenizer
        
        # Fallback to pattern matching
        if 'gpt-4' in model_name_lower:
            return 'tiktoken_gpt4' if self._compatibility_matrix['tiktoken_gpt4']['info'].available else 'gpt2'
        elif 'gpt-3.5' in model_name_lower or 'gpt3.5' in model_name_lower:
            return 'tiktoken_gpt35' if self._compatibility_matrix['tiktoken_gpt35']['info'].available else 'gpt2'
        elif any(x in model_name_lower for x in ['claude', 'anthropic']):
            return 'claude_estimator'
        elif any(x in model_name_lower for x in ['bert', 'roberta', 'distil']):
            return 'sentence_transformer' if self._compatibility_matrix['sentence_transformer']['info'].available else 'gpt2'
        
        # Default fallback
        return 'gpt2'

    def check_model_compatibility(self, tokenizer_name: str, model_name: str) -> ModelCompatibility:
        """
        Check compatibility between a tokenizer and model with detailed analysis
        
        Args:
            tokenizer_name: Name of the tokenizer to check
            model_name: Name of the target model
            
        Returns:
            ModelCompatibility object with detailed compatibility info
        """
        model_name_lower = model_name.lower()
        model_info = None
        
        # Find model in database (exact match first, then partial)
        for db_model, info in self._model_database.items():
            if model_name_lower == db_model.lower():
                model_info = info
                break
        
        # If no exact match, try partial matching
        if not model_info:
            for db_model, info in self._model_database.items():
                if any(keyword in model_name_lower for keyword in db_model.lower().split('-')):
                    model_info = info
                    break
        
        if not model_info:
            # Unknown model - provide general guidance
            return self._assess_unknown_model(tokenizer_name, model_name)
        
        # Assess compatibility based on model info
        optimal_tokenizer = model_info['optimal_tokenizer']
        acceptable_tokenizers = model_info.get('acceptable_tokenizers', [])
        
        if tokenizer_name == optimal_tokenizer:
            return ModelCompatibility(
                model_name=model_name,
                compatibility=CompatibilityLevel.PERFECT,
                confidence=0.95,
                recommendation=f"Perfect match! {tokenizer_name} is the optimal tokenizer for {model_name}",
                warnings=[],
                icon="✅"
            )
        elif tokenizer_name in acceptable_tokenizers:
            return ModelCompatibility(
                model_name=model_name,
                compatibility=CompatibilityLevel.GOOD,
                confidence=0.80,
                recommendation=f"{tokenizer_name} works well with {model_name}, though {optimal_tokenizer} is optimal",
                warnings=[f"Consider using {optimal_tokenizer} for best accuracy"],
                icon="✅"
            )
        else:
            # Check if it's at least from the same family
            return self._assess_cross_family_compatibility(tokenizer_name, model_name, model_info)

    def _assess_unknown_model(self, tokenizer_name: str, model_name: str) -> ModelCompatibility:
        """Assess compatibility for unknown models using heuristics"""
        model_lower = model_name.lower()
        warnings = [f"Model '{model_name}' not in compatibility database"]
        
        # Heuristic matching based on model name patterns
        if any(keyword in model_lower for keyword in ['gpt-4', 'gpt4']):
            optimal = 'tiktoken_gpt4'
        elif any(keyword in model_lower for keyword in ['gpt-3.5', 'gpt3.5']):
            optimal = 'tiktoken_gpt35'
        elif any(keyword in model_lower for keyword in ['claude']):
            optimal = 'claude_estimator'
        elif any(keyword in model_lower for keyword in ['bert', 'roberta', 'distil']):
            optimal = 'sentence_transformer'
        else:
            optimal = 'gpt2'  # Safe fallback
        
        if tokenizer_name == optimal:
            compatibility = CompatibilityLevel.GOOD
            confidence = 0.60  # Lower confidence for unknown models
            recommendation = f"Based on model name, {tokenizer_name} appears to be a good choice for {model_name}"
            icon = "⚠️"
        else:
            compatibility = CompatibilityLevel.ACCEPTABLE
            confidence = 0.40
            recommendation = f"Consider using {optimal} instead of {tokenizer_name} for {model_name}"
            warnings.append(f"Recommended tokenizer: {optimal}")
            icon = "⚠️"
        
        return ModelCompatibility(
            model_name=model_name,
            compatibility=compatibility,
            confidence=confidence,
            recommendation=recommendation,
            warnings=warnings,
            icon=icon
        )

    def _assess_cross_family_compatibility(self, tokenizer_name: str, model_name: str, model_info: Dict) -> ModelCompatibility:
        """Assess compatibility across different model families"""
        optimal_tokenizer = model_info['optimal_tokenizer']
        model_family = model_info['family']
        
        # Define compatibility between families
        cross_family_matrix = {
            ('gpt2', 'openai'): CompatibilityLevel.ACCEPTABLE,
            ('gpt2', 'anthropic'): CompatibilityLevel.ACCEPTABLE,
            ('gpt2', 'bert'): CompatibilityLevel.POOR,
            ('gpt2', 'meta'): CompatibilityLevel.GOOD,
            ('gpt2', 'mistral'): CompatibilityLevel.GOOD,
            ('tiktoken_gpt4', 'anthropic'): CompatibilityLevel.ACCEPTABLE,
            ('tiktoken_gpt35', 'anthropic'): CompatibilityLevel.ACCEPTABLE,
            ('claude_estimator', 'openai'): CompatibilityLevel.ACCEPTABLE,
            ('sentence_transformer', 'openai'): CompatibilityLevel.POOR,
            ('sentence_transformer', 'anthropic'): CompatibilityLevel.POOR,
        }
        
        compatibility_key = (tokenizer_name, model_family)
        compatibility = cross_family_matrix.get(compatibility_key, CompatibilityLevel.POOR)
        
        warnings = []
        if compatibility in [CompatibilityLevel.POOR, CompatibilityLevel.ACCEPTABLE]:
            warnings.append(f"Suboptimal tokenizer choice - recommend {optimal_tokenizer}")
            
        if compatibility == CompatibilityLevel.POOR:
            icon = "❌"
            confidence = 0.30
            recommendation = f"Poor compatibility between {tokenizer_name} and {model_name}. Strongly recommend {optimal_tokenizer}"
        elif compatibility == CompatibilityLevel.ACCEPTABLE:
            icon = "⚠️"
            confidence = 0.60
            recommendation = f"Acceptable but not optimal. Consider upgrading to {optimal_tokenizer} for better accuracy"
        else:
            icon = "✅"
            confidence = 0.75
            recommendation = f"Good compatibility between {tokenizer_name} and {model_name}"
        
        return ModelCompatibility(
            model_name=model_name,
            compatibility=compatibility,
            confidence=confidence,
            recommendation=recommendation,
            warnings=warnings,
            icon=icon
        )

    def get_model_recommendations(self, target_use_case: str = None) -> List[Dict[str, Any]]:
        """Get model recommendations based on use case"""
        recommendations = []
        
        for model_name, model_info in self._model_database.items():
            if target_use_case and target_use_case not in model_info.get('use_cases', []):
                continue
                
            optimal_tokenizer = model_info['optimal_tokenizer']
            tokenizer_info = self._compatibility_matrix.get(optimal_tokenizer, {}).get('info')
            
            recommendation = {
                'model_name': model_name,
                'model_family': model_info['family'],
                'optimal_tokenizer': optimal_tokenizer,
                'tokenizer_display_name': tokenizer_info.display_name if tokenizer_info else optimal_tokenizer,
                'context_window': model_info.get('context_window', 'Unknown'),
                'use_cases': model_info.get('use_cases', []),
                'pricing_tier': model_info.get('pricing_tier', 'unknown'),
                'is_premium_tokenizer': tokenizer_info.is_premium if tokenizer_info else False
            }
            
            recommendations.append(recommendation)
        
        # Sort by pricing tier and context window
        tier_order = {'free': 0, 'budget': 1, 'standard': 2, 'premium': 3}
        recommendations.sort(key=lambda x: (tier_order.get(x['pricing_tier'], 4), -x.get('context_window', 0)))
        
        return recommendations

    def get_tokenizer_performance_comparison(self) -> Dict[str, Any]:
        """Get performance comparison of all available tokenizers"""
        comparison = {
            'tokenizers': [],
            'performance_summary': {},
            'accuracy_summary': {},
            'availability_summary': {}
        }
        
        for tokenizer_name, tokenizer_data in self._compatibility_matrix.items():
            info = tokenizer_data['info']
            
            tokenizer_comparison = {
                'name': info.name,
                'display_name': info.display_name,
                'performance': info.performance.value,
                'accuracy': info.accuracy.value,
                'is_premium': info.is_premium,
                'available': info.available,
                'compatible_model_count': len(tokenizer_data.get('models', [])),
                'use_cases': tokenizer_data.get('use_cases', [])
            }
            
            comparison['tokenizers'].append(tokenizer_comparison)
        
        # Calculate summaries
        available_tokenizers = [t for t in comparison['tokenizers'] if t['available']]
        
        comparison['performance_summary'] = {
            'fast': len([t for t in available_tokenizers if t['performance'] == 'fast']),
            'medium': len([t for t in available_tokenizers if t['performance'] == 'medium']),
            'slow': len([t for t in available_tokenizers if t['performance'] == 'slow'])
        }
        
        comparison['accuracy_summary'] = {
            'exact': len([t for t in available_tokenizers if t['accuracy'] == 'exact']),
            'estimated': len([t for t in available_tokenizers if t['accuracy'] == 'estimated'])
        }
        
        comparison['availability_summary'] = {
            'total': len(comparison['tokenizers']),
            'available': len(available_tokenizers),
            'premium': len([t for t in available_tokenizers if t['is_premium']]),
            'free': len([t for t in available_tokenizers if not t['is_premium']])
        }
        
        return comparison

    def get_compatibility_warnings(self, tokenizer_name: str, model_name: str = None) -> List[str]:
        """Get compatibility warnings for a tokenizer/model combination"""
        warnings = []
        
        tokenizer_info = self._compatibility_matrix.get(tokenizer_name, {}).get('info')
        if not tokenizer_info:
            warnings.append(f"Unknown tokenizer: {tokenizer_name}")
            return warnings
        
        if not tokenizer_info.available:
            warnings.append(f"Tokenizer {tokenizer_name} is not available: {tokenizer_info.error_message}")
        
        if model_name:
            compatibility = self.check_model_compatibility(tokenizer_name, model_name)
            if compatibility.compatibility in [CompatibilityLevel.POOR, CompatibilityLevel.ACCEPTABLE]:
                warnings.extend(compatibility.warnings)
        
        return warnings

    def get_tokenizer_stats(self) -> Dict[str, Any]:
        """Get summary statistics about available tokenizers"""
        total_tokenizers = len(self._compatibility_matrix)
        available_tokenizers = sum(1 for info in self._compatibility_matrix.values() if info['info'].available)
        premium_available = sum(1 for info in self._compatibility_matrix.values() 
                              if info['info'].is_premium and info['info'].available)
        
        return {
            'total_tokenizers': total_tokenizers,
            'available_tokenizers': available_tokenizers,
            'premium_available': premium_available,
            'free_available': available_tokenizers - premium_available,
            'libraries_status': {
                'tiktoken': TIKTOKEN_AVAILABLE,
                'sentence_transformers': SENTENCE_TRANSFORMERS_AVAILABLE,
                'transformers': TRANSFORMERS_AVAILABLE
            },
            'model_database_size': len(self._model_database),
            'supported_model_families': list(set(info['family'] for info in self._model_database.values()))
        }

    def validate_tokenizer_model_pair(self, tokenizer_name: str, model_name: str) -> Dict[str, Any]:
        """Comprehensive validation of tokenizer-model pairing"""
        result = {
            'is_valid': False,
            'compatibility_level': 'unknown',
            'confidence': 0.0,
            'warnings': [],
            'recommendations': [],
            'cost_impact': None,
            'accuracy_impact': None
        }
        
        # Check if tokenizer exists and is available
        tokenizer_info = self._compatibility_matrix.get(tokenizer_name, {}).get('info')
        if not tokenizer_info:
            result['warnings'].append(f"Unknown tokenizer: {tokenizer_name}")
            result['recommendations'].append("Use a supported tokenizer from the available list")
            return result
        
        if not tokenizer_info.available:
            result['warnings'].append(f"Tokenizer {tokenizer_name} is not available")
            result['recommendations'].append("Install required dependencies or use an available tokenizer")
            return result
        
        # Check model compatibility
        compatibility = self.check_model_compatibility(tokenizer_name, model_name)
        
        result.update({
            'is_valid': compatibility.compatibility != CompatibilityLevel.POOR,
            'compatibility_level': compatibility.compatibility.value,
            'confidence': compatibility.confidence,
            'warnings': compatibility.warnings,
            'icon': compatibility.icon
        })
        
        # Add specific recommendations based on compatibility
        if compatibility.compatibility == CompatibilityLevel.PERFECT:
            result['recommendations'].append("Excellent choice! This tokenizer is optimal for your model")
        elif compatibility.compatibility == CompatibilityLevel.GOOD:
            result['recommendations'].append(compatibility.recommendation)
        elif compatibility.compatibility == CompatibilityLevel.ACCEPTABLE:
            result['recommendations'].append(compatibility.recommendation)
            result['recommendations'].append("Consider upgrading to premium for exact tokenization")
        else:  # POOR
            result['recommendations'].append("This tokenizer is not recommended for your model")
            result['recommendations'].append(f"Use {self.get_recommended_tokenizer(model_name)} instead")
        
        # Assess cost and accuracy impact
        if tokenizer_info.accuracy == AccuracyLevel.EXACT:
            result['accuracy_impact'] = "High accuracy - exact token counting"
            if compatibility.compatibility == CompatibilityLevel.PERFECT:
                result['cost_impact'] = "Optimal cost estimation - no overestimation"
            else:
                result['cost_impact'] = "Good cost estimation with possible minor variance"
        else:
            result['accuracy_impact'] = "Estimated counting - may have variance"
            result['cost_impact'] = "Cost estimation may have 10-20% variance"
        
        return result

    def get_all_model_families(self) -> Dict[str, List[str]]:
        """Get all supported model families and their models"""
        families = {}
        for model_name, model_info in self._model_database.items():
            family = model_info['family']
            if family not in families:
                families[family] = []
            families[family].append(model_name)
        
        # Sort models within each family
        for family in families:
            families[family].sort()
        
        return families

    def search_compatible_models(self, tokenizer_name: str, 
                                compatibility_level: CompatibilityLevel = CompatibilityLevel.GOOD) -> List[Dict[str, Any]]:
        """Search for models compatible with a given tokenizer"""
        compatible_models = []
        
        for model_name in self._model_database.keys():
            compatibility = self.check_model_compatibility(tokenizer_name, model_name)
            
            # Check if compatibility meets minimum requirement
            level_order = {
                CompatibilityLevel.POOR: 0,
                CompatibilityLevel.ACCEPTABLE: 1,
                CompatibilityLevel.GOOD: 2,
                CompatibilityLevel.PERFECT: 3
            }
            
            if level_order[compatibility.compatibility] >= level_order[compatibility_level]:
                model_info = self._model_database[model_name]
                compatible_models.append({
                    'model_name': model_name,
                    'family': model_info['family'],
                    'compatibility': compatibility.compatibility.value,
                    'confidence': compatibility.confidence,
                    'icon': compatibility.icon,
                    'context_window': model_info.get('context_window', 'Unknown'),
                    'use_cases': model_info.get('use_cases', []),
                    'pricing_tier': model_info.get('pricing_tier', 'unknown')
                })
        
        # Sort by compatibility level (best first) then by context window
        compatible_models.sort(key=lambda x: (
            -level_order.get(CompatibilityLevel(x['compatibility']), 0),
            -x.get('context_window', 0) if isinstance(x.get('context_window'), int) else 0
        ))
        
        return compatible_models

    def generate_tokenizer_recommendation_report(self, target_model: str = None, 
                                               target_use_case: str = None) -> Dict[str, Any]:
        """Generate a comprehensive tokenizer recommendation report"""
        report = {
            'target_model': target_model,
            'target_use_case': target_use_case,
            'generated_at': str(datetime.now()),
            'recommendations': [],
            'alternatives': [],
            'warnings': [],
            'summary': {}
        }
        
        if target_model:
            # Model-specific recommendations
            recommended_tokenizer = self.get_recommended_tokenizer(target_model)
            compatibility = self.check_model_compatibility(recommended_tokenizer, target_model)
            
            tokenizer_info = self._compatibility_matrix.get(recommended_tokenizer, {}).get('info')
            
            primary_rec = {
                'tokenizer_name': recommended_tokenizer,
                'display_name': tokenizer_info.display_name if tokenizer_info else recommended_tokenizer,
                'compatibility': compatibility.compatibility.value,
                'confidence': compatibility.confidence,
                'icon': compatibility.icon,
                'reasoning': compatibility.recommendation,
                'is_primary': True
            }
            
            report['recommendations'].append(primary_rec)
            
            # Find alternatives
            alternative_tokenizers = [name for name in self._compatibility_matrix.keys() 
                                    if name != recommended_tokenizer]
            
            for alt_tokenizer in alternative_tokenizers:
                alt_compatibility = self.check_model_compatibility(alt_tokenizer, target_model)
                if alt_compatibility.compatibility in [CompatibilityLevel.GOOD, CompatibilityLevel.ACCEPTABLE]:
                    alt_info = self._compatibility_matrix.get(alt_tokenizer, {}).get('info')
                    
                    alternative = {
                        'tokenizer_name': alt_tokenizer,
                        'display_name': alt_info.display_name if alt_info else alt_tokenizer,
                        'compatibility': alt_compatibility.compatibility.value,
                        'confidence': alt_compatibility.confidence,
                        'icon': alt_compatibility.icon,
                        'reasoning': alt_compatibility.recommendation,
                        'is_primary': False
                    }
                    
                    report['alternatives'].append(alternative)
        
        else:
            # General recommendations based on use case
            model_recommendations = self.get_model_recommendations(target_use_case)
            
            # Group by tokenizer
            tokenizer_usage = {}
            for model_rec in model_recommendations:
                tokenizer = model_rec['optimal_tokenizer']
                if tokenizer not in tokenizer_usage:
                    tokenizer_usage[tokenizer] = []
                tokenizer_usage[tokenizer].append(model_rec['model_name'])
            
            # Convert to recommendations
            for tokenizer_name, models in tokenizer_usage.items():
                tokenizer_info = self._compatibility_matrix.get(tokenizer_name, {}).get('info')
                
                recommendation = {
                    'tokenizer_name': tokenizer_name,
                    'display_name': tokenizer_info.display_name if tokenizer_info else tokenizer_name,
                    'compatible_models': models,
                    'model_count': len(models),
                    'is_premium': tokenizer_info.is_premium if tokenizer_info else False,
                    'available': tokenizer_info.available if tokenizer_info else False
                }
                
                report['recommendations'].append(recommendation)
        
        # Add summary
        available_recs = [r for r in report['recommendations'] 
                         if self._compatibility_matrix.get(r['tokenizer_name'], {}).get('info', {}).available]
        premium_recs = [r for r in available_recs 
                       if self._compatibility_matrix.get(r['tokenizer_name'], {}).get('info', {}).is_premium]
        
        report['summary'] = {
            'total_recommendations': len(report['recommendations']),
            'available_recommendations': len(available_recs),
            'premium_recommendations': len(premium_recs),
            'free_recommendations': len(available_recs) - len(premium_recs)
        }
        
        # Add warnings for unavailable tokenizers
        for rec in report['recommendations']:
            tokenizer_info = self._compatibility_matrix.get(rec['tokenizer_name'], {}).get('info')
            if tokenizer_info and not tokenizer_info.available:
                report['warnings'].append(f"Recommended tokenizer {rec['tokenizer_name']} is not available: {tokenizer_info.error_message}")
        
        return report