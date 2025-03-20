from flask import Flask, render_template, request, jsonify
import json
from solver import solve_bin_packing
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/solve', methods=['POST'])
def solve():
    try:
        data = request.json
        
        # Parse input data
        weights = data.get('weights', [])
        bin_capacity = data.get('bin_capacity', 0)
        objective = data.get('objective', 'min_bins')
        min_items_per_bin = data.get('min_items_per_bin', 1)
        
        # New parameters
        sort_method = data.get('sort_method', 'none')
        bin_count = data.get('bin_count', 3)
        item_labels = data.get('item_labels', [])
        
        # Validate inputs
        if not weights:
            return jsonify({"error": "Please enter at least one weight"}), 400
                
        if bin_capacity <= 0:
            return jsonify({"error": "Bin capacity must be positive"}), 400
                
        if min_items_per_bin <= 0:
            return jsonify({"error": "Minimum items per bin must be positive"}), 400
        
        if objective == 'balance_bins' and (bin_count is None or bin_count < 2):
            return jsonify({"error": "For balanced bins, you must specify at least 2 bins"}), 400
        
        # Apply sorting if requested
        if sort_method != 'none':
            # Create a list of (index, weight) tuples to preserve original indices
            indexed_weights = list(enumerate(weights))
            
            if sort_method == 'desc':
                # Sort descending by weight
                indexed_weights.sort(key=lambda x: x[1], reverse=True)
            elif sort_method == 'asc':
                # Sort ascending by weight
                indexed_weights.sort(key=lambda x: x[1])
            elif sort_method == 'random':
                # Random shuffle
                random.shuffle(indexed_weights)
            
            # Extract the original indices and the sorted weights
            original_indices = [idx for idx, _ in indexed_weights]
            sorted_weights = [weight for _, weight in indexed_weights]
            
            # Map original item labels to new positions if provided
            if item_labels and len(item_labels) == len(weights):
                sorted_labels = [item_labels[idx] for idx in original_indices]
            else:
                sorted_labels = None
                
            # Use sorted weights for solving
            solver_weights = sorted_weights
            solver_labels = sorted_labels
        else:
            # No sorting, use original weights and labels
            solver_weights = weights
            original_indices = list(range(len(weights)))
            solver_labels = item_labels if item_labels and len(item_labels) == len(weights) else None
        
        # Solve the problem
        result, error_message = solve_bin_packing(
            solver_weights, 
            bin_capacity, 
            objective, 
            min_items_per_bin,
            bin_count if objective == 'balance_bins' else None,
            solver_labels
        )
        
        if result is None:
            detailed_error = error_message or "No solution found. Try adjusting parameters."
            return jsonify({"error": detailed_error}), 400
        
        # Process results - map back to original indices if sorting was applied
        processed_result = []
        
        for bin_id, items in result.items():
            # Get original item indices if sorting was applied
            original_item_indices = [original_indices[i] for i in items]
            
            # Get item weights
            item_weights = [weights[i] for i in original_item_indices]
            
            # Get item labels if available
            item_label_values = None
            if item_labels and len(item_labels) >= len(weights):
                item_label_values = [item_labels[i] for i in original_item_indices]
            
            bin_weight = sum(item_weights)
            fill_ratio = bin_weight / bin_capacity
            
            bin_data = {
                "bin_id": bin_id,
                "items": original_item_indices,
                "item_weights": item_weights,
                "total_weight": bin_weight,
                "capacity": bin_capacity,
                "fill_ratio": fill_ratio
            }
            
            # Add labels if available
            if item_label_values:
                bin_data["item_labels"] = item_label_values
                
            processed_result.append(bin_data)
            
        response_data = {
            "success": True,
            "bins": processed_result,
            "bin_count": len(result),
            "total_weight": sum(weights),
            "sort_method": sort_method
        }
        
        # Include warning message if one was returned
        if error_message:
            response_data["warning"] = error_message
            
        return jsonify(response_data)
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_strategies():
    try:
        data = request.json
        
        # Parse input data
        weights = data.get('weights', [])
        bin_capacity = data.get('bin_capacity', 0)
        min_items_per_bin = data.get('min_items_per_bin', 1)
        sort_method = data.get('sort_method', 'none')
        bin_count = data.get('bin_count', 3)
        item_labels = data.get('item_labels', [])
        
        # Validate inputs
        if not weights:
            return jsonify({"error": "Please enter at least one weight"}), 400
                
        if bin_capacity <= 0:
            return jsonify({"error": "Bin capacity must be positive"}), 400
                
        if min_items_per_bin <= 0:
            return jsonify({"error": "Minimum items per bin must be positive"}), 400
        
        # Define strategies to compare
        strategies = ['min_bins', 'max_weight', 'max_items', 'balance_bins']
        results = {}
        
        # Apply sorting if requested
        if sort_method != 'none':
            # Create a list of (index, weight) tuples to preserve original indices
            indexed_weights = list(enumerate(weights))
            
            if sort_method == 'desc':
                # Sort descending by weight
                indexed_weights.sort(key=lambda x: x[1], reverse=True)
            elif sort_method == 'asc':
                # Sort ascending by weight
                indexed_weights.sort(key=lambda x: x[1])
            elif sort_method == 'random':
                # Random shuffle
                random.shuffle(indexed_weights)
            
            # Extract the original indices and the sorted weights
            original_indices = [idx for idx, _ in indexed_weights]
            sorted_weights = [weight for _, weight in indexed_weights]
            
            # Map original item labels to new positions if provided
            if item_labels and len(item_labels) == len(weights):
                sorted_labels = [item_labels[idx] for idx in original_indices]
            else:
                sorted_labels = None
                
            # Use sorted weights for solving
            solver_weights = sorted_weights
            solver_labels = sorted_labels
        else:
            # No sorting, use original weights and labels
            solver_weights = weights
            original_indices = list(range(len(weights)))
            solver_labels = item_labels if item_labels and len(item_labels) == len(weights) else None
        
        # Run each strategy
        for strategy in strategies:
            # Skip balance_bins if bin_count is not valid
            if strategy == 'balance_bins' and (bin_count is None or bin_count < 2):
                results[strategy] = {
                    "error": "For balanced bins, you must specify at least 2 bins",
                    "success": False
                }
                continue
                
            # Solve with current strategy
            result, error_message = solve_bin_packing(
                solver_weights, 
                bin_capacity, 
                strategy, 
                min_items_per_bin,
                bin_count if strategy == 'balance_bins' else None,
                solver_labels
            )
            
            if result is None:
                results[strategy] = {
                    "error": error_message or "No solution found",
                    "success": False
                }
                continue
                
            # Process results - map back to original indices
            processed_result = []
            
            for bin_id, items in result.items():
                # Get original item indices
                original_item_indices = [original_indices[i] for i in items]
                
                # Get item weights
                item_weights = [weights[i] for i in original_item_indices]
                
                # Get item labels if available
                item_label_values = None
                if item_labels and len(item_labels) >= len(weights):
                    item_label_values = [item_labels[i] for i in original_item_indices]
                
                bin_weight = sum(item_weights)
                fill_ratio = bin_weight / bin_capacity
                
                bin_data = {
                    "bin_id": bin_id,
                    "items": original_item_indices,
                    "item_weights": item_weights,
                    "total_weight": bin_weight,
                    "capacity": bin_capacity,
                    "fill_ratio": fill_ratio
                }
                
                # Add labels if available
                if item_label_values:
                    bin_data["item_labels"] = item_label_values
                    
                processed_result.append(bin_data)
                
            # Calculate statistics
            bin_count = len(result)
            total_weight = sum(weights)
            avg_fill = sum(bin_data["fill_ratio"] for bin_data in processed_result) / bin_count if bin_count > 0 else 0
            
            # Store the results
            results[strategy] = {
                "success": True,
                "bins": processed_result,
                "bin_count": bin_count,
                "total_weight": total_weight,
                "avg_fill_ratio": avg_fill,
                "warning": error_message
            }
            
        return jsonify({
            "success": True,
            "results": results,
            "sort_method": sort_method
        })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/save_config', methods=['POST'])
def save_config():
    try:
        # Get configuration from request
        config = request.json
        
        # Generate a filename based on timestamp
        filename = f"config_{config.get('bin_capacity')}_{len(config.get('weights', []))}.json"
        
        # Save to file
        with open(f"./configs/{filename}", 'w') as f:
            json.dump(config, f, indent=2)
            
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/load_configs', methods=['GET'])
def load_configs():
    import os
    import glob
    
    try:
        # List all config files
        config_files = glob.glob("./configs/*.json")
        configs = []
        
        for file_path in config_files:
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                    config['filename'] = os.path.basename(file_path)
                    configs.append(config)
            except:
                pass
                
        return jsonify({"success": True, "configs": configs})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/load_config/<filename>', methods=['GET'])
def load_config(filename):
    try:
        with open(f"./configs/{filename}", 'r') as f:
            config = json.load(f)
            
        return jsonify({"success": True, "config": config})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    import os
    # Create configs directory if it doesn't exist
    os.makedirs('./configs', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True) 