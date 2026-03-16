import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

# Import the simulation functions from simulationtest.py
import sys
sys.path.insert(0, r'c:\Users\sahil\Documents\Python programing')
from simulationtest import (
    generate_incidents, simulate_mode, run_experiment,
    INCIDENT_TYPES, SEVERITIES
)

class SimulationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Security Incident Simulation GUI")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Configuration variables
        self.n_incidents = tk.IntVar(value=400)
        self.n_runs = tk.IntVar(value=30)
        self.low_severity = tk.DoubleVar(value=45)
        self.med_severity = tk.DoubleVar(value=35)
        self.high_severity = tk.DoubleVar(value=20)
        self.selected_scenario = tk.StringVar(value="2")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Create the GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Security Incident Simulation",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Scenario selection frame
        scenario_frame = ttk.LabelFrame(main_frame, text="Select Scenario", padding=10)
        scenario_frame.pack(fill=tk.X, pady=10)
        
        scenarios = {
            "1": "Small Test (50 incidents, 5 runs)",
            "2": "Standard (400 incidents, 30 runs)",
            "3": "High Severity (400 incidents, high severity focus)",
            "4": "Large Scale (1000 incidents, 50 runs)",
            "5": "Custom (define your own)",
        }
        
        for key, desc in scenarios.items():
            rb = ttk.Radiobutton(
                scenario_frame,
                text=desc,
                variable=self.selected_scenario,
                value=key,
                command=self.on_scenario_change
            )
            rb.pack(anchor=tk.W, pady=5)
        
        # Custom parameters frame
        self.custom_frame = ttk.LabelFrame(main_frame, text="Custom Parameters", padding=10)
        self.custom_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Incidents
        ttk.Label(self.custom_frame, text="Number of Incidents:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.custom_frame, textvariable=self.n_incidents, width=15).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Runs
        ttk.Label(self.custom_frame, text="Number of Runs:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.custom_frame, textvariable=self.n_runs, width=15).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Severity Distribution
        ttk.Label(self.custom_frame, text="Severity Distribution:", font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(15, 5))
        
        ttk.Label(self.custom_frame, text="Low (%):", foreground="green").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.custom_frame, textvariable=self.low_severity, width=15).grid(row=3, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(self.custom_frame, text="Medium (%):", foreground="orange").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.custom_frame, textvariable=self.med_severity, width=15).grid(row=4, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(self.custom_frame, text="High (%):", foreground="red").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.custom_frame, textvariable=self.high_severity, width=15).grid(row=5, column=1, sticky=tk.W, padx=5)
        
        # Total percentage display
        self.total_label = ttk.Label(self.custom_frame, text="Total: 100%", foreground="blue")
        self.total_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Bind changes to update total (use trace_add for modern Tcl)
        try:
            self.low_severity.trace_add('write', self.update_total)
            self.med_severity.trace_add('write', self.update_total)
            self.high_severity.trace_add('write', self.update_total)
        except:
            # Fallback for older Python/Tcl versions
            self.low_severity.trace('w', self.update_total)
            self.med_severity.trace('w', self.update_total)
            self.high_severity.trace('w', self.update_total)
        
        # Disable custom frame initially
        self.set_custom_frame_state("disabled")
        
        # Run button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        self.run_button = ttk.Button(
            button_frame,
            text="Run Simulation",
            command=self.run_simulation
        )
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Exit",
            command=self.root.quit
        ).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="blue")
        self.status_label.pack(pady=10)
        
    def on_scenario_change(self):
        """Handle scenario selection change"""
        scenario = self.selected_scenario.get()
        
        if scenario == "1":
            self.n_incidents.set(50)
            self.n_runs.set(5)
            self.low_severity.set(60)
            self.med_severity.set(30)
            self.high_severity.set(10)
            self.set_custom_frame_state("disabled")
        elif scenario == "2":
            self.n_incidents.set(400)
            self.n_runs.set(30)
            self.low_severity.set(45)
            self.med_severity.set(35)
            self.high_severity.set(20)
            self.set_custom_frame_state("disabled")
        elif scenario == "3":
            self.n_incidents.set(400)
            self.n_runs.set(30)
            self.low_severity.set(20)
            self.med_severity.set(35)
            self.high_severity.set(45)
            self.set_custom_frame_state("disabled")
        elif scenario == "4":
            self.n_incidents.set(1000)
            self.n_runs.set(50)
            self.low_severity.set(45)
            self.med_severity.set(35)
            self.high_severity.set(20)
            self.set_custom_frame_state("disabled")
        elif scenario == "5":
            self.set_custom_frame_state("normal")
    
    def set_custom_frame_state(self, state):
        """Enable or disable custom parameters frame"""
        for child in self.custom_frame.winfo_children():
            if isinstance(child, (ttk.Entry, ttk.Label)):
                if state == "normal":
                    child.configure(state="normal")
                else:
                    child.configure(state="disabled")
    
    def update_total(self, *args):
        """Update total percentage display"""
        try:
            total = self.low_severity.get() + self.med_severity.get() + self.high_severity.get()
            color = "blue" if total == 100 else "red"
            self.total_label.configure(text=f"Total: {total:.0f}%", foreground=color)
        except:
            pass
    
    def run_simulation(self):
        """Run the simulation with selected parameters"""
        try:
            # Validate inputs
            n_incidents = self.n_incidents.get()
            n_runs = self.n_runs.get()
            low = self.low_severity.get()
            med = self.med_severity.get()
            high = self.high_severity.get()
            
            if n_incidents <= 0 or n_runs <= 0:
                messagebox.showerror("Error", "Incidents and runs must be positive")
                return
            
            if n_incidents > 10000:
                messagebox.showwarning("Warning", "Large number of incidents may take a while")
            
            total = low + med + high
            if abs(total - 100) > 0.1:
                messagebox.showerror("Error", f"Severity distribution must sum to 100%, got {total:.1f}%")
                return
            
            # Disable run button
            self.run_button.configure(state="disabled")
            self.status_label.configure(text="Simulation running...", foreground="orange")
            self.root.update()
            
            # Run in separate thread to keep GUI responsive
            thread = threading.Thread(target=self.execute_simulation, args=(
                n_incidents, n_runs, low/100, med/100, high/100
            ))
            thread.daemon = True
            thread.start()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            self.run_button.configure(state="normal")
    
    def execute_simulation(self, n_incidents, n_runs, low_prob, med_prob, high_prob):
        """Execute simulation (runs in separate thread)"""
        try:
            severity_probs = [low_prob, med_prob, high_prob]
            
            # Run experiment
            results = []
            trust_curves = {"HUMAN_ONLY": [], "AI_ONLY": [], "COLLAB": []}
            
            for run in range(n_runs):
                df = generate_incidents(n_incidents)
                
                # Manually set severity probabilities for this run
                original_severity_probs = None
                import simulationtest
                original_severity_probs = simulationtest.SEVERITY_PROBS
                simulationtest.SEVERITY_PROBS = severity_probs
                
                for mode in ["HUMAN_ONLY", "AI_ONLY", "COLLAB"]:
                    sim = simulate_mode(df, mode=mode)
                    results.append({
                        "run": run,
                        "mode": mode,
                        "accuracy": sim["accuracy"],
                        "avg_time_per_incident": sim["avg_time_per_incident"],
                        "policy_blocks": sim["policy_blocks"],
                        "overrides": sim["overrides"],
                    })
                    trust_curves[mode].append(sim["trust_series"])
                
                simulationtest.SEVERITY_PROBS = original_severity_probs
            
            df_results = pd.DataFrame(results)
            
            # Display results
            self.display_results(df_results, trust_curves)
            
            self.status_label.configure(text="Simulation complete!", foreground="green")
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", foreground="red")
            messagebox.showerror("Simulation Error", f"Error during simulation:\n{str(e)}")
        finally:
            self.run_button.configure(state="normal")
    
    def display_results(self, df_results, trust_curves):
        """Display results in a new window"""
        results_window = tk.Toplevel(self.root)
        results_window.title("Simulation Results")
        results_window.geometry("1100x800")
        
        # Summary statistics
        summary = df_results.groupby("mode").agg({
            "accuracy": ["mean", "std"],
            "avg_time_per_incident": ["mean", "std"],
            "policy_blocks": ["mean"],
            "overrides": ["mean"],
        })
        
        summary_text = "\n===== SUMMARY (Mean ± Std) =====\n\n"
        summary_text += summary.to_string()
        
        # Display in text widget
        text_frame = ttk.LabelFrame(results_window, text="Summary Statistics", padding=10)
        text_frame.pack(fill=tk.X, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, height=10, width=120, font=("Courier", 9))
        text_widget.pack(fill=tk.X)
        text_widget.insert("1.0", summary_text)
        text_widget.configure(state="disabled")
        
        # Create notebook for plots
        notebook = ttk.Notebook(results_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Accuracy plot
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Accuracy")
        
        fig1 = plt.Figure(figsize=(8, 5), dpi=100)
        ax1 = fig1.add_subplot(111)
        means = df_results.groupby("mode")["accuracy"].mean()
        stds = df_results.groupby("mode")["accuracy"].std()
        ax1.bar(means.index, means.values, yerr=stds.values, capsize=5, color=["#3498db", "#e74c3c", "#2ecc71"], alpha=0.7)
        ax1.set_title("Mean Accuracy by Mode", fontsize=12, fontweight='bold')
        ax1.set_ylabel("Accuracy")
        ax1.set_ylim(0, 1)
        ax1.grid(axis='y', alpha=0.3)
        
        canvas1 = FigureCanvasTkAgg(fig1, master=tab1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Time plot
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text="Time per Incident")
        
        fig2 = plt.Figure(figsize=(8, 5), dpi=100)
        ax2 = fig2.add_subplot(111)
        means_t = df_results.groupby("mode")["avg_time_per_incident"].mean()
        stds_t = df_results.groupby("mode")["avg_time_per_incident"].std()
        ax2.bar(means_t.index, means_t.values, yerr=stds_t.values, capsize=5, color=["#3498db", "#e74c3c", "#2ecc71"], alpha=0.7)
        ax2.set_title("Mean Time per Incident by Mode", fontsize=12, fontweight='bold')
        ax2.set_ylabel("Time (simulated units)")
        ax2.grid(axis='y', alpha=0.3)
        
        canvas2 = FigureCanvasTkAgg(fig2, master=tab2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Trust curve plot
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Trust Evolution")
        
        fig3 = plt.Figure(figsize=(8, 5), dpi=100)
        ax3 = fig3.add_subplot(111)
        
        for mode in ["AI_ONLY", "COLLAB"]:
            curves = np.array(trust_curves[mode])
            mean_curve = curves.mean(axis=0)
            ax3.plot(mean_curve, label=mode, linewidth=2, marker='o', markersize=3)
        
        ax3.set_title("Trust Evolution Over Incidents", fontsize=12, fontweight='bold')
        ax3.set_xlabel("Incident Index")
        ax3.set_ylabel("Trust (0-1)")
        ax3.set_ylim(0, 1)
        ax3.legend()
        ax3.grid(alpha=0.3)
        
        canvas3 = FigureCanvasTkAgg(fig3, master=tab3)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def main():
    root = tk.Tk()
    app = SimulationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
