import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import argparse
from matplotlib.animation import FuncAnimation
from refrigeration_system import RefrigerationSystem, SYSTEM_CONFIGS


class RefrigerationSimulatorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Refrigeration Simulator")
        
        self.system_type = tk.StringVar(value="bottle_cooler")
        self.control_type = tk.StringVar(value="ON_OFF")
        
        self.create_widgets()
        self.create_plot()
        
        self.simulator = RefrigerationSystem(self.system_type.get(), self.control_type.get())
        self.time = 0
        self.data = {"time": [], "cabinet_1": [], "cabinet_2": [], "ambient": []}
        
        self.animation = FuncAnimation(self.fig, self.update_plot, interval=100, blit=False)

    def create_widgets(self):
        frame = ttk.Frame(self.master, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(frame, text="Ambient Temperature:").grid(column=0, row=0, sticky=tk.W)
        self.ambient_temp = ttk.Entry(frame, width=10)
        self.ambient_temp.grid(column=1, row=0, sticky=(tk.W, tk.E))
        self.ambient_temp.insert(0, "25")
        
        ttk.Button(frame, text="Set", command=self.set_ambient_temp).grid(column=2, row=0, sticky=tk.W)
        
        ttk.Label(frame, text="System Type:").grid(column=0, row=1, sticky=tk.W)
        ttk.Combobox(frame, textvariable=self.system_type, 
                     values=list(SYSTEM_CONFIGS.keys())).grid(column=1, row=1, sticky=(tk.W, tk.E))
        
        ttk.Label(frame, text="Control Type:").grid(column=0, row=2, sticky=tk.W)
        ttk.Combobox(frame, textvariable=self.control_type, 
                     values=["ON_OFF", "VCC"]).grid(column=1, row=2, sticky=(tk.W, tk.E))
        
        ttk.Button(frame, text="Restart Simulation", command=self.restart_simulation).grid(column=0, row=3, columnspan=2)

    def create_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def set_ambient_temp(self):
        try:
            new_temp = float(self.ambient_temp.get())
            self.simulator.temperature["ambient"] = new_temp
        except ValueError:
            print("Invalid temperature value")

    def restart_simulation(self):
        self.simulator = RefrigerationSystem(self.system_type.get(), self.control_type.get())
        self.time = 0
        self.data = {"time": [], "cabinet_1": [], "cabinet_2": [], "ambient": []}

    def update_plot(self, frame):
        self.simulator.simulate(60)  # Simulate for 1 minute
        self.time += 1
        
        self.data["time"].append(self.time)
        self.data["cabinet_1"].append(self.simulator.temperature["cabinet_1"])
        self.data["cabinet_2"].append(self.simulator.temperature["cabinet_2"])
        self.data["ambient"].append(self.simulator.temperature["ambient"])
        
        self.ax.clear()
        self.ax.plot(self.data["time"], self.data["cabinet_1"], label="Cabinet 1")
        self.ax.plot(self.data["time"], self.data["cabinet_2"], label="Cabinet 2")
        self.ax.plot(self.data["time"], self.data["ambient"], label="Ambient")
        
        self.ax.set_xlabel("Time (minutes)")
        self.ax.set_ylabel("Temperature (°C)")
        self.ax.set_title("Refrigeration System Simulation")
        self.ax.legend()
        
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = RefrigerationSimulatorGUI(root)
    root.mainloop()