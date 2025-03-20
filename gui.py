import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import random
import os
from solver import solve_bin_packing

class BinPackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bin Packing Solver")
        self.root.geometry("1000x700")
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input Parameters", padding="10")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Weights input
        ttk.Label(input_frame, text="Order Weights (comma-separated):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.weights_entry = ttk.Entry(input_frame, width=50)
        self.weights_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.weights_entry.insert(0, "10, 20, 30, 40, 50, 15, 25, 35")
        
        # Bin capacity
        ttk.Label(input_frame, text="Bin Capacity:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.capacity_entry = ttk.Entry(input_frame, width=10)
        self.capacity_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.capacity_entry.insert(0, "60")
        
        # Objective
        ttk.Label(input_frame, text="Objective:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.objective_var = tk.StringVar(value="min_bins")
        objective_frame = ttk.Frame(input_frame)
        objective_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(objective_frame, text="Minimize Bins", variable=self.objective_var, value="min_bins").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(objective_frame, text="Maximize Weight", variable=self.objective_var, value="max_weight").pack(side=tk.LEFT, padx=5)
        
        # Min items per bin
        ttk.Label(input_frame, text="Min Items Per Bin:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.min_items_entry = ttk.Entry(input_frame, width=10)
        self.min_items_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.min_items_entry.insert(0, "1")
        
        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Solve button
        solve_button = ttk.Button(buttons_frame, text="Solve", command=self.solve)
        solve_button.pack(side=tk.LEFT, padx=5)
        
        # Save config button
        save_button = ttk.Button(buttons_frame, text="Save Config", command=self.save_config)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Load config button
        load_button = ttk.Button(buttons_frame, text="Load Config", command=self.load_config)
        load_button.pack(side=tk.LEFT, padx=5)
        
        # Results section - split into tabs
        results_notebook = ttk.Notebook(main_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text results tab
        text_frame = ttk.Frame(results_notebook, padding="10")
        results_notebook.add(text_frame, text="Text Results")
        
        self.results_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Visualization tab
        viz_frame = ttk.Frame(results_notebook, padding="10")
        results_notebook.add(viz_frame, text="Visualization")
        
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(viz_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", xscrollcommand=h_scrollbar.set)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Configure the scrollbar
        h_scrollbar.config(command=self.canvas.xview)
    
    def get_current_config(self):
        """Get current configuration from the UI fields"""
        weights_str = self.weights_entry.get().strip()
        weights = [int(w.strip()) for w in weights_str.split(',')]
        
        config = {
            "weights": weights,
            "bin_capacity": int(self.capacity_entry.get()),
            "objective": self.objective_var.get(),
            "min_items_per_bin": int(self.min_items_entry.get())
        }
        return config
    
    def set_config(self, config):
        """Set UI fields from the given configuration"""
        self.weights_entry.delete(0, tk.END)
        self.weights_entry.insert(0, ", ".join(str(w) for w in config["weights"]))
        
        self.capacity_entry.delete(0, tk.END)
        self.capacity_entry.insert(0, str(config["bin_capacity"]))
        
        self.objective_var.set(config["objective"])
        
        self.min_items_entry.delete(0, tk.END)
        self.min_items_entry.insert(0, str(config["min_items_per_bin"]))
    
    def save_config(self):
        """Save current configuration to a JSON file"""
        try:
            config = self.get_current_config()
            
            # Ask for filename
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Configuration"
            )
            
            if not filename:
                return  # User cancelled
            
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
                
            messagebox.showinfo("Success", f"Configuration saved to {os.path.basename(filename)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def load_config(self):
        """Load configuration from a JSON file"""
        try:
            # Ask for filename
            filename = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Configuration"
            )
            
            if not filename:
                return  # User cancelled
            
            with open(filename, 'r') as f:
                config = json.load(f)
            
            self.set_config(config)
            messagebox.showinfo("Success", f"Configuration loaded from {os.path.basename(filename)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
        
    def solve(self):
        try:
            config = self.get_current_config()
            weights = config["weights"]
            bin_capacity = config["bin_capacity"]
            objective = config["objective"]
            min_items = config["min_items_per_bin"]
            
            # Validate inputs
            if not weights:
                messagebox.showerror("Error", "Please enter at least one weight")
                return
                
            if bin_capacity <= 0:
                messagebox.showerror("Error", "Bin capacity must be positive")
                return
                
            if min_items <= 0:
                messagebox.showerror("Error", "Minimum items per bin must be positive")
                return
            
            # Solve the problem
            result = solve_bin_packing(weights, bin_capacity, objective, min_items)
            
            # Display text results
            self.results_text.delete(1.0, tk.END)
            
            if result is None:
                self.results_text.insert(tk.END, "No solution found. Try adjusting parameters.")
                return
            else:
                self.results_text.insert(tk.END, f"Solution found with {len(result)} bins:\n\n")
                
                for bin_id, items in result.items():
                    bin_weight = sum(weights[i] for i in items)
                    items_str = ", ".join(str(i) for i in items)
                    weights_str = ", ".join(str(weights[i]) for i in items)
                    
                    self.results_text.insert(tk.END, f"Bin {bin_id+1}:\n")
                    self.results_text.insert(tk.END, f"  Item indices: {items_str}\n")
                    self.results_text.insert(tk.END, f"  Item weights: {weights_str}\n")
                    self.results_text.insert(tk.END, f"  Total weight: {bin_weight} / {bin_capacity}\n")
                    self.results_text.insert(tk.END, f"  Fill rate: {bin_weight/bin_capacity*100:.1f}%\n\n")
            
            # Display visualization
            self.draw_bins(result, weights, bin_capacity)
        
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def draw_bins(self, bins, weights, bin_capacity):
        # Clear canvas
        self.canvas.delete("all")
        
        if not bins:
            return
            
        # Define drawing parameters
        bin_width = 100
        bin_height = 300
        bin_spacing = 40
        margin = 50
        
        # Generate colors for items
        colors = []
        for _ in range(len(weights)):
            r = random.randint(100, 240)
            g = random.randint(100, 240)
            b = random.randint(100, 240)
            colors.append(f"#{r:02x}{g:02x}{b:02x}")
        
        # Draw each bin
        for i, (bin_id, items) in enumerate(bins.items()):
            x = margin + i * (bin_width + bin_spacing)
            y = margin
            
            # Draw bin outline
            self.canvas.create_rectangle(x, y, x + bin_width, y + bin_height, 
                                        outline="black", width=2)
            
            # Draw bin capacity label
            self.canvas.create_text(x + bin_width//2, y - 20, 
                                   text=f"Bin {bin_id+1}", 
                                   font=("Arial", 10, "bold"))
            
            # Draw items in bin
            current_height = 0
            for item in items:
                item_weight = weights[item]
                item_height = (item_weight / bin_capacity) * bin_height
                
                # Draw item rectangle
                item_y = y + bin_height - current_height - item_height
                self.canvas.create_rectangle(
                    x, item_y,
                    x + bin_width, y + bin_height - current_height,
                    fill=colors[item], outline="black"
                )
                
                # Draw item label
                if item_height > 20:  # Only show label if there's enough space
                    self.canvas.create_text(
                        x + bin_width//2, item_y + item_height//2,
                        text=f"Item {item}\n({item_weight})",
                        font=("Arial", 8), fill="black"
                    )
                
                current_height += item_height
            
            # Draw fill level
            total_weight = sum(weights[i] for i in items)
            fill_ratio = total_weight / bin_capacity
            fill_text = f"{fill_ratio:.1%}"
            self.canvas.create_text(
                x + bin_width//2, y + bin_height + 15,
                text=f"Fill: {fill_text}",
                font=("Arial", 9)
            )
        
        # Resize canvas scrollregion to fit all bins
        total_width = margin * 2 + len(bins) * (bin_width + bin_spacing)
        total_height = bin_height + margin * 2
        self.canvas.config(scrollregion=(0, 0, total_width, total_height))

if __name__ == "__main__":
    root = tk.Tk()
    app = BinPackingApp(root)
    root.mainloop() 