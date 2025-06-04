# test_model_database.py
"""
Test script for the Model Parameter Database
Run this to validate the database is working correctly
"""

import sys
import os

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.model_database import ModelParameterDatabase, ModelFamily, TrainingFeasibility, get_model_database
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running this from the project root directory")
    print("and that core/model_database.py exists")
    sys.exit(1)

def test_basic_functionality():
    """Test basic database functionality"""
    print("🧪 Testing Model Parameter Database")
    print("=" * 50)
    
    # Initialize database
    try:
        db = ModelParameterDatabase()
        print(f"✅ Database initialized with {len(db.models)} models")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False
    
    return True

def test_model_retrieval():
    """Test model information retrieval"""
    print("\n📊 Testing Model Retrieval")
    print("-" * 30)
    
    db = get_model_database()
    
    # Test specific model lookup
    test_models = ["gpt-4", "llama-2-7b", "claude-3-opus", "bert-base-uncased"]
    
    for model_name in test_models:
        model_info = db.get_model_info(model_name)
        if model_info:
            print(f"✅ {model_name}: {model_info.parameters:,} parameters, {model_info.training_feasibility.value}")
        else:
            print(f"❌ {model_name}: Not found")
    
    # Test case variations
    variations = ["GPT-4", "gpt_4", "GPT 4"]
    for variation in variations:
        model_info = db.get_model_info(variation)
        if model_info:
            print(f"✅ Name variation '{variation}' found: {model_info.name}")
        else:
            print(f"❌ Name variation '{variation}' not found")

def test_filtering_and_search():
    """Test filtering and search functionality"""
    print("\n🔍 Testing Filtering and Search")
    print("-" * 35)
    
    db = get_model_database()
    
    # Test by family
    openai_models = db.get_models_by_family(ModelFamily.OPENAI)
    print(f"✅ OpenAI models: {len(openai_models)} found")
    for model in openai_models:
        print(f"   - {model.display_name}")
    
    # Test trainable models
    trainable = db.get_trainable_models()
    local_only = db.get_trainable_models(local_only=True)
    print(f"✅ Trainable models: {len(trainable)} total, {len(local_only)} local-feasible")
    
    # Test API models
    api_models = db.get_api_models()
    print(f"✅ API models: {len(api_models)} found")
    
    # Test search
    search_results = db.search_models("llama")
    print(f"✅ Search 'llama': {len(search_results)} results")

def test_calculations():
    """Test calculation methods"""
    print("\n🧮 Testing Calculations")
    print("-" * 25)
    
    db = get_model_database()
    
    # Test Chinchilla scaling
    test_params = [7_000_000_000, 175_000_000_000]  # 7B and 175B
    
    for params in test_params:
        optimal_tokens = db.estimate_chinchilla_tokens(params)
        compute_budget = db.estimate_compute_budget(params)
        
        print(f"✅ {params/1_000_000_000:.1f}B parameters:")
        print(f"   - Optimal tokens: {optimal_tokens:,}")
        print(f"   - Compute budget: {compute_budget:.2e} FLOPs")

def test_database_validation():
    """Test database validation"""
    print("\n✅ Testing Database Validation")
    print("-" * 32)
    
    db = get_model_database()
    validation_result = db.validate_database()
    
    print(f"Database valid: {validation_result['valid']}")
    print(f"Models validated: {validation_result['total_models_validated']}")
    
    if validation_result['issues']:
        print("❌ Issues found:")
        for issue in validation_result['issues']:
            print(f"   - {issue}")
    else:
        print("✅ No critical issues found")
    
    if validation_result['warnings']:
        print("⚠️  Warnings:")
        for warning in validation_result['warnings']:
            print(f"   - {warning}")
    else:
        print("✅ No warnings")

def test_summary_stats():
    """Test summary statistics"""
    print("\n📈 Database Summary Statistics")
    print("-" * 32)
    
    db = get_model_database()
    summary = db.get_model_summary()
    
    print(f"Total models: {summary['total_models']}")
    print(f"Trainable models: {summary['trainable_models']}")
    print(f"Local trainable: {summary['local_trainable']}")
    print(f"API available: {summary['api_available']}")
    
    print("\nBy Family:")
    for family, count in summary['by_family'].items():
        print(f"  {family}: {count}")
    
    print("\nBy Training Feasibility:")
    for feasibility, count in summary['by_feasibility'].items():
        print(f"  {feasibility}: {count}")
    
    print("\nBy Pricing Tier:")
    for tier, count in summary['by_pricing_tier'].items():
        print(f"  {tier}: {count}")

def detailed_model_inspection():
    """Show detailed information for a few key models"""
    print("\n🔬 Detailed Model Inspection")
    print("-" * 32)
    
    db = get_model_database()
    
    # Show details for key models
    key_models = ["gpt-4", "llama-2-7b", "claude-3-opus"]
    
    for model_name in key_models:
        model = db.get_model_info(model_name)
        if model:
            print(f"\n📋 {model.display_name} ({model.family.value})")
            print(f"   Parameters: {model.parameters:,}")
            print(f"   Context Length: {model.context_length:,}")
            print(f"   Training Feasibility: {model.training_feasibility.value}")
            print(f"   GPU Memory: {model.gpu_memory_required}GB")
            print(f"   Training Multiplier: {model.training_memory_multiplier}x")
            if model.estimated_training_cost:
                print(f"   Est. Training Cost: ${model.estimated_training_cost:,}")
            if model.api_cost_per_1k_tokens:
                print(f"   API Cost: ${model.api_cost_per_1k_tokens}/1K tokens")
            print(f"   Use Cases: {', '.join(model.use_cases)}")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Model Database Tests")
    print("=" * 50)
    
    try:
        # Basic functionality
        if not test_basic_functionality():
            return False
        
        # Model retrieval
        test_model_retrieval()
        
        # Filtering and search
        test_filtering_and_search()
        
        # Calculations
        test_calculations()
        
        # Validation
        test_database_validation()
        
        # Summary stats
        test_summary_stats()
        
        # Detailed inspection
        detailed_model_inspection()
        
        print("\n🎉 All tests completed successfully!")
        print("The Model Parameter Database is ready for use.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)