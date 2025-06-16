# tokenizer_manager_hybrid.py - Progressive Loading with Graceful Fallbacks
"""
Hybrid TokenizerManager that prioritizes user experience:
- Core functionality works immediately (lightweight tokenizers)
- Premium features load progressively in background
- Graceful fallbacks prevent startup failures
- User gets immediate value, premium features enhance experience
"""

import logging
import threading
import time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import re

# Always available - basic tokenization
import string
import math

# Progressive imports with fallbacks
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.info("tiktoken not available - will use fallback tokenization")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.info("sentence-transformers not available - will use fallback tokenization")

try:
    from transformers import AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.info("transformers library not available - will use fallback tokenization")

class PerformanceLevel(Enum):
    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"

class AccuracyLevel(Enum):
    EXACT = "exact"
    ESTIMATED = "estimated"

class LoadingStatus(Enum):
    NOT_STARTED = "not_started"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"

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
    loading_status: LoadingStatus = LoadingStatus.NOT_STARTED
    error_message: Optional[str] = None

class HybridTokenizerManager:
    """
    Hybrid tokenizer manager with progressive loading and fallbacks
    
    Strategy:
    1. Start immediately with lightweight fallback tokenizers
    2. Load premium tokenizers in background thread
    3. Notify UI when premium features become available
    4. Never block application startup
    """
    
    def __init__(self):
        self._tokenizers = {}
        self._loading_callbacks = []
        self._tokenizer_definitions = self._build_tokenizer_definitions()
        
        # Initialize immediate fallback tokenizers
        self._initialize_fallback_tokenizers()
        
        # Start background loading of premium tokenizers
        self._start_background_loading()
        
        logging.info("HybridTokenizerManager initialized with immediate fallbacks")

    def _build_tokenizer_definitions(self) -> Dict[str, TokenizerInfo]:
        """Define all possible tokenizers with their metadata"""
        return {
            # Always available fallbacks
            'word_estimator': TokenizerInfo(
                name='word_estimator',
                display_name='Word Count Estimator',
                description='Fast word-based token estimation (GPT-style)',
                is_premium=False,
                performance=PerformanceLevel.FAST,
                accuracy=AccuracyLevel.ESTIMATED,
                compatible_models=['gpt-4', 'gpt-3.5', 'claude-3', 'general'],
                available=True,
                loading_status=LoadingStatus.LOADED
            ),
            
            'char_estimator': TokenizerInfo(
                name='char_estimator',
                display_name='Character Estimator',
                description='Character-based token estimation',
                is_premium=False,
                performance=PerformanceLevel.FAST,
                accuracy=AccuracyLevel.ESTIMATED,
                compatible_models=['general'],
                available=True,
                loading_status=LoadingStatus.LOADED
            ),
            
            # Premium tokenizers (loaded in background)
            'gpt2': TokenizerInfo(
                name='gpt2',
                display_name='🔒 GPT-2 (Exact)',
                description='Exact GPT-2/GPT-3/GPT-4 tokenization',
                is_premium=True,
                performance=PerformanceLevel.MEDIUM,
                accuracy=AccuracyLevel.EXACT,
                compatible_models=['gpt-2', 'gpt-3.5', 'gpt-4'],
                available=TRANSFORMERS_AVAILABLE,
                loading_status=LoadingStatus.NOT_STARTED if TRANSFORMERS_AVAILABLE else LoadingStatus.UNAVAILABLE
            ),
            
            'tiktoken_gpt4': TokenizerInfo(
                name='tiktoken_gpt4',
                display_name='🔒 GPT-4 (Native)',
                description='Official OpenAI GPT-4 tokenizer',
                is_premium=True,
                performance=PerformanceLevel.FAST,
                accuracy=AccuracyLevel.EXACT,
                compatible_models=['gpt-4', 'gpt-4-turbo'],
                available=TIKTOKEN_AVAILABLE,
                loading_status=LoadingStatus.NOT_STARTED if TIKTOKEN_AVAILABLE else LoadingStatus.UNAVAILABLE
            ),
            
            'tiktoken_gpt35': TokenizerInfo(
                name='tiktoken_gpt35',
                display_name='🔒 GPT-3.5 (Native)',
                description='Official OpenAI GPT-3.5 tokenizer',
                is_premium=True,
                performance=PerformanceLevel.FAST,
                accuracy=AccuracyLevel.EXACT,
                compatible_models=['gpt-3.5-turbo'],
                available=TIKTOKEN_AVAILABLE,
                loading_status=LoadingStatus.NOT_STARTED if TIKTOKEN_AVAILABLE else LoadingStatus.UNAVAILABLE
            ),
            
            'sentence_transformer': TokenizerInfo(
                name='sentence_transformer',
                display_name='🔒 BERT/Sentence Transformers',
                description='Sentence transformer tokenization',
                is_premium=True,
                performance=PerformanceLevel.SLOW,
                accuracy=AccuracyLevel.EXACT,
                compatible_models=['bert-base', 'all-MiniLM-L6-v2'],
                available=SENTENCE_TRANSFORMERS_AVAILABLE,
                loading_status=LoadingStatus.NOT_STARTED if SENTENCE_TRANSFORMERS_AVAILABLE else LoadingStatus.UNAVAILABLE
            ),
        }

    def _initialize_fallback_tokenizers(self):
        """Initialize immediate fallback tokenizers that never fail"""
        # Word-based estimator (GPT-style: ~1.3 tokens per word)
        self._tokenizers['word_estimator'] = self._create_word_estimator()
        
        # Character-based estimator (~4 chars per token)
        self._tokenizers['char_estimator'] = self._create_char_estimator()
        
        logging.info("Fallback tokenizers initialized - app ready to use immediately")

    def _create_word_estimator(self):
        """Create word-based token estimator"""
        def tokenize(text: str) -> int:
            if not text:
                return 0
            # GPT tokenizers average ~1.3 tokens per word
            word_count = len(text.split())
            return max(1, int(word_count * 1.3))
        
        return tokenize

    def _create_char_estimator(self):
        """Create character-based token estimator"""
        def tokenize(text: str) -> int:
            if not text:
                return 0
            # Most tokenizers average ~4 characters per token
            return max(1, int(len(text) / 4))
        
        return tokenize

    def _start_background_loading(self):
        """Start background thread to load premium tokenizers"""
        def load_premium_tokenizers():
            """Background function to load premium tokenizers"""
            
            # Load GPT-2 tokenizer
            if TRANSFORMERS_AVAILABLE and 'gpt2' in self._tokenizer_definitions:
                self._load_gpt2_tokenizer()
            
            # Load tiktoken tokenizers
            if TIKTOKEN_AVAILABLE:
                self._load_tiktoken_tokenizers()
            
            # Load sentence transformers
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self._load_sentence_transformer()
            
            logging.info("Background tokenizer loading completed")
        
        # Start background thread
        loading_thread = threading.Thread(target=load_premium_tokenizers, daemon=True)
        loading_thread.start()

    def _load_gpt2_tokenizer(self):
        """Load GPT-2 tokenizer with error handling"""
        try:
            self._tokenizer_definitions['gpt2'].loading_status = LoadingStatus.LOADING
            self._notify_loading_status('gpt2', 'loading')
            
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained("gpt2")
            
            def gpt2_tokenize(text: str) -> int:
                if not text:
                    return 0
                return len(tokenizer.encode(text))
            
            self._tokenizers['gpt2'] = gpt2_tokenize
            self._tokenizer_definitions['gpt2'].loading_status = LoadingStatus.LOADED
            self._notify_loading_status('gpt2', 'loaded')
            
            logging.info("GPT-2 tokenizer loaded successfully in background")
            
        except Exception as e:
            self._tokenizer_definitions['gpt2'].loading_status = LoadingStatus.FAILED
            self._tokenizer_definitions['gpt2'].error_message = str(e)
            self._notify_loading_status('gpt2', 'failed')
            logging.warning(f"Failed to load GPT-2 tokenizer: {e}")

    def _load_tiktoken_tokenizers(self):
        """Load tiktoken tokenizers with error handling"""
        for model_name, tokenizer_name in [('gpt-4', 'tiktoken_gpt4'), ('gpt-3.5-turbo', 'tiktoken_gpt35')]:
            try:
                self._tokenizer_definitions[tokenizer_name].loading_status = LoadingStatus.LOADING
                self._notify_loading_status(tokenizer_name, 'loading')
                
                import tiktoken
                encoding = tiktoken.encoding_for_model(model_name)
                
                def tiktoken_tokenize(text: str, enc=encoding) -> int:
                    if not text:
                        return 0
                    return len(enc.encode(text))
                
                self._tokenizers[tokenizer_name] = tiktoken_tokenize
                self._tokenizer_definitions[tokenizer_name].loading_status = LoadingStatus.LOADED
                self._notify_loading_status(tokenizer_name, 'loaded')
                
                logging.info(f"{tokenizer_name} loaded successfully in background")
                
            except Exception as e:
                self._tokenizer_definitions[tokenizer_name].loading_status = LoadingStatus.FAILED
                self._tokenizer_definitions[tokenizer_name].error_message = str(e)
                self._notify_loading_status(tokenizer_name, 'failed')
                logging.warning(f"Failed to load {tokenizer_name}: {e}")

    def _load_sentence_transformer(self):
        """Load sentence transformer with error handling"""
        try:
            self._tokenizer_definitions['sentence_transformer'].loading_status = LoadingStatus.LOADING
            self._notify_loading_status('sentence_transformer', 'loading')
            
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            def st_tokenize(text: str) -> int:
                if not text:
                    return 0
                # Sentence transformers use BERT-style tokenization
                tokens = model.tokenize([text])
                return len(tokens[0]) if tokens else 0
            
            self._tokenizers['sentence_transformer'] = st_tokenize
            self._tokenizer_definitions['sentence_transformer'].loading_status = LoadingStatus.LOADED
            self._notify_loading_status('sentence_transformer', 'loaded')
            
            logging.info("Sentence transformer loaded successfully in background")
            
        except Exception as e:
            self._tokenizer_definitions['sentence_transformer'].loading_status = LoadingStatus.FAILED
            self._tokenizer_definitions['sentence_transformer'].error_message = str(e)
            self._notify_loading_status('sentence_transformer', 'failed')
            logging.warning(f"Failed to load sentence transformer: {e}")

    def _notify_loading_status(self, tokenizer_name: str, status: str):
        """Notify registered callbacks about loading status changes"""
        for callback in self._loading_callbacks:
            try:
                callback(tokenizer_name, status)
            except Exception as e:
                logging.warning(f"Callback notification failed: {e}")

    def register_loading_callback(self, callback):
        """Register callback for tokenizer loading status updates"""
        self._loading_callbacks.append(callback)

    def get_token_count(self, text: str, tokenizer_name: str = 'word_estimator') -> Tuple[int, Dict[str, Any]]:
        """
        Get token count using specified tokenizer with automatic fallback
        
        Args:
            text: Text to tokenize
            tokenizer_name: Preferred tokenizer name
            
        Returns:
            Tuple of (token_count, metadata)
        """
        if not text:
            return 0, {'method': 'empty_text', 'tokenizer': tokenizer_name}
        
        # Check if requested tokenizer is available
        if tokenizer_name in self._tokenizers:
            tokenizer_info = self._tokenizer_definitions.get(tokenizer_name)
            
            try:
                count = self._tokenizers[tokenizer_name](text)
                metadata = {
                    'method': tokenizer_name,
                    'accuracy': tokenizer_info.accuracy.value if tokenizer_info else 'estimated',
                    'is_premium': tokenizer_info.is_premium if tokenizer_info else False,
                    'loading_status': tokenizer_info.loading_status.value if tokenizer_info else 'loaded'
                }
                return count, metadata
                
            except Exception as e:
                logging.warning(f"Tokenizer {tokenizer_name} failed: {e}")
                # Fall through to fallback
        
        # Fallback to word estimator
        count = self._tokenizers['word_estimator'](text)
        metadata = {
            'method': 'word_estimator',
            'accuracy': 'estimated',
            'is_premium': False,
            'fallback_used': True,
            'requested_tokenizer': tokenizer_name
        }
        
        return count, metadata

    def get_available_tokenizers(self) -> List[Dict[str, Any]]:
        """Get list of all tokenizers with their current status"""
        tokenizers = []
        
        for name, info in self._tokenizer_definitions.items():
            tokenizers.append({
                'name': info.name,
                'display_name': info.display_name,
                'description': info.description,
                'is_premium': info.is_premium,
                'performance': info.performance.value,
                'accuracy': info.accuracy.value,
                'compatible_models': info.compatible_models,
                'available': info.available,
                'loading_status': info.loading_status.value,
                'has_access': True,  # Access control handled elsewhere
                'error_message': info.error_message
            })
        
        return tokenizers

    def get_recommended_tokenizer(self, target_model: str = None) -> str:
        """Get best available tokenizer for target model"""
        if target_model:
            # Find exact match first
            for name, info in self._tokenizer_definitions.items():
                if (target_model.lower() in [m.lower() for m in info.compatible_models] and 
                    info.loading_status == LoadingStatus.LOADED):
                    return name
        
        # Return best loaded premium tokenizer
        for name, info in self._tokenizer_definitions.items():
            if (info.is_premium and 
                info.loading_status == LoadingStatus.LOADED and 
                info.accuracy == AccuracyLevel.EXACT):
                return name
        
        # Fallback to word estimator
        return 'word_estimator'

    def get_loading_progress(self) -> Dict[str, Any]:
        """Get current loading progress for UI display"""
        total_premium = sum(1 for info in self._tokenizer_definitions.values() if info.is_premium and info.available)
        loaded_premium = sum(1 for info in self._tokenizer_definitions.values() 
                           if info.is_premium and info.loading_status == LoadingStatus.LOADED)
        loading_premium = sum(1 for info in self._tokenizer_definitions.values() 
                            if info.is_premium and info.loading_status == LoadingStatus.LOADING)
        
        return {
            'total_premium_tokenizers': total_premium,
            'loaded_premium_tokenizers': loaded_premium,
            'loading_premium_tokenizers': loading_premium,
            'loading_complete': loading_premium == 0 and loaded_premium > 0,
            'loading_progress_percent': (loaded_premium / total_premium * 100) if total_premium > 0 else 100
        }

# Backward compatibility alias
TokenizerManager = HybridTokenizerManager