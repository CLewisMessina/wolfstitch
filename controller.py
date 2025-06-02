# controller.py
import logging
from typing import List, Dict, Any, Tuple, Optional
from processing.extract import load_file
from processing.clean import clean_text
from processing.splitter import split_text

# Import our new premium systems
from core.tokenizer_manager import TokenizerManager
from core.license_manager import LicenseManager

class ProcessingController:
    """Enhanced controller with premium tokenizer support"""
    
    def __init__(self):
        self.tokenizer_manager = TokenizerManager()
        self.license_manager = LicenseManager()
        logging.info("ProcessingController initialized with premium tokenizer support")

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

    def process_book(self, path: str, clean_opts: Dict[str, Any], split_method: str, 
                    delimiter: str = None, tokenizer_name: str = 'gpt2') -> List[str]:
        """
        Enhanced book processing with tokenizer selection
        
        Args:
            path: File path to process
            clean_opts: Cleaning options dictionary
            split_method: Splitting method ('paragraph', 'sentence', 'custom')
            delimiter: Custom delimiter if split_method is 'custom'
            tokenizer_name: Tokenizer to use for processing
            
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
        
        # Split text
        chunks = split_text(cleaned, split_method, delimiter)
        
        logging.info(f"Processed {path}: {len(chunks)} chunks created using {tokenizer_name}")
        return chunks

    def get_token_count(self, text: str, tokenizer_name: str = 'gpt2') -> Tuple[int, Dict[str, Any]]:
        """
        Enhanced token counting with metadata
        
        Args:
            text: Text to count tokens for
            tokenizer_name: Tokenizer to use
            
        Returns:
            Tuple of (token_count, metadata)
            metadata includes accuracy, performance, compatibility info
        """
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

    def analyze_chunks(self, chunks: List[str], tokenizer_name: str = 'gpt2', 
                      token_limit: int = 512) -> Dict[str, Any]:
        """
        Analyze chunks with comprehensive statistics
        
        Args:
            chunks: List of text chunks
            tokenizer_name: Tokenizer to use for analysis
            token_limit: Token limit for warnings
            
        Returns:
            Dictionary with comprehensive analysis
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

        return analysis

    def _calculate_cost_estimates(self, total_tokens: int, tokenizer_name: str) -> Dict[str, Any]:
        """Calculate training cost estimates (premium feature)"""
        # Rough cost estimates for popular training services
        # These would be updated regularly in a real implementation
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
            recommendations.append("Consider using smart chunking to optimize token distribution")
        
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
            'premium_licensed': self.license_manager.is_premium_licensed()
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