# controller.py - Enhanced with Cost Analysis Integration
import logging
from typing import List, Dict, Any, Tuple, Optional
from processing.extract import load_file
from processing.clean import clean_text
from processing.splitter import split_text  # Keep existing basic splitter

# Import our premium systems
from core.tokenizer_manager import TokenizerManager
from core.license_manager import LicenseManager, FeatureTier
from core.cost_calculator import EnhancedCostCalculator, calculate_training_cost

class ProcessingController:
    """Enhanced controller with premium tokenizer support and cost analysis"""
    
    def __init__(self):
        self.tokenizer_manager = TokenizerManager()
        self.license_manager = LicenseManager()
        
        # Initialize cost calculator with error handling
        try:
            self.cost_calculator = EnhancedCostCalculator()
            self._cost_calculator_available = True
            logging.info("Enhanced Cost Calculator initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Cost Calculator: {e}")
            self.cost_calculator = None
            self._cost_calculator_available = False
        
        # Update license manager with cost analysis feature
        self._add_cost_analysis_feature()
        
        logging.info("ProcessingController initialized with premium tokenizer and cost analysis support")

    def _add_cost_analysis_feature(self):
        """Add cost analysis feature to license manager feature definitions"""
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

    def process_book(self, path: str, clean_opts: Dict[str, Any], split_method: str, 
                    delimiter: str = None, tokenizer_name: str = 'gpt2', 
                    use_smart_splitting: bool = None, max_tokens: int = 512) -> List[str]:
        """
        Enhanced book processing (smart splitting disabled for now)
        
        Args:
            path: File path to process
            clean_opts: Cleaning options dictionary
            split_method: Splitting method ('paragraph', 'sentence', 'custom')
            delimiter: Custom delimiter if split_method is 'custom'
            tokenizer_name: Tokenizer to use for processing
            use_smart_splitting: Whether to use smart splitting (disabled for now)
            max_tokens: Maximum tokens per chunk for smart splitting
            
        Returns:
            List of text chunks
        """
        # Validate tokenizer access
        if not self.license_manager.check_tokenizer_access(tokenizer_name):
            logging.warning(f"Access denied to tokenizer {tokenizer_name}, falling back to gpt2")
            tokenizer_name = 'gpt2'
        
        # Load and clean text
        raw = load_file(path)
        cleaned = clean_text(raw, **clean_opts)
        
        # Use basic splitting for now (smart splitting will be added later)
        chunks = split_text(cleaned, split_method, delimiter)
        
        logging.info(f"Processed {path}: {len(chunks)} chunks created using basic {split_method} splitting")
        return chunks

    def get_smart_splitting_status(self) -> Dict[str, Any]:
        """Get smart splitting status for UI info display"""
        has_smart_access = self.license_manager.check_feature_access('smart_chunking')
        
        return {
            'available': False,  # Disabled for now
            'description': 'Smart chunking will be available in a future update',
            'upgrade_message': 'Coming soon - automatic token optimization for premium users'
        }

    # ==================================================================================
    # ENHANCED METHODS WITH COST ANALYSIS INTEGRATION
    # ==================================================================================

    def analyze_chunks(self, chunks: List[str], tokenizer_name: str = 'gpt2', 
                      token_limit: int = 512) -> Dict[str, Any]:
        """
        Enhanced analyze_chunks method with optional cost analysis integration
        Maintains full backward compatibility while adding cost insights for premium users
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

        # Check access to advanced analytics
        has_advanced_analytics = self.license_manager.check_feature_access('advanced_analytics')
        has_cost_analysis = self.license_manager.check_feature_access('advanced_cost_analysis')
        
        token_counts = []
        over_limit_count = 0
        
        for chunk in chunks:
            count, metadata = self.get_token_count(chunk, tokenizer_name)
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
            'tokenizer_used': tokenizer_name,
            'token_limit': token_limit
        }

        # Premium analytics
        if has_advanced_analytics:
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
            cost_estimates = self._calculate_cost_estimates(total_tokens, tokenizer_name)
            
            analysis.update({
                'efficiency_score': round(efficiency_score * 100, 1),
                'token_distribution': token_ranges,
                'cost_estimates': cost_estimates,
                'recommendations': self._generate_recommendations(analysis, efficiency_score),
                'advanced_analytics': True
            })
        else:
            analysis.update({
                'advanced_analytics': False,
                'upgrade_message': self.license_manager.get_upgrade_message('advanced_analytics')
            })

        # Add basic cost preview for all users
        cost_preview = self._get_cost_preview(total_tokens, tokenizer_name, has_cost_analysis)
        analysis['cost_preview'] = cost_preview

        return analysis

    def analyze_chunks_with_costs(self, chunks: List[str], tokenizer_name: str = 'gpt2',
                                 token_limit: int = 512, target_models: Optional[List[str]] = None,
                                 api_usage_monthly: int = 100000) -> Dict[str, Any]:
        """
        Enhanced analysis method with comprehensive cost analysis
        
        Args:
            chunks: List of text chunks to analyze
            tokenizer_name: Tokenizer to use for analysis
            token_limit: Token limit per chunk
            target_models: Optional list of target models for cost analysis
            api_usage_monthly: Monthly API usage in tokens for ROI analysis
            
        Returns:
            Comprehensive analysis including detailed cost breakdown
        """
        # Start with standard analysis
        analysis = self.analyze_chunks(chunks, tokenizer_name, token_limit)
        
        # Check if user has access to advanced cost analysis
        if not self.license_manager.check_feature_access('advanced_cost_analysis'):
            analysis['cost_analysis'] = {
                'available': False,
                'upgrade_message': self.license_manager.get_upgrade_message('advanced_cost_analysis'),
                'preview': self._get_cost_preview(analysis['total_tokens'], tokenizer_name, False)
            }
            return analysis
        
        # Perform comprehensive cost analysis for premium users
        if not self._cost_calculator_available:
            analysis['cost_analysis'] = {
                'available': False,
                'error': 'Cost calculator not available',
                'basic_estimate': self._get_basic_cost_estimate(analysis['total_tokens'])
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

    def _get_cost_preview(self, total_tokens: int, tokenizer_name: str, has_full_access: bool) -> Dict[str, Any]:
        """Generate cost preview for all users"""
        if has_full_access and self._cost_calculator_available:
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
            'upgrade_message': 'Upgrade to Premium for exact cost analysis with 15+ training approaches',
            'confidence': 'low'
        }

    def _get_basic_cost_estimate(self, total_tokens: int) -> Dict[str, Any]:
        """Generate basic cost estimate for free users"""
        # Rough estimates based on common approaches
        # Local training (RTX 4090): ~$0.0003 per token
        # API fine-tuning: ~$0.01-0.03 per token
        
        local_estimate = total_tokens * 0.0003
        api_estimate_low = total_tokens * 0.008  # GPT-3.5 training
        api_estimate_high = total_tokens * 0.030  # GPT-4 training
        
        return {
            'total_tokens': total_tokens,
            'local_training': local_estimate,
            'api_low': api_estimate_low,
            'api_high': api_estimate_high,
            'min_cost': local_estimate,
            'max_cost': api_estimate_high,
            'note': 'Rough estimates only - upgrade for precise calculations'
        }

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

    # ==================================================================================
    # EXISTING METHODS (UNCHANGED)
    # ==================================================================================

    def get_available_tokenizers(self) -> List[Dict[str, Any]]:
        """Get list of available tokenizers with licensing info"""
        tokenizers = []
        for tokenizer_info in self.tokenizer_manager.get_available_tokenizers():
            # Check if user has access to this tokenizer
            has_access = self.license_manager.check_tokenizer_access(tokenizer_info.name)
            
            tokenizers.append({
                'name': tokenizer_info.name,
                'display_name': tokenizer_info.display_name,
                'description': tokenizer_info.description,
                'is_premium': tokenizer_info.is_premium,
                'performance': tokenizer_info.performance.value,
                'accuracy': tokenizer_info.accuracy.value,
                'compatible_models': tokenizer_info.compatible_models,
                'available': tokenizer_info.available,
                'has_access': has_access,
                'error_message': tokenizer_info.error_message
            })
        
        return tokenizers

    def get_recommended_tokenizer(self, target_model: str = None) -> str:
        """Get recommended tokenizer for a target model"""
        if target_model:
            recommended = self.tokenizer_manager.get_recommended_tokenizer(target_model)
            # Check if user has access to recommended tokenizer
            if self.license_manager.check_tokenizer_access(recommended):
                return recommended
        
        # Fallback to best available tokenizer for user's license
        if self.license_manager.is_premium_licensed():
            # Return first available premium tokenizer
            for tokenizer_info in self.tokenizer_manager.get_available_tokenizers():
                if tokenizer_info.is_premium and tokenizer_info.available:
                    return tokenizer_info.name
        
        # Default to GPT-2
        return 'gpt2'

    def get_token_count(self, text: str, tokenizer_name: str = 'gpt2') -> Tuple[int, Dict[str, Any]]:
        """Enhanced token counting with metadata"""
        # Check access to tokenizer
        if not self.license_manager.check_tokenizer_access(tokenizer_name):
            # Add access denial to metadata
            count, metadata = self.tokenizer_manager.get_token_count(text, 'gpt2')
            metadata['access_denied'] = True
            metadata['requested_tokenizer'] = tokenizer_name
            metadata['upgrade_message'] = self.license_manager.get_upgrade_message('advanced_tokenizers')
            return count, metadata
        
        # Use requested tokenizer
        count, metadata = self.tokenizer_manager.get_token_count(text, tokenizer_name)
        metadata['access_denied'] = False
        return count, metadata

    def _calculate_cost_estimates(self, total_tokens: int, tokenizer_name: str) -> Dict[str, Any]:
        """Calculate training cost estimates (premium feature)"""
        # Rough cost estimates for popular training services
        cost_per_1k_tokens = {
            'gpt2': 0.0,  # Free/open source
            'tiktoken_gpt4': 0.03,  # OpenAI API costs
            'tiktoken_gpt35': 0.002,
            'sentence_transformer': 0.0,  # Open source
            'claude_estimator': 0.008  # Anthropic API costs
        }
        
        base_cost = cost_per_1k_tokens.get(tokenizer_name, 0.01)
        total_cost = (total_tokens / 1000) * base_cost
        
        return {
            'tokenizer': tokenizer_name,
            'total_tokens': total_tokens,
            'cost_per_1k_tokens': base_cost,
            'estimated_api_cost': round(total_cost, 4),
            'note': 'Estimates based on current API pricing. Actual costs may vary.'
        }

    def _generate_recommendations(self, analysis: Dict[str, Any], efficiency_score: float) -> List[str]:
        """Generate optimization recommendations (premium feature)"""
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
        if analysis['tokenizer_used'] == 'gpt2' and analysis['total_tokens'] > 10000:
            recommendations.append("Consider upgrading to exact tokenizers for large datasets")
        
        if not recommendations:
            recommendations.append("Your chunking strategy looks well-optimized!")
        
        return recommendations

    def get_licensing_info(self) -> Dict[str, Any]:
        """Get current licensing status and available features"""
        license_status = self.license_manager.get_license_status()
        tokenizer_stats = self.tokenizer_manager.get_tokenizer_stats()
        
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
            'cost_analysis_available': self._cost_calculator_available and 
                                     self.license_manager.check_feature_access('advanced_cost_analysis')
        }

    def start_trial(self) -> bool:
        """Start premium trial"""
        return self.license_manager.start_trial()

    def get_upgrade_info(self) -> Dict[str, Any]:
        """Get information for upgrade dialog"""
        return self.license_manager.show_premium_upgrade_info()

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