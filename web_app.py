import os
import json
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from solver import solve_bin_packing

app = Flask(__name__)

# Ensure the configs directory exists
CONFIGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(CONFIGS_DIR, exist_ok=True)

# Store configs in a file
CONFIGS_FILE = os.path.join(CONFIGS_DIR, 'configs.json')
if not os.path.exists(CONFIGS_FILE):
    with open(CONFIGS_FILE, 'w') as f:
        json.dump([], f)

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/solve', methods=['POST'])
def api_solve():
    try:
        # Parse input data
        data = request.json
        weights = data.get('weights', [])
        bin_capacity = data.get('bin_capacity', 100)
        objective = data.get('objective', 'min_bins')
        min_items_per_bin = data.get('min_items_per_bin', 1)
        sort_method = data.get('sort_method', 'none')
        bin_count = data.get('bin_count', None)
        item_labels = data.get('item_labels', [])
        
        # Validate input
        if not weights:
            return jsonify({'error': 'No weights provided'}), 400
        
        if bin_capacity <= 0:
            return jsonify({'error': 'Bin capacity must be positive'}), 400
        
        if min_items_per_bin <= 0:
            return jsonify({'error': 'Minimum items per bin must be positive'}), 400
        
        if objective == 'balance_bins' and (not bin_count or bin_count <= 0):
            return jsonify({'error': 'Number of bins must be positive for balance_bins objective'}), 400
        
        # Apply sorting if specified
        original_weights = weights.copy()
        if sort_method == 'desc':
            # Sort weights in descending order
            indices = sorted(range(len(weights)), key=lambda i: weights[i], reverse=True)
            weights = [weights[i] for i in indices]
            # Reorder labels if present
            if item_labels:
                item_labels = [item_labels[i] for i in indices]
        elif sort_method == 'asc':
            # Sort weights in ascending order
            indices = sorted(range(len(weights)), key=lambda i: weights[i])
            weights = [weights[i] for i in indices]
            # Reorder labels if present
            if item_labels:
                item_labels = [item_labels[i] for i in indices]
        elif sort_method == 'random':
            # Random shuffle
            import random
            indices = list(range(len(weights)))
            random.shuffle(indices)
            weights = [weights[i] for i in indices]
            # Reorder labels if present
            if item_labels:
                item_labels = [item_labels[i] for i in indices]
        
        # Call the solver
        start_time = time.time()
        result = solve_bin_packing(
            weights,
            bin_capacity,
            objective,
            min_items_per_bin,
            bin_count,
            item_labels
        )
        
        # If result contains an error, return it
        if 'error' in result:
            return jsonify(result), 400
        
        # Calculate total weight
        total_weight = sum(sum(bin_data.get('item_weights', [])) for bin_data in result['bins'])
        
        # Add computation time
        result['computation_time'] = round(time.time() - start_time, 3)
        result['total_weight'] = total_weight
        
        # Add warning if needed
        if max(weights) > bin_capacity:
            result['warning'] = 'Some items exceed bin capacity and cannot be packed'
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Error in API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def api_compare():
    try:
        # Parse input data
        data = request.json
        weights = data.get('weights', [])
        bin_capacity = data.get('bin_capacity', 100)
        min_items_per_bin = data.get('min_items_per_bin', 1)
        sort_method = data.get('sort_method', 'none')
        bin_count = data.get('bin_count', 3)
        item_labels = data.get('item_labels', [])
        
        # Apply sorting if specified
        original_weights = weights.copy()
        if sort_method == 'desc':
            # Sort weights in descending order
            indices = sorted(range(len(weights)), key=lambda i: weights[i], reverse=True)
            weights = [weights[i] for i in indices]
            # Reorder labels if present
            if item_labels:
                item_labels = [item_labels[i] for i in indices]
        elif sort_method == 'asc':
            # Sort weights in ascending order
            indices = sorted(range(len(weights)), key=lambda i: weights[i])
            weights = [weights[i] for i in indices]
            # Reorder labels if present
            if item_labels:
                item_labels = [item_labels[i] for i in indices]
        elif sort_method == 'random':
            # Random shuffle
            import random
            indices = list(range(len(weights)))
            random.shuffle(indices)
            weights = [weights[i] for i in indices]
            # Reorder labels if present
            if item_labels:
                item_labels = [item_labels[i] for i in indices]
        
        # Compare different objectives
        objectives = ['min_bins', 'max_weight', 'max_items', 'balance_bins']
        results = {}
        
        for objective in objectives:
            # Skip balance_bins if bin_count is not valid
            if objective == 'balance_bins' and (not bin_count or bin_count <= 0):
                results[objective] = {
                    'success': False,
                    'error': 'Number of bins must be positive for balance_bins objective'
                }
                continue
            
            try:
                # Call the solver
                start_time = time.time()
                result = solve_bin_packing(
                    weights.copy(),
                    bin_capacity,
                    objective,
                    min_items_per_bin,
                    (bin_count if objective == 'balance_bins' else None),
                    item_labels.copy() if item_labels else []
                )
                
                # Check for solver error
                if 'error' in result:
                    results[objective] = {
                        'success': False,
                        'error': result['error']
                    }
                    continue
                
                # Calculate statistics
                bin_count = result['bin_count']
                total_weight = sum(sum(bin_data.get('item_weights', [])) for bin_data in result['bins'])
                avg_fill_ratio = sum(bin_data['total_weight'] / bin_data['capacity'] for bin_data in result['bins']) / bin_count
                
                # Store results
                results[objective] = {
                    'success': True,
                    'bin_count': bin_count,
                    'total_weight': total_weight,
                    'avg_fill_ratio': avg_fill_ratio,
                    'computation_time': round(time.time() - start_time, 3),
                    'bins': result['bins']
                }
                
                # Add warning if needed
                if max(weights) > bin_capacity:
                    results[objective]['warning'] = 'Some items exceed bin capacity'
                
            except Exception as e:
                results[objective] = {
                    'success': False,
                    'error': str(e)
                }
        
        return jsonify({'results': results})
    
    except Exception as e:
        app.logger.error(f"Error in comparison API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_config', methods=['POST'])
def api_save_config():
    try:
        # Parse input data
        data = request.json
        
        # Load existing configs
        with open(CONFIGS_FILE, 'r') as f:
            configs = json.load(f)
        
        # Add timestamp
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add to configs
        configs.append(data)
        
        # Save configs
        with open(CONFIGS_FILE, 'w') as f:
            json.dump(configs, f, indent=2)
        
        return jsonify({'success': True})
    
    except Exception as e:
        app.logger.error(f"Error saving config: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/load_configs', methods=['GET'])
def api_load_configs():
    try:
        # Load configs
        with open(CONFIGS_FILE, 'r') as f:
            configs = json.load(f)
        
        # Sort by timestamp (newest first)
        configs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({'configs': configs})
    
    except Exception as e:
        app.logger.error(f"Error loading configs: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 