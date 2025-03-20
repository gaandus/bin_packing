# Bin Packing Visualization

An interactive web application for solving and visualizing bin packing problems using Google OR-Tools.

## Features

- Multiple objective modes:
  - **Minimize Bins**: Use the fewest number of bins possible (classic bin packing)
  - **Maximize Weight**: Fill each bin with as much weight as possible
  - **Maximize Items**: Put as many items as possible in each bin
  - **Balance Bins**: Evenly distribute weight across a fixed number of bins
- Interactive visualization of bin packing results
- Save and load configurations
- Random weight generator
- Item sorting options (descending, ascending, random)
- Item labels for better identification
- Strategy comparison to see how different objectives perform
- Mobile-responsive design with dark mode
- Configuration saving and loading
- Vertical bin stacking for better visibility on all devices
- Back to top button for easy navigation

## How It Works

### Solver Implementation

The bin packing solver uses Google OR-Tools' mixed-integer programming (MIP) capabilities to find optimal solutions:

1. **Mathematical Formulation**:
   - **Decision Variables**:
     - x[i,j] = 1 if item i is placed in bin j, 0 otherwise
     - y[j] = 1 if bin j is used, 0 otherwise
   - **Constraints**:
     - Each item must be assigned to exactly one bin
     - The total weight in each bin cannot exceed its capacity
     - Each used bin must contain at least the minimum required items
     - For the balance_bins objective, deviation from average weight is tracked

2. **Objective Functions**:
   - **min_bins**: Minimize the sum of y[j] (number of bins used)
   - **max_weight**: Maximize weight utilization in each bin before using another
   - **max_items**: Maximize the number of items in each bin before using another
   - **balance_bins**: Minimize the deviation from the average weight across a fixed number of bins

3. **Optimization Process**:
   - The solver first creates a model with necessary variables and constraints
   - For each objective type, different constraints and optimization goals are set
   - The OR-Tools SCIP solver is invoked to find the optimal solution
   - Results are processed and returned in a structured format for visualization

### Application Architecture

The application follows a simple structure:

- **solver.py**: Contains the core bin packing algorithm implementation
- **web_app.py**: Flask application that handles HTTP requests and connects the frontend to the solver
- **templates/index.html**: The main user interface for the application
- **static/js/app.js**: Client-side JavaScript for user interactions and visualizations
- **static/css/style.css**: Styling for the application, with responsive design

### Data Flow

1. User inputs item weights, bin capacity, and objective on the web interface
2. The Flask backend processes the request and calls the solver function
3. The solver creates and solves the mathematical model using OR-Tools
4. Results are returned to the frontend as JSON data
5. JavaScript code processes the results and creates the visual representation
6. Bin packing visualization shows how items are distributed across bins

The application uses JSON for data storage and communication between components, making it easy to save and load configurations.

## Requirements

- Python 3.9+
- Flask
- Google OR-Tools
- Modern web browser

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/bin-packing.git
   cd bin-packing
   ```

2. Build and run with Docker:
   ```
   docker build -t bin-packing .
   docker run -p 5000:5000 -v $(pwd)/data:/app/data bin-packing
   ```

3. Open your browser and navigate to `http://localhost:5000`

### Manual Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/bin-packing.git
   cd bin-packing
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python web_app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Enter item weights separated by commas
2. Set the bin capacity
3. Choose an objective function
4. Click "Solve" to see the visualization
5. Optionally save your configuration for later use

### Random Weight Generator

Generate random weights for testing:
1. Click "Random Weights"
2. Set count, min weight, max weight
3. Choose whether to include labels
4. Click "Generate"

### Item Sorting

Sort items before packing to see how different orders affect the result:
1. Choose a sort method: None, Descending, Ascending, Random
2. Solve to see the impact

### Strategy Comparison

Compare how different objectives perform on the same problem:
1. Set up your bin packing problem
2. Click "Compare Strategies"
3. View side-by-side results of all objectives

## Deployment

### Docker Deployment

For production deployment, you can use the included Docker configuration:

```
docker build -t bin-packing .
docker run -d --name bin-packing --restart always -p 127.0.0.1:5000:5000 -v $(pwd)/data:/app/data bin-packing
```

### Nginx Configuration

To serve the application behind Nginx:

```
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Advanced Usage Examples

### Objective Selection Guide

Choose the right objective based on your specific use case:

1. **Minimize Bins (min_bins)**
   - **Use case**: Shipping boxes where you want to use as few containers as possible
   - **Example**: Packing items with weights [10, 15, 20, 25, 30, 35, 40] into bins with capacity 70
   - **Result**: The solver will use the minimum number of bins, prioritizing tight packing
   - **Real-world application**: E-commerce order fulfillment, reducing shipping costs

2. **Maximize Weight (max_weight)**
   - **Use case**: Loading trucks or containers where you want to maximize utilization
   - **Example**: Loading a truck with capacity 1000 kg with packages of varying weights
   - **Result**: The solver will maximize the weight in each bin before using another
   - **Real-world application**: Freight transport, maximizing cargo utilization

3. **Maximize Items (max_items)**
   - **Use case**: When you want to put as many distinct items as possible in each bin
   - **Example**: Grouping small components into assembly kits or packaging
   - **Result**: Each bin will contain as many items as possible before creating a new bin
   - **Real-world application**: Assembly line provisioning, creating balanced work packages

4. **Balance Bins (balance_bins)**
   - **Use case**: When you need to distribute weight evenly across a fixed number of bins
   - **Example**: Distributing workload among 3 teams, with tasks of different weights
   - **Result**: The solver will minimize the weight difference between bins
   - **Real-world application**: Workload balancing, meal prep planning, team task assignment

### Example Scenarios

**Scenario 1: Shipping Optimization**
- Weights: [22, 35, 17, 28, 19, 26, 35, 22, 16, 18, 31, 24]
- Bin Capacity: 70
- Objective: min_bins
- This minimizes the number of shipping boxes needed while ensuring no box exceeds weight limits.

**Scenario 2: Assembly Kits**
- Weights: [5, 3, 8, 4, 6, 2, 7, 3, 5, 4, 9, 6, 3, 2, 5]
- Bin Capacity: 20
- Objective: max_items
- Sort Method: descending
- This creates assembly kits with as many parts as possible, starting with the heaviest components.

**Scenario 3: Team Workload Distribution**
- Weights: [15, 8, 20, 12, 17, 9, 14, 11, 19, 16]
- Bin Capacity: 50
- Objective: balance_bins
- Bin Count: 3
- This distributes tasks among three teams as evenly as possible.

## Performance Considerations

### Algorithm Complexity

Bin packing is an NP-hard problem, meaning:

- As the number of items increases, the computation time can grow exponentially
- Optimal solutions for large datasets may take significant time to compute
- The application uses the following strategies to manage complexity:

### Optimization Techniques

1. **Early Termination**: The solver is configured to return a good solution within a reasonable time frame rather than waiting indefinitely for the absolute optimal solution

2. **Preprocessing**:
   - Sorting items by weight (descending/ascending) can significantly improve solver performance
   - Items larger than bin capacity are automatically identified and excluded from packing attempts

3. **Problem Size Guidelines**:
   - Small problems (up to 50 items): Usually solved within seconds
   - Medium problems (50-100 items): May take several seconds to a minute
   - Large problems (100+ items): May take several minutes or more
   - Very large problems (500+ items): Consider breaking into smaller batches

### Memory Usage

- The solver's memory requirements scale with the number of items and potential bins
- For each item and potential bin, the solver creates binary variables and constraints
- A problem with n items and m potential bins requires O(n×m) variables and constraints

### Browser Performance

- Visualization performance may degrade with a very large number of bins or items
- The vertical stacking layout helps maintain usability even with many bins
- For extremely large problems, consider using the application in a desktop environment

## License

[MIT License](LICENSE) 