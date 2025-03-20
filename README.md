# Bin Packing Solver

A simple graphical user interface for solving bin packing problems using the OR-Tools library.

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

## Requirements

### For Local Run
- Python 3.6 or higher
- Required packages: 
  - `ortools` (installed automatically if missing)
  - `tkinter` (included in standard Python)

### For Docker Run
- Docker
- Docker Compose
- X11 server (for GUI display):
  - Windows: VcXsrv or Xming
  - macOS: XQuartz
  - Linux: Built-in X server

## Usage

### Running Locally

1. Run the application:
   ```
   python gui.py
   ```

2. Enter the item weights as comma-separated values (e.g., "10, 20, 30, 40")
3. Set the bin capacity (maximum weight per bin)
4. Choose the objective:
   - **Minimize Bins**: Use as few bins as possible
   - **Maximize Weight**: Pack as much weight as possible
5. Set the minimum items per bin (optional, default is 1)
6. Click "Solve" to find the solution
7. View the results in the Text Results tab or see the visualization in the Visualization tab

### Saving and Loading Configurations

- Click "Save Config" to save your current problem settings to a JSON file
- Click "Load Config" to load a previously saved configuration

This feature allows you to reuse common problem configurations without having to re-enter all the values.

### Running with Docker

1. Run the provided script:
   ```
   ./run.sh
   ```

This will:
- Check for Docker and Docker Compose installation
- Configure display settings based on your OS
- Build and start the Docker container
- Launch the bin packing application

#### Troubleshooting Docker GUI

- **Windows**: Ensure VcXsrv or Xming is running with "Disable access control" checked
- **macOS**: Run `xhost +` before starting the container
- **Linux**: Run `xhost +local:docker` before starting the container

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