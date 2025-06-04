# Quick test
from core.cost_calculator import calculate_training_cost

# Test with a 50K token dataset for LLaMA 2 7B
results = calculate_training_cost(50000, "llama-2-7b")
print(f"Best approach: {results['cost_estimates'][0]['approach_name']}")
print(f"Cost: ${results['cost_estimates'][0]['total_cost_usd']:.2f}")
print(f"Break-even: {results['roi_analysis']['break_even_months']:.1f} months")