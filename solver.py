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

def solve_bin_packing(order_weights, bin_capacity, objective='min_bins', min_items_per_bin=1):
    """Solves the bin packing problem using OR-Tools.
    objective: 'min_bins' to minimize the number of bins, 'max_weight' to maximize the packed weight.
    min_items_per_bin: Minimum number of items that must be in each used bin.
    """
    data = create_data_model(order_weights, bin_capacity)
    
    # Create the solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return None
    
    # Variables
    x = {}
    for i in data['items']:
        for j in data['bins']:
            x[(i, j)] = solver.IntVar(0, 1, f'x_{i}_{j}')
    
    y = {j: solver.IntVar(0, 1, f'y[{j}]') for j in data['bins']}
    
    # Constraints
    for i in data['items']:
        solver.Add(sum(x[i, j] for j in data['bins']) == 1)
    
    for j in data['bins']:
        solver.Add(
            sum(x[i, j] * data['weights'][i] for i in data['items']) <= y[j] * data['bin_capacity']
        )
        solver.Add(sum(x[i, j] for i in data['items']) >= y[j] * min_items_per_bin)
    
    # Objective
    if objective == 'min_bins':
        solver.Minimize(solver.Sum([y[j] for j in data['bins']]))
    elif objective == 'max_weight':
        solver.Maximize(solver.Sum(x[i, j] * data['weights'][i] for i in data['items'] for j in data['bins']))
    
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        packed_bins = {}
        for j in data['bins']:
            if y[j].solution_value() == 1:
                packed_bins[j] = [i for i in data['items'] if x[i, j].solution_value() > 0]
        return packed_bins
    else:
        return None

# Example usage
if __name__ == "__main__":
    order_weights = [10, 20, 30, 40, 50, 15, 25, 35]  # Example order weights
    bin_capacity = 60  # Example bin capacity
    objective = 'min_bins'  # Change to 'max_weight' to maximize weight
    min_items_per_bin = 2  # Minimum number of items per bin
    result = solve_bin_packing(order_weights, bin_capacity, objective, min_items_per_bin)
    print("Packed Bins:", result)
