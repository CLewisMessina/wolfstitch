# controller_COMPLETE.py - Full Integration with Existing Systems + Hybrid Features
import os  # FIXED: Missing import that caused NameError
import logging
import threading
import time
from typing import List, Dict, Any, Tuple, Optional
from processing.extract import load_file
from processing.clean import clean_text
from processing.splitter import split_text  # Keep existing basic splitter

# Import hybrid tokenizer manager
from core.tokenizer_manager import HybridTokenizerManager

# Import premium systems with fallbacks
try:
    from core.license_manager import LicenseManager, FeatureTier
    LICENSE_MANAGER_AVAILABLE = True
except ImportError:
    LICENSE_MANAGER_AVAILABLE = False
    logging.info("License manager not available - running in basic mode")

try:
    from core.cost_calculator import EnhancedCostCalculator, calculate_training_cost
    COST_CALCULATOR_AVAILABLE = True
except ImportError:
    COST_CALCULATOR_AVAILABLE = False
    logging.info("Cost calculator not available - cost analysis disabled")

class ProcessingController:
    """
    Complete controller with full compatibility for existing systems + hybrid features
    
    This controller maintains 100% compatibility with existing cost dialogs and UI
    while adding progressive hybrid tokenizer loading capabilities.
    """
    
    def __init__(self):
        # Always available - hybrid tokenizer with immediate fallbacks
        self.tokenizer_manager = HybridTokenizerManager()
        
        # Progressive loading status
        self._premium_features_loading = True
        self._premium_features_loaded = False
        self._loading_callbacks = []
        
        # Initialize license manager with fallback
        self._initialize_license_manager()
        
        # Initialize cost calculator with fallback
        self._initialize_cost_calculator()
        
        # Register for tokenizer loading updates
        if hasattr(self.tokenizer_manager, 'register_loading_callback'):
            self.tokenizer_manager.register_loading_callback(self._on_tokenizer_loaded)
        
        # Start background premium feature loading
        self._start_premium_loading()
        
        logging.info("ProcessingController initialized - core functionality ready immediately")

    def _initialize_license_manager(self):
        """Initialize license manager with graceful fallback"""
        if LICENSE_MANAGER_AVAILABLE:
            try:
                self.license_manager = LicenseManager()
                self._license_manager_available = True
                logging.info("License manager initialized successfully")
            except Exception as e:
                logging.warning(f"License manager initialization failed: {e}")
                self.license_manager = None
                self._license_manager_available = False
        else:
            self.license_manager = None
            self._license_manager_available = False

    def _initialize_cost_calculator(self):
        """Initialize cost calculator with graceful fallback"""
        if COST_CALCULATOR_AVAILABLE:
            try:
                self.cost_calculator = EnhancedCostCalculator()
                self._cost_calculator_available = True
                logging.info("Enhanced Cost Calculator initialized successfully")
            except Exception as e:
                logging.warning(f"Cost calculator initialization failed: {e}")
                self.cost_calculator = None
                self._cost_calculator_available = False
        else:
            self.cost_calculator = None
            self._cost_calculator_available = False

    def _start_premium_loading(self):
        """Start background loading of premium features"""
        def load_premium_features():
            """Background function to enhance premium features"""
            time.sleep(1)  # Small delay to let app start
            
            # Add cost analysis feature to license manager if available
            if self._license_manager_available:
                self._add_cost_analysis_feature()
            
            # Notify completion
            self._premium_features_loading = False
            self._premium_features_loaded = True
            self._notify_premium_loaded()
            
            logging.info("Premium features loading completed")
        
        # Start background thread
        loading_thread = threading.Thread(target=load_premium_features, daemon=True)
        loading_thread.start()

    def _add_cost_analysis_feature(self):
        """Add cost analysis feature to license manager feature definitions"""
        if not self._license_manager_available:
            return
            
        try:
            # Add the feature to the existing feature definitions
            if hasattr(self.license_manager, '_feature_definitions'):
                self.license_manager._feature_definitions['advanced_cost_analysis'] = {
                    'tier': FeatureTier.PREMIUM,
                    'description': 'Comprehensive AI training cost analysis and optimization',
                    'includes': [
                        'Multi-provider cost comparison (Lambda Labs, Vast.ai, RunPod)',
                        'ROI analysis and break-even calculations',
                        'Cost optimization recommendations',
                        'Training approach comparison matrix (15+ approaches)',
                        'Hardware requirement analysis',
                        'Real-time cloud pricing integration',
                        'Export-ready cost reports'
                    ]
                }
                logging.info("Added advanced_cost_analysis feature to license manager")
        except Exception as e:
            logging.warning(f"Could not add cost analysis feature to license manager: {e}")

    def _on_tokenizer_loaded(self, tokenizer_name: str, status: str):
        """Handle tokenizer loading status updates"""
        logging.info(f"Tokenizer {tokenizer_name} status: {status}")
        
        # Notify UI about tokenizer availability changes
        for callback in self._loading_callbacks:
            try:
                callback('tokenizer', tokenizer_name, status)
            except Exception as e:
                logging.warning(f"Loading callback failed: {e}")

    def _notify_premium_loaded(self):
        """Notify callbacks that premium features are ready"""
        for callback in self._loading_callbacks:
            try:
                callback('premium_features', 'all', 'loaded')
            except Exception as e:
                logging.warning(f"Premium loading callback failed: {e}")

    def register_loading_callback(self, callback):
        """Register callback for loading status updates"""
        self._loading_callbacks.append(callback)

    def get_loading_status(self) -> Dict[str, Any]:
        """Get comprehensive loading status for UI display"""
        if hasattr(self.tokenizer_manager, 'get_loading_progress'):
            tokenizer_progress = self.tokenizer_manager.get_loading_progress()
        else:
            tokenizer_progress = {'loading_progress_percent': 100, 'loading_complete': True, 'loading_premium_tokenizers': 0}
        
        return {
            'core_ready': True,  # Always ready immediately
            'tokenizers': tokenizer_progress,
            'premium_features': {
                'loading': self._premium_features_loading,
                'loaded': self._premium_features_loaded,
                'license_manager_available': self._license_manager_available,
                'cost_calculator_available': self._cost_calculator_available
            },
            'overall_progress': {
                'immediate_functionality': 100,
                'premium_tokenizers': tokenizer_progress.get('loading_progress_percent', 0),
                'premium_features': 100 if self._premium_features_loaded else (50 if not self._premium_features_loading else 0)
            }
        }

    # ==================================================================================
    # CORE PROCESSING METHODS (Always Available)
    # ==================================================================================

    def process_book(self, path: str, clean_opts: Dict[str, Any], split_method: str, 
                    delimiter: str = None, tokenizer_name: str = 'word_estimator', 
                    use_smart_splitting: bool = None, max_tokens: int = 512) -> List[str]:
        """
        Enhanced book processing with hybrid tokenizer support
        """
        # Validate tokenizer access with license check
        actual_tokenizer = self._validate_tokenizer_access(tokenizer_name)
        
        # Load and clean text
        raw = load_file(path)
        file_extension = os.path.splitext(path)[1].lower()  # FIXED: Now has proper import
        cleaned = clean_text(raw, file_extension=file_extension, **clean_opts)
        
        # Use basic splitting for now (smart splitting will be added later)
        chunks = split_text(cleaned, split_method, delimiter)
        
        logging.info(f"Processed {path}: {len(chunks)} chunks created using basic {split_method} splitting with {actual_tokenizer}")
        return chunks

    def _validate_tokenizer_access(self, tokenizer_name: str) -> str:
        """Validate tokenizer access with license and availability checks"""
        # Check license access if license manager is available
        if self._license_manager_available and self.license_manager:
            try:
                if not self.license_manager.check_tokenizer_access(tokenizer_name):
                    logging.info(f"Access denied to tokenizer {tokenizer_name}, falling back to word_estimator")
                    return 'word_estimator'
            except Exception as e:
                logging.warning(f"License check failed: {e}")
        
        # Check if tokenizer is actually available
        available_tokenizers = self.get_available_tokenizers()
        tokenizer_info = next((t for t in available_tokenizers if t['name'] == tokenizer_name), None)
        
        if not tokenizer_info or tokenizer_info.get('loading_status') != 'loaded':
            logging.info(f"Tokenizer {tokenizer_name} not ready, using fallback")
            return 'word_estimator'
        
        return tokenizer_name

    def get_smart_splitting_status(self) -> Dict[str, Any]:
        """Get smart splitting status for UI info display"""
        has_smart_access = False
        if self._license_manager_available and self.license_manager:
            try:
                has_smart_access = self.license_manager.check_feature_access('smart_chunking')
            except:
                pass
        
        return {
            'available': False,  # Disabled for now
            'description': 'Smart chunking will be available in a future update',
            'upgrade_message': 'Coming soon - automatic token optimization for premium users',
            'license_check_available': self._license_manager_available
        }

    # ==================================================================================
    # ENHANCED ANALYTICS WITH PROGRESSIVE FEATURES
    # ==================================================================================

    def analyze_chunks(self, chunks: List[str], tokenizer_name: str = 'word_estimator', 
                      token_limit: int = 512) -> Dict[str, Any]:
        """
        Enhanced analyze_chunks with progressive feature integration
        """
        if not chunks:
            return {
                'total_chunks': 0,
                'total_tokens': 0,
                'avg_tokens': 0,
                'min_tokens': 0,
                'max_tokens': 0,
                'over_limit': 0,
                'efficiency_score': 0
            }

        # Validate and use appropriate tokenizer
        actual_tokenizer = self._validate_tokenizer_access(tokenizer_name)
        
        # Check access to advanced analytics
        has_advanced_analytics = False
        has_cost_analysis = False
        
        if self._license_manager_available and self.license_manager:
            try:
                has_advanced_analytics = self.license_manager.check_feature_access('advanced_analytics')
                has_cost_analysis = self.license_manager.check_feature_access('advanced_cost_analysis')
            except:
                pass
        
        # Analyze chunks with actual tokenizer
        token_counts = []
        over_limit_count = 0
        
        for chunk in chunks:
            count, metadata = self.get_token_count(chunk, actual_tokenizer)
            token_counts.append(count)
            if count > token_limit:
                over_limit_count += 1

        total_tokens = sum(token_counts)
        avg_tokens = total_tokens / len(token_counts) if token_counts else 0
        min_tokens = min(token_counts) if token_counts else 0
        max_tokens = max(token_counts) if token_counts else 0

        # Basic analysis (available to all users)
        analysis = {
            'total_chunks': len(chunks),
            'total_tokens': total_tokens,
            'avg_tokens': round(avg_tokens, 1),
            'min_tokens': min_tokens,
            'max_tokens': max_tokens,
            'over_limit': over_limit_count,
            'over_limit_percentage': round((over_limit_count / len(chunks)) * 100, 1) if chunks else 0,
            'tokenizer_used': actual_tokenizer,
            'token_limit': token_limit,
            'tokenizer_fallback_used': actual_tokenizer != tokenizer_name
        }

        # Progressive premium analytics
        if has_advanced_analytics and self._premium_features_loaded:
            # Calculate efficiency score (how close to optimal token usage)
            optimal_tokens = token_limit * 0.9  # 90% of limit is optimal
            efficiency_scores = []
            for count in token_counts:
                if count <= optimal_tokens:
                    efficiency_scores.append(1.0)  # Perfect
                elif count <= token_limit:
                    efficiency_scores.append(0.7)  # Good
                else:
                    efficiency_scores.append(0.3)  # Poor
            
            efficiency_score = sum(efficiency_scores) / len(efficiency_scores) if efficiency_scores else 0
            
            # Token distribution analysis
            token_ranges = {
                'under_50': sum(1 for c in token_counts if c < 50),
                '50_200': sum(1 for c in token_counts if 50 <= c < 200),
                '200_400': sum(1 for c in token_counts if 200 <= c < 400),
                '400_512': sum(1 for c in token_counts if 400 <= c <= token_limit),
                'over_limit': over_limit_count
            }
            
            # Cost estimation (premium feature)
            cost_estimates = self._calculate_cost_estimates(total_tokens, actual_tokenizer)
            
            analysis.update({
                'efficiency_score': round(efficiency_score * 100, 1),
                'token_distribution': token_ranges,
                'cost_estimates': cost_estimates,
                'recommendations': self._generate_recommendations(analysis, efficiency_score),
                'advanced_analytics': True
            })
        else:
            upgrade_message = "Upgrade to Premium for advanced analytics"
            if self._license_manager_available and self.license_manager:
                try:
                    upgrade_message = self.license_manager.get_upgrade_message('advanced_analytics')
                except:
                    pass
            
            analysis.update({
                'advanced_analytics': False,
                'upgrade_message': upgrade_message,
                'features_loading': self._premium_features_loading
            })

        # Add cost preview for all users
        cost_preview = self._get_cost_preview(total_tokens, actual_tokenizer, has_cost_analysis)
        analysis['cost_preview'] = cost_preview

        return analysis

    def analyze_chunks_with_costs(self, chunks: List[str], tokenizer_name: str = 'word_estimator',
                                 token_limit: int = 512, target_models: Optional[List[str]] = None,
                                 api_usage_monthly: int = 100000) -> Dict[str, Any]:
        """
        Enhanced analysis method with comprehensive cost analysis
        COMPLETE COMPATIBILITY with existing cost dialogs
        """
        # Start with standard analysis
        analysis = self.analyze_chunks(chunks, tokenizer_name, token_limit)
        
        # Check if user has access to advanced cost analysis
        has_cost_analysis = False
        if self._license_manager_available and self.license_manager:
            try:
                has_cost_analysis = self.license_manager.check_feature_access('advanced_cost_analysis')
            except:
                pass
        
        if not has_cost_analysis:
            analysis['cost_analysis'] = {
                'available': False,
                'upgrade_message': 'Upgrade to Premium for advanced cost analysis',
                'preview': self._get_cost_preview(analysis['total_tokens'], tokenizer_name, False)
            }
            return analysis
        
        # Perform comprehensive cost analysis for premium users
        if not self._cost_calculator_available or not self._premium_features_loaded:
            analysis['cost_analysis'] = {
                'available': False,
                'error': 'Cost calculator not available or still loading',
                'basic_estimate': self._get_basic_cost_estimate(analysis['total_tokens']),
                'loading': self._premium_features_loading
            }
            return analysis
        
        try:
            # Use target models or default recommended models
            if not target_models:
                target_models = self._get_recommended_models_for_analysis(analysis['total_tokens'])
            
            # Perform cost analysis for each target model
            cost_analyses = {}
            for model_name in target_models:
                try:
                    cost_result = self.cost_calculator.calculate_comprehensive_costs(
                        dataset_tokens=analysis['total_tokens'],
                        target_model=model_name,
                        api_usage_monthly=api_usage_monthly
                    )
                    cost_analyses[model_name] = cost_result
                except Exception as e:
                    logging.warning(f"Cost analysis failed for {model_name}: {e}")
                    cost_analyses[model_name] = {
                        'error': str(e),
                        'model_name': model_name
                    }
            
            # Add comprehensive cost analysis to results
            analysis['cost_analysis'] = {
                'available': True,
                'models_analyzed': list(cost_analyses.keys()),
                'detailed_results': cost_analyses,
                'summary': self._generate_cost_summary(cost_analyses),
                'recommendations': self._generate_cost_recommendations(cost_analyses, analysis)
            }
            
        except Exception as e:
            logging.error(f"Comprehensive cost analysis failed: {e}")
            analysis['cost_analysis'] = {
                'available': False,
                'error': str(e),
                'fallback_estimate': self._get_basic_cost_estimate(analysis['total_tokens'])
            }
        
        return analysis

    # ==================================================================================
    # HELPER METHODS FOR COST ANALYSIS (Required by existing dialogs)
    # ==================================================================================

    def _get_recommended_models_for_analysis(self, total_tokens: int) -> List[str]:
        """Get recommended models based on dataset size"""
        if total_tokens < 50000:
            return ["llama-2-7b", "mistral-7b"]
        elif total_tokens < 200000:
            return ["llama-2-7b", "llama-2-13b", "claude-3-haiku"]
        else:
            return ["llama-2-13b", "llama-2-70b", "claude-3-sonnet"]

    def _generate_cost_summary(self, cost_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of cost analyses across models"""
        if not cost_analyses:
            return {'error': 'No cost analyses available'}
        
        summaries = []
        for model_name, analysis in cost_analyses.items():
            if 'error' in analysis:
                continue
                
            cost_estimates = analysis.get('cost_estimates', [])
            if cost_estimates:
                best_approach = min(cost_estimates, key=lambda x: x['total_cost_usd'])
                summaries.append({
                    'model': model_name,
                    'best_approach': best_approach['approach_name'],
                    'cost': best_approach['total_cost_usd'],
                    'hours': best_approach['training_hours']
                })
        
        if not summaries:
            return {'error': 'No valid cost estimates generated'}
        
        # Find overall best option
        best_overall = min(summaries, key=lambda x: x['cost'])
        
        return {
            'models_compared': len(summaries),
            'best_overall': best_overall,
            'cost_range': {
                'min': min(s['cost'] for s in summaries),
                'max': max(s['cost'] for s in summaries)
            },
            'all_options': summaries
        }

    def _generate_cost_recommendations(self, cost_analyses: Dict[str, Any], 
                                     chunk_analysis: Dict[str, Any]) -> List[str]:
        """Generate cost-specific recommendations"""
        recommendations = []
        
        # Dataset size recommendations
        total_tokens = chunk_analysis.get('total_tokens', 0)
        if total_tokens < 10000:
            recommendations.append("Small dataset detected - consider data augmentation for better model quality")
        elif total_tokens > 1000000:
            recommendations.append("Large dataset provides excellent training opportunities")
        
        # Efficiency recommendations
        efficiency = chunk_analysis.get('efficiency_score', 0)
        if efficiency < 70:
            recommendations.append("Improve chunk efficiency to reduce training costs")
        
        # Cost-specific recommendations from analyses
        for model_name, analysis in cost_analyses.items():
            if 'error' in analysis:
                continue
                
            model_recommendations = analysis.get('recommendations', [])
            recommendations.extend(model_recommendations[:2])  # Add top 2 per model
        
        return recommendations[:5]  # Limit to top 5

    def _get_cost_preview(self, total_tokens: int, tokenizer_name: str, has_full_access: bool) -> Dict[str, Any]:
        """Generate cost preview with progressive enhancement"""
        if has_full_access and self._cost_calculator_available and self._premium_features_loaded:
            try:
                # Quick cost calculation for premium users
                result = self.cost_calculator.calculate_comprehensive_costs(
                    dataset_tokens=total_tokens,
                    target_model="llama-2-7b"  # Use as reference
                )
                
                cost_estimates = result.get('cost_estimates', [])
                if cost_estimates:
                    best_approach = min(cost_estimates, key=lambda x: x['total_cost_usd'])
                    return {
                        'available': True,
                        'best_approach': best_approach['approach_name'],
                        'estimated_cost': best_approach['total_cost_usd'],
                        'training_hours': best_approach['training_hours'],
                        'confidence': 'high'
                    }
            except Exception as e:
                logging.warning(f"Failed to generate cost preview: {e}")
        
        # Basic cost preview for free users or fallback
        basic_estimate = self._get_basic_cost_estimate(total_tokens)
        return {
            'available': False,
            'estimated_cost_range': f"${basic_estimate['min_cost']:.0f} - ${basic_estimate['max_cost']:.0f}",
            'accuracy': '±50%',
            'upgrade_message': 'Upgrade to Premium for exact cost analysis',
            'confidence': 'low',
            'features_loading': self._premium_features_loading
        }

    def _get_basic_cost_estimate(self, total_tokens: int) -> Dict[str, Any]:
        """Generate basic cost estimate for all users"""
        # Rough estimates based on common approaches
        local_estimate = total_tokens * 0.0003
        api_estimate_low = total_tokens * 0.008
        api_estimate_high = total_tokens * 0.030
        
        return {
            'total_tokens': total_tokens,
            'local_training': local_estimate,
            'api_low': api_estimate_low,
            'api_high': api_estimate_high,
            'min_cost': local_estimate,
            'max_cost': api_estimate_high,
            'note': 'Rough estimates only - upgrade for precise calculations'
        }

    def _calculate_cost_estimates(self, total_tokens: int, tokenizer_name: str) -> Dict[str, Any]:
        """Calculate training cost estimates (progressive feature)"""
        cost_per_1k_tokens = {
            'word_estimator': 0.008,
            'char_estimator': 0.008,
            'gpt2': 0.008,
            'tiktoken_gpt4': 0.03,
            'tiktoken_gpt35': 0.002,
            'sentence_transformer': 0.005,
        }
        
        base_cost = cost_per_1k_tokens.get(tokenizer_name, 0.01)
        total_cost = (total_tokens / 1000) * base_cost
        
        return {
            'tokenizer': tokenizer_name,
            'total_tokens': total_tokens,
            'cost_per_1k_tokens': base_cost,
            'estimated_api_cost': round(total_cost, 4),
            'note': 'Estimates based on current API pricing. Actual costs may vary.',
            'calculation_method': 'progressive' if self._premium_features_loaded else 'basic'
        }

    def _generate_recommendations(self, analysis: Dict[str, Any], efficiency_score: float) -> List[str]:
        """Generate optimization recommendations (progressive feature)"""
        recommendations = []
        
        if efficiency_score < 0.6:
            recommendations.append("Consider optimizing chunk sizes for better token distribution")
        
        if analysis['over_limit_percentage'] > 20:
            recommendations.append(f"Reduce chunk size - {analysis['over_limit_percentage']:.1f}% exceed token limit")
        
        if analysis['min_tokens'] < 50:
            recommendations.append("Some chunks are very small - consider combining short paragraphs")
        
        if analysis['max_tokens'] > analysis['token_limit'] * 1.5:
            recommendations.append("Some chunks are extremely large - consider more aggressive splitting")
        
        # Tokenizer-specific recommendations
        if analysis['tokenizer_used'] in ['word_estimator', 'char_estimator'] and analysis['total_tokens'] > 10000:
            recommendations.append("Consider upgrading to exact tokenizers for large datasets")
        
        if not recommendations:
            recommendations.append("Your chunking strategy looks well-optimized!")
        
        return recommendations

    # ==================================================================================
    # TOKENIZER INTERFACE METHODS
    # ==================================================================================

    def get_available_tokenizers(self) -> List[Dict[str, Any]]:
        """Get list of available tokenizers with licensing and loading info"""
        if hasattr(self.tokenizer_manager, 'get_available_tokenizers'):
            tokenizers = self.tokenizer_manager.get_available_tokenizers()
        else:
            # Fallback for basic tokenizer manager
            tokenizers = [
                {
                    'name': 'word_estimator',
                    'display_name': 'Word Count Estimator',
                    'description': 'Fast word-based token estimation',
                    'is_premium': False,
                    'performance': 'fast',
                    'accuracy': 'estimated',
                    'compatible_models': ['general'],
                    'available': True,
                    'loading_status': 'loaded',
                    'error_message': None
                }
            ]
        
        # Add license access information
        for tokenizer in tokenizers:
            # Check license access
            has_access = True
            if self._license_manager_available and self.license_manager:
                try:
                    has_access = self.license_manager.check_tokenizer_access(tokenizer['name'])
                except:
                    pass
            
            tokenizer['has_access'] = has_access
            
            # Update display name for locked tokenizers
            if tokenizer['is_premium'] and not has_access:
                if not tokenizer['display_name'].startswith('🔒'):
                    tokenizer['display_name'] = f"🔒 {tokenizer['display_name']}"
        
        return tokenizers

    def get_recommended_tokenizer(self, target_model: str = None) -> str:
        """Get recommended tokenizer with license consideration"""
        # Get manager recommendation
        if hasattr(self.tokenizer_manager, 'get_recommended_tokenizer'):
            recommended = self.tokenizer_manager.get_recommended_tokenizer(target_model)
        else:
            recommended = 'word_estimator'
        
        # Check license access
        if self._license_manager_available and self.license_manager:
            try:
                if not self.license_manager.check_tokenizer_access(recommended):
                    # Fall back to best available free tokenizer
                    return 'word_estimator'
            except:
                pass
        
        return recommended

    def get_token_count(self, text: str, tokenizer_name: str = 'word_estimator') -> Tuple[int, Dict[str, Any]]:
        """Enhanced token counting with license and loading status"""
        # Check access first
        actual_tokenizer = self._validate_tokenizer_access(tokenizer_name)
        
        # Get count from tokenizer manager
        if hasattr(self.tokenizer_manager, 'get_token_count'):
            count, metadata = self.tokenizer_manager.get_token_count(text, actual_tokenizer)
        else:
            # Basic fallback
            word_count = len(text.split())
            count = max(1, int(word_count * 1.3))
            metadata = {
                'method': 'word_approximation',
                'accuracy': 'estimated',
                'fallback_used': True
            }
        
        # Add license information
        if self._license_manager_available and self.license_manager:
            try:
                if actual_tokenizer != tokenizer_name:
                    metadata['access_denied'] = True
                    metadata['requested_tokenizer'] = tokenizer_name
                    metadata['upgrade_message'] = self.license_manager.get_upgrade_message('advanced_tokenizers')
                else:
                    metadata['access_denied'] = False
            except:
                metadata['license_check_failed'] = True
        
        return count, metadata

    # ==================================================================================
    # LICENSE AND UPGRADE METHODS (Required by existing UI)
    # ==================================================================================

    def get_licensing_info(self) -> Dict[str, Any]:
        """Get current licensing status and available features"""
        if not self._license_manager_available or not self.license_manager:
            return {
                'license_status': {
                    'status': 'basic',
                    'tier': 'free',
                    'days_remaining': None,
                    'user_email': None
                },
                'tokenizer_stats': {'available': 2, 'premium': 0},
                'available_features': ['basic_processing'],
                'premium_licensed': False,
                'cost_analysis_available': False,
                'license_manager_available': False
            }
        
        try:
            license_status = self.license_manager.get_license_status()
            tokenizer_stats = {'available': len(self.get_available_tokenizers()), 'premium': 0}
            
            return {
                'license_status': {
                    'status': license_status.status.value,
                    'tier': license_status.tier.value,
                    'days_remaining': license_status.days_remaining,
                    'user_email': license_status.user_email
                },
                'tokenizer_stats': tokenizer_stats,
                'available_features': license_status.features_enabled,
                'premium_licensed': self.license_manager.is_premium_licensed(),
                'cost_analysis_available': (self._cost_calculator_available and 
                                          self.license_manager.check_feature_access('advanced_cost_analysis')),
                'license_manager_available': True
            }
        except Exception as e:
            logging.warning(f"License info retrieval failed: {e}")
            return self.get_licensing_info()  # Return basic info

    def start_trial(self) -> bool:
        """Start premium trial with fallback"""
        if self._license_manager_available and self.license_manager:
            try:
                return self.license_manager.start_trial()
            except Exception as e:
                logging.warning(f"Trial start failed: {e}")
        return False

    def get_upgrade_info(self) -> Dict[str, Any]:
        """Get information for upgrade dialog with fallback"""
        if self._license_manager_available and self.license_manager:
            try:
                return self.license_manager.show_premium_upgrade_info()
            except Exception as e:
                logging.warning(f"Upgrade info retrieval failed: {e}")
        
        # Basic upgrade info fallback
        return {
            'message': 'Upgrade to Premium for advanced features',
            'features': ['Exact tokenization', 'Advanced analytics', 'Cost analysis'],
            'pricing': 'Contact for pricing information'
        }

# Legacy compatibility functions (maintain existing API)
def process_book(path, clean_opts, split_method, delimiter=None):
    """Legacy function for backward compatibility"""
    controller = ProcessingController()
    return controller.process_book(path, clean_opts, split_method, delimiter)

def get_token_count(text):
    """Legacy function for backward compatibility"""
    controller = ProcessingController()
    count, metadata = controller.get_token_count(text)
    return count