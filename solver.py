import sys
import subprocess

# Ensure ortools is installed
try:
    from ortools.linear_solver import pywraplp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ortools"])
    from ortools.linear_solver import pywraplp

def create_data_model(order_weights, bin_capacity):
    """Create the data model for bin packing."""
    data = {}
    data['weights'] = order_weights  # Capacity constraint is based on weight
    data['items'] = list(range(len(order_weights)))
    data['bins'] = data['items']
    data['bin_capacity'] = bin_capacity
    return data

def solve_bin_packing(order_weights, bin_capacity, objective='min_bins', min_items_per_bin=1, bin_count=None, item_labels=None):
    """Solves the bin packing problem using OR-Tools.
    objective: 
        - 'min_bins' to minimize the number of bins used
        - 'max_weight' to maximize the packed weight in each bin 
        - 'max_items' to maximize the number of items in each bin
        - 'balance_bins' to balance weight across a fixed number of bins
    min_items_per_bin: Minimum number of items that must be in each used bin.
    bin_count: Number of bins to use (only for 'balance_bins' objective).
    item_labels: Optional labels for items (used for result reporting).
    
    Returns:
      - A dictionary of packed bins if solution is found
      - A tuple (None, error_message) if no solution is found
    """
    # Validate inputs
    if not order_weights:
        return None, "No weights provided to pack"
    
    if bin_capacity <= 0:
        return None, "Bin capacity must be positive"
    
    # Check if any individual weight exceeds bin capacity
    overweight_items = [(i, w) for i, w in enumerate(order_weights) if w > bin_capacity]
    if overweight_items:
        items_str = ", ".join([f"item {i} (weight {w})" for i, w in overweight_items])
        return None, f"Some items exceed bin capacity: {items_str}"
    
    # Check if min_items_per_bin is feasible
    if min_items_per_bin * max(order_weights) > bin_capacity:
        return None, f"Minimum items per bin ({min_items_per_bin}) cannot fit within bin capacity due to weight constraints"
    
    # Check if minimum items constraint is feasible with number of items
    total_items = len(order_weights)
    max_bins_possible = total_items // min_items_per_bin
    if max_bins_possible == 0 and total_items > 0:
        return None, f"Not enough items ({total_items}) to satisfy minimum items per bin ({min_items_per_bin})"
    
    # For balance_bins, check that bin_count is provided and reasonable
    if objective == 'balance_bins':
        if bin_count is None or bin_count < 2:
            return None, "For 'balance_bins' objective, you must specify at least 2 bins"
        
        total_weight = sum(order_weights)
        avg_bin_weight = total_weight / bin_count
        
        if avg_bin_weight > bin_capacity:
            return None, f"Cannot balance {total_weight} weight across {bin_count} bins (average {avg_bin_weight:.1f}) with capacity {bin_capacity}"
        
        if total_items < bin_count:
            return None, f"Not enough items ({total_items}) to distribute across {bin_count} bins"
    
    data = create_data_model(order_weights, bin_capacity)
    
    # Create the solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return None, "Failed to create solver instance"
    
    # Variables
    x = {}
    for i in data['items']:
        for j in data['bins']:
            x[(i, j)] = solver.IntVar(0, 1, f'x_{i}_{j}')
    
    y = {j: solver.IntVar(0, 1, f'y[{j}]') for j in data['bins']}
    
    # Track bin fill levels
    bin_fill = {}
    for j in data['bins']:
        bin_fill[j] = solver.NumVar(0, data['bin_capacity'], f'fill_{j}')
    
    # For max_items, track item count per bin
    item_count = {}
    if objective in ['max_items', 'balance_bins']:
        for j in data['bins']:
            item_count[j] = solver.IntVar(0, len(data['items']), f'items_{j}')
    
    # For balance_bins, we need variables to track deviations from average
    deviation_vars = {}
    if objective == 'balance_bins':
        # Limit to specified bin_count
        active_bins = min(bin_count, len(data['bins']))
        
        # Calculate target average weight per bin
        total_weight = sum(order_weights)
        avg_weight = total_weight / active_bins
        
        # Variables to track deviation above/below average
        for j in range(active_bins):
            deviation_vars[j] = solver.NumVar(0, data['bin_capacity'], f'dev_{j}')
    
    # Constraints
    # Each item must be assigned to exactly one bin
    for i in data['items']:
        solver.Add(sum(x[i, j] for j in data['bins']) == 1)
    
    for j in data['bins']:
        # Calculate bin fill for each bin
        solver.Add(bin_fill[j] == solver.Sum(x[i, j] * data['weights'][i] for i in data['items']))
        
        # For max_items and balance_bins, calculate item count for each bin
        if objective in ['max_items', 'balance_bins']:
            solver.Add(item_count[j] == solver.Sum(x[i, j] for i in data['items']))
        
        # Bin capacity constraint
        solver.Add(
            sum(x[i, j] * data['weights'][i] for i in data['items']) <= y[j] * data['bin_capacity']
        )
        
        # Only apply min_items constraint if bin is used
        if min_items_per_bin > 0:
            solver.Add(sum(x[i, j] for i in data['items']) >= y[j] * min_items_per_bin)
    
    # Additional constraints based on objective
    if objective in ['max_weight', 'max_items']:
        # Ensure bins are used in order
        for j in range(1, len(data['bins'])):
            # Bin j can only be used if bin j-1 is used
            solver.Add(y[j-1] >= y[j])
            
            if objective == 'max_weight':
                # For max_weight, previous bin should be filled to capacity before next bin
                threshold = 0.8 * data['bin_capacity']
                solver.Add(bin_fill[j-1] >= y[j] * threshold)
            elif objective == 'max_items':
                # For max_items, previous bin should have max items before next bin
                # Use a simpler constraint approach that doesn't use OnlyEnforceIf
                # Set a weight threshold and an item count threshold
                item_threshold = min(3, min_items_per_bin + 1)  # At least min_items + 1 or 3
                weight_threshold = 0.7 * data['bin_capacity']
                
                # Create a "softened" constraint: 
                # If bin j is used, either bin j-1 has enough items or enough weight
                # y[j] <= 1 - (item_count[j-1] < threshold) * (bin_fill[j-1] < weight_threshold)
                
                # We can linearize this with an indicator variable and big-M approach
                # The indicator will be true if bin j-1 has enough items or enough weight
                # M should be large enough to make the constraint always satisfied when y[j] = 0
                M = data['bin_capacity'] * 2  # Big-M constant
                
                # This constraint means: "if bin j is used, bin j-1 should be filled reasonably well"
                # Mathematically: y[j] ≤ max(item_count[j-1] / item_threshold, bin_fill[j-1] / weight_threshold)
                # We use a softened version since we can't directly encode the max() function
                
                # If bin j is used (y[j] = 1), enforce that bin j-1 has at least 70% weight fill
                solver.Add(bin_fill[j-1] >= y[j] * weight_threshold - M * (1 - y[j]))
    
    elif objective == 'balance_bins':
        # For balance_bins, we need to:
        # 1. Ensure we use exactly bin_count bins
        # 2. Minimize the deviation from the average weight
        
        # Use exactly the specified number of bins
        active_bins = min(bin_count, len(data['bins']))
        solver.Add(solver.Sum([y[j] for j in range(active_bins)]) == active_bins)
        
        # Force the remaining bins to be unused
        if active_bins < len(data['bins']):
            for j in range(active_bins, len(data['bins'])):
                solver.Add(y[j] == 0)
        
        # Calculate the target average weight per bin
        total_weight = sum(order_weights)
        avg_weight = total_weight / active_bins
        
        # Set up deviation variables
        for j in range(active_bins):
            # Define deviation as absolute difference from average
            # Using linearization of absolute value |bin_fill[j] - avg_weight|
            # deviation_vars[j] >= bin_fill[j] - avg_weight
            solver.Add(deviation_vars[j] >= bin_fill[j] - avg_weight)
            # deviation_vars[j] >= avg_weight - bin_fill[j]
            solver.Add(deviation_vars[j] >= avg_weight - bin_fill[j])
    
    # Objective function
    if objective == 'min_bins':
        solver.Minimize(solver.Sum([y[j] for j in data['bins']]))
    elif objective == 'max_weight':
        # Maximize total packed weight
        solver.Maximize(solver.Sum(x[i, j] * data['weights'][i] for i in data['items'] for j in data['bins']))
    elif objective == 'max_items':
        # First minimize number of bins, then maximize items in each bin
        # Multi-objective approach using weights
        bin_count_var = solver.Sum([y[j] for j in data['bins']])
        
        # Balance between fewer bins and more items per bin
        # Multi-objective weights - large negative weight for bins, positive for item counts
        solver.Minimize(1000 * bin_count_var - solver.Sum(
            item_count[j] * (len(data['bins']) - j) for j in data['bins']
        ))
    elif objective == 'balance_bins':
        # Minimize total deviation across all bins
        solver.Minimize(solver.Sum([deviation_vars[j] for j in range(active_bins)]))
    
    # Time limit for solving (10 seconds)
    solver.SetTimeLimit(10000)  # milliseconds
    
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        packed_bins = {}
        for j in data['bins']:
            if y[j].solution_value() > 0.5:  # Using > 0.5 to handle potential floating-point issues
                items_in_bin = [i for i in data['items'] if x[i, j].solution_value() > 0.5]
                if items_in_bin:  # Only add bins that have items
                    packed_bins[j] = items_in_bin
        
        # Check if no solution was found despite solver reporting success
        if not packed_bins:
            return None, "Could not find a valid solution that satisfies all constraints"
        
        warning_message = None
        if status == pywraplp.Solver.FEASIBLE:
            warning_message = "Found a solution, but it may not be optimal"
            
        # For balance_bins, calculate statistics on the balance achieved
        if objective == 'balance_bins' and packed_bins:
            bin_weights = [sum(order_weights[i] for i in items) for j, items in packed_bins.items()]
            avg_weight = sum(bin_weights) / len(bin_weights)
            max_deviation = max(abs(w - avg_weight) for w in bin_weights)
            max_deviation_pct = (max_deviation / avg_weight) * 100 if avg_weight > 0 else 0
            
            if max_deviation_pct > 20:  # If deviation is more than 20%
                if warning_message:
                    warning_message += f". Bins are not well balanced (max deviation: {max_deviation_pct:.1f}%)"
                else:
                    warning_message = f"Bins are not well balanced (max deviation: {max_deviation_pct:.1f}%)"
        
        return packed_bins, warning_message
    elif status == pywraplp.Solver.INFEASIBLE:
        return None, "The problem is infeasible. Try relaxing some constraints."
    elif status == pywraplp.Solver.UNBOUNDED:
        return None, "The problem is unbounded. Check your objective function."
    elif status == pywraplp.Solver.NOT_SOLVED:
        if solver.WallTime() >= 10000:
            return None, "Time limit exceeded. Try simplifying the problem or adjusting parameters."
        else:
            return None, "The problem could not be solved. Please check your inputs."
    else:
        return None, "Unknown solver status. Please try again with different parameters."

# Example usage
if __name__ == "__main__":
    order_weights = [10, 20, 30, 40, 50, 15, 25, 35]  # Example order weights
    bin_capacity = 60  # Example bin capacity
    objective = 'min_bins'  # Options: 'min_bins', 'max_weight', 'max_items', 'balance_bins'
    min_items_per_bin = 2  # Minimum number of items per bin
    bin_count = 3  # For 'balance_bins' objective
    result, error = solve_bin_packing(order_weights, bin_capacity, objective, min_items_per_bin, bin_count)
    if result:
        print("Packed Bins:", result)
        if error:
            print("Note:", error)
    else:
        print("Error:", error)
