# core/tokenizer_manager.py
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Standard library imports
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

class TokenizerManager:
    def __init__(self):
        self._tokenizers = {}
        self._compatibility_matrix = self._build_compatibility_matrix()
        self._initialize_tokenizers()

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
        
        # Direct model matching
        for tokenizer_name, info in self._compatibility_matrix.items():
            if any(model_name_lower in model.lower() for model in info['models']):
                if info['info'].available:
                    return tokenizer_name
        
        # Partial matching
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
            }
        }