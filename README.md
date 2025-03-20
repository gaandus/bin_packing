# Bin Packing Solver

A web application for solving bin packing problems using the OR-Tools library.

## Overview

This application helps you solve bin packing problems by arranging items of different weights into bins of fixed capacity. The goal is typically to use as few bins as possible or to maximize the weight packed into bins.

## Features

- Input weights for multiple items
- Set bin capacity
- Choose objective: minimize bins or maximize weight
- Set minimum items per bin constraint
- Visual representation of the packing solution
- Detailed text output of the solution
- Save and load problem configurations
- Docker support
- Web-based UI accessible from any browser

## Requirements

### For Local Run
- Python 3.6 or higher
- Required packages: 
  - `ortools`
  - `flask`

### For Docker Run
- Docker

## Usage

### Running Locally

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

2. Run the web application:
   ```
   python web_app.py
   ```

3. Open your browser and navigate to `http://localhost:5000`

### Running with Docker

1. Run the provided script:
   ```
   # Linux/macOS
   ./run.sh
   
   # Windows
   run_windows.bat
   ```

This will:
- Build the Docker container
- Start the web application on port 5000
- Automatically open your browser to the application

## Using the Application

1. Enter the item weights as comma-separated values (e.g., "10, 20, 30, 40")
2. Set the bin capacity (maximum weight per bin)
3. Choose the objective:
   - **Minimize Bins**: Use as few bins as possible
   - **Maximize Weight**: Pack as much weight as possible
4. Set the minimum items per bin (optional, default is 1)
5. Click "Solve" to find the solution
6. View the results, including:
   - Text summary with bin count and fill rates
   - Visual representation of bins and items
   - Detailed bin-by-bin breakdown

### Saving and Loading Configurations

- Click "Save Config" to save your current problem settings
- Click "Load Config" to load a previously saved configuration

## Example

Input:
- Order Weights: 10, 20, 30, 40, 50, 15, 25, 35
- Bin Capacity: 60
- Objective: Minimize Bins
- Min Items Per Bin: 2

This will pack the items into bins such that:
- Each bin contains at most 60 weight units
- Each bin contains at least 2 items
- The solution uses the minimum possible number of bins

## How the Solver Works

The application uses Google's OR-Tools library to solve the bin packing problem as a mixed-integer programming (MIP) problem. The mathematical formulation:

- Decision variables:
  - x[i,j] = 1 if item i is placed in bin j, 0 otherwise
  - y[j] = 1 if bin j is used, 0 otherwise

- Constraints:
  - Each item must be placed in exactly one bin
  - The total weight in each bin must not exceed the bin capacity
  - Each used bin must contain at least the minimum number of items

- Objective:
  - Minimize the number of bins used (min_bins)
  - OR: Maximize the total weight packed (max_weight) 