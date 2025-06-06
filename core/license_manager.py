# core/license_manager.py
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from enum import Enum
import hashlib

# Try to import encryption for future license key validation
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.warning("pycryptodome not available - license encryption disabled")

class LicenseStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALID = "invalid"
    TRIAL = "trial"
    FREE = "free"
    DEMO = "demo"

class FeatureTier(Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

@dataclass
class LicenseInfo:
    status: LicenseStatus
    tier: FeatureTier
    expires_at: Optional[datetime]
    features_enabled: List[str]
    user_email: Optional[str] = None
    license_key: Optional[str] = None
    days_remaining: Optional[int] = None
    trial_days_used: int = 0

class LicenseManager:
    def __init__(self):
        self.license_file_path = os.path.join(os.getcwd(), ".wolfscribe_license")
        self.trial_file_path = os.path.join(os.getcwd(), ".wolfscribe_trial")
        self._license_info: Optional[LicenseInfo] = None
        self._feature_definitions = self._build_feature_definitions()
        self._initialize_license()

    def _build_feature_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Define what features belong to which tiers"""
        return {
            # Free tier features
            'basic_tokenization': {
                'tier': FeatureTier.FREE,
                'description': 'Basic GPT-2 tokenization',
                'tokenizers': ['gpt2']
            },
            'basic_export': {
                'tier': FeatureTier.FREE,
                'description': 'Export as TXT and CSV',
                'formats': ['txt', 'csv']
            },
            'basic_chunking': {
                'tier': FeatureTier.FREE,
                'description': 'Paragraph, sentence, and custom splitting'
            },
            
            # Premium tier features
            'advanced_tokenizers': {
                'tier': FeatureTier.PREMIUM,
                'description': 'OpenAI, Claude, and BERT tokenizers',
                'tokenizers': ['tiktoken_gpt4', 'tiktoken_gpt35', 'sentence_transformer', 'claude_estimator']
            },
            'advanced_cost_analysis': {
            'tier': FeatureTier.PREMIUM,
            'description': 'Comprehensive AI training cost analysis and optimization'
            },
            'smart_chunking': {
                'tier': FeatureTier.PREMIUM,
                'description': 'AI-powered dynamic chunking optimization'
            },
            'advanced_analytics': {
                'tier': FeatureTier.PREMIUM,
                'description': 'Token statistics and cost estimation'
            },
            'batch_processing': {
                'tier': FeatureTier.PREMIUM,
                'description': 'Process multiple files simultaneously'
            },
            'export_metadata': {
                'tier': FeatureTier.PREMIUM,
                'description': 'Export with tokenizer metadata and statistics'
            },
            'model_compatibility': {
                'tier': FeatureTier.PREMIUM,
                'description': 'Advanced model compatibility checking'
            }
        }

    def _initialize_license(self):
        """Initialize license status on startup"""
        # Check for demo mode (environment variable)
        if os.getenv('WOLFSCRIBE_DEMO', '').lower() in ['true', '1', 'yes']:
            self._license_info = LicenseInfo(
                status=LicenseStatus.DEMO,
                tier=FeatureTier.PREMIUM,
                expires_at=None,
                features_enabled=list(self._feature_definitions.keys()),
                user_email="demo@wolfscribe.ai"
            )
            logging.info("Demo mode activated - all premium features enabled")
            return

        # Check for license file
        if os.path.exists(self.license_file_path):
            try:
                with open(self.license_file_path, 'r') as f:
                    license_data = json.load(f)
                self._license_info = self._validate_license_data(license_data)
                logging.info(f"License loaded: {self._license_info.status.value}")
                return
            except Exception as e:
                logging.error(f"Failed to load license file: {e}")

        # Check for environment variable license
        license_key = os.getenv('WOLFSCRIBE_LICENSE_KEY')
        if license_key:
            self._license_info = self._validate_license_key(license_key)
            logging.info(f"Environment license loaded: {self._license_info.status.value}")
            return

        # Check for trial
        trial_info = self._check_trial_status()
        if trial_info:
            self._license_info = trial_info
            logging.info(f"Trial license active: {trial_info.days_remaining} days remaining")
            return

        # Default to free tier
        self._license_info = LicenseInfo(
            status=LicenseStatus.FREE,
            tier=FeatureTier.FREE,
            expires_at=None,
            features_enabled=self._get_features_for_tier(FeatureTier.FREE)
        )
        logging.info("No license found - using free tier")

    def _validate_license_data(self, license_data: Dict) -> LicenseInfo:
        """Validate license data from file"""
        try:
            expires_str = license_data.get('expires_at')
            expires_at = datetime.fromisoformat(expires_str) if expires_str else None
            
            # Check if expired
            if expires_at and expires_at < datetime.now():
                status = LicenseStatus.EXPIRED
                tier = FeatureTier.FREE
            else:
                status = LicenseStatus.ACTIVE
                tier = FeatureTier.PREMIUM
            
            days_remaining = None
            if expires_at:
                days_remaining = max(0, (expires_at - datetime.now()).days)
            
            return LicenseInfo(
                status=status,
                tier=tier,
                expires_at=expires_at,
                features_enabled=self._get_features_for_tier(tier),
                user_email=license_data.get('user_email'),
                license_key=license_data.get('license_key'),
                days_remaining=days_remaining
            )
        except Exception as e:
            logging.error(f"Invalid license data: {e}")
            return LicenseInfo(
                status=LicenseStatus.INVALID,
                tier=FeatureTier.FREE,
                expires_at=None,
                features_enabled=self._get_features_for_tier(FeatureTier.FREE)
            )

    def _validate_license_key(self, license_key: str) -> LicenseInfo:
        """Validate license key from environment variable"""
        # Simple validation for now - in future this would call Stripe API
        if license_key.startswith('wfs_') and len(license_key) >= 20:
            return LicenseInfo(
                status=LicenseStatus.ACTIVE,
                tier=FeatureTier.PREMIUM,
                expires_at=None,  # Assume subscription is active
                features_enabled=self._get_features_for_tier(FeatureTier.PREMIUM),
                license_key=license_key
            )
        else:
            return LicenseInfo(
                status=LicenseStatus.INVALID,
                tier=FeatureTier.FREE,
                expires_at=None,
                features_enabled=self._get_features_for_tier(FeatureTier.FREE)
            )

    def _check_trial_status(self) -> Optional[LicenseInfo]:
        """Check if user is eligible for or currently in trial"""
        trial_length_days = 7  # 7-day trial
        
        if os.path.exists(self.trial_file_path):
            try:
                with open(self.trial_file_path, 'r') as f:
                    trial_data = json.load(f)
                
                start_date = datetime.fromisoformat(trial_data['start_date'])
                days_used = (datetime.now() - start_date).days
                days_remaining = max(0, trial_length_days - days_used)
                
                if days_remaining > 0:
                    return LicenseInfo(
                        status=LicenseStatus.TRIAL,
                        tier=FeatureTier.PREMIUM,
                        expires_at=start_date + timedelta(days=trial_length_days),
                        features_enabled=self._get_features_for_tier(FeatureTier.PREMIUM),
                        days_remaining=days_remaining,
                        trial_days_used=days_used
                    )
                else:
                    # Trial expired
                    return None
            except Exception as e:
                logging.error(f"Error reading trial file: {e}")
                return None
        
        return None

    def start_trial(self) -> bool:
        """Start a new trial period"""
        if os.path.exists(self.trial_file_path):
            logging.warning("Trial already started")
            return False
        
        try:
            trial_data = {
                'start_date': datetime.now().isoformat(),
                'device_id': self._get_device_id()
            }
            
            with open(self.trial_file_path, 'w') as f:
                json.dump(trial_data, f, indent=2)
            
            # Reinitialize to load trial
            self._initialize_license()
            logging.info("Trial started successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to start trial: {e}")
            return False

    def _get_device_id(self) -> str:
        """Generate a simple device identifier"""
        # Simple device ID based on hostname and user
        import platform
        import getpass
        device_string = f"{platform.node()}-{getpass.getuser()}"
        return hashlib.md5(device_string.encode()).hexdigest()[:16]

    def _get_features_for_tier(self, tier: FeatureTier) -> List[str]:
        """Get list of features available for a tier"""
        features = []
        for feature_name, feature_info in self._feature_definitions.items():
            if feature_info['tier'] == FeatureTier.FREE or (tier == FeatureTier.PREMIUM and feature_info['tier'] in [FeatureTier.FREE, FeatureTier.PREMIUM]):
                features.append(feature_name)
        return features

    # Public API Methods

    def is_premium_licensed(self) -> bool:
        """Check if user has premium license"""
        if not self._license_info:
            return False
        return self._license_info.tier in [FeatureTier.PREMIUM, FeatureTier.ENTERPRISE] and \
               self._license_info.status in [LicenseStatus.ACTIVE, LicenseStatus.TRIAL, LicenseStatus.DEMO]

    def check_feature_access(self, feature_name: str) -> bool:
        """Check if user has access to a specific feature"""
        if not self._license_info:
            return False
        return feature_name in self._license_info.features_enabled

    def check_tokenizer_access(self, tokenizer_name: str) -> bool:
        """Check if user has access to a specific tokenizer"""
        if not self.check_feature_access('advanced_tokenizers'):
            # Only GPT-2 available in free tier
            return tokenizer_name == 'gpt2'
        return True

    def get_license_status(self) -> LicenseInfo:
        """Get current license information"""
        if not self._license_info:
            self._initialize_license()
        return self._license_info

    def get_upgrade_message(self, feature_name: str) -> str:
        """Get contextual upgrade message for a feature"""
        feature_info = self._feature_definitions.get(feature_name, {})
        description = feature_info.get('description', feature_name)
        
        if self._license_info and self._license_info.status == LicenseStatus.TRIAL:
            days = self._license_info.days_remaining or 0
            return f"Trial: {days} days left for {description}"
        elif self._license_info and self._license_info.status == LicenseStatus.EXPIRED:
            return f"License expired. Renew to access {description}"
        else:
            return f"Upgrade to Premium for {description}"

    def show_premium_upgrade_info(self) -> Dict[str, Any]:
        """Get information for showing upgrade dialog"""
        license_status = self.get_license_status()
        
        premium_features = []
        for feature_name, feature_info in self._feature_definitions.items():
            if feature_info['tier'] == FeatureTier.PREMIUM:
                premium_features.append({
                    'name': feature_name,
                    'description': feature_info['description'],
                    'available': self.check_feature_access(feature_name)
                })

        return {
            'current_status': license_status.status.value,
            'current_tier': license_status.tier.value,
            'days_remaining': license_status.days_remaining,
            'trial_available': not os.path.exists(self.trial_file_path),
            'premium_features': premium_features,
            'upgrade_url': 'https://wolflow.ai/upgrade',  # Future Stripe integration
            'pricing': {
                'monthly': '$15/month',
                'yearly': '$150/year (2 months free)'
            }
        }

    def install_license(self, license_key: str, user_email: str) -> bool:
        """Install a new license (for future Stripe integration)"""
        try:
            # In future, this would validate with Stripe API
            # For now, simple validation
            if license_key.startswith('wfs_') and '@' in user_email:
                license_data = {
                    'license_key': license_key,
                    'user_email': user_email,
                    'installed_at': datetime.now().isoformat(),
                    'device_id': self._get_device_id()
                }
                
                with open(self.license_file_path, 'w') as f:
                    json.dump(license_data, f, indent=2)
                
                # Reinitialize to load new license
                self._initialize_license()
                logging.info(f"License installed for {user_email}")
                return True
            else:
                logging.error("Invalid license key format")
                return False
        except Exception as e:
            logging.error(f"Failed to install license: {e}")
            return False

    def remove_license(self) -> bool:
        """Remove current license (for testing/troubleshooting)"""
        try:
            if os.path.exists(self.license_file_path):
                os.remove(self.license_file_path)
            if os.path.exists(self.trial_file_path):
                os.remove(self.trial_file_path)
            
            # Reinitialize to free tier
            self._initialize_license()
            logging.info("License removed - reverted to free tier")
            return True
        except Exception as e:
            logging.error(f"Failed to remove license: {e}")
            return False

    def get_feature_list(self, tier: Optional[FeatureTier] = None) -> Dict[str, Dict[str, Any]]:
        """Get list of features for a tier"""
        if tier is None:
            return self._feature_definitions
        
        return {
            name: info for name, info in self._feature_definitions.items()
            if info['tier'] == tier or (tier == FeatureTier.PREMIUM and info['tier'] == FeatureTier.FREE)
        }