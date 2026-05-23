"""
Geometric Neuron: 3D Phase Space Torus UI
-----------------------------------------
Visualizes the internal continuous geometry of the dendritic cable.
Watch the physical signal fold into a Strange Attractor and attempt 
to lock onto the AIS grating's geometry.
"""

import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import threading
import time

# ============================================================
# 1. The Upgraded Geometric Neuron (With 'Hunting' Plasticity)
# ============================================================
class GeometricNeuronV4_UI:
    def __init__(self, initial_length=120, rc_alpha=0.85, initial_hz=10.0, dt=0.01):
        self.dt = dt
        self.rc_alpha = rc_alpha
        
        self.cable_length = initial_length
        self.target_hz = initial_hz
        self.cable = np.zeros(self.cable_length)
        self.ais_grating = self._grow_ais_grating(self.target_hz, self.cable_length)
        
        # TIGHTENED INTEGRATION: Makes the cell highly selective (no false locks)
        self.membrane_potential = 0.0
        self.membrane_leak = 0.90
        self.charge_rate = 0.10
        self.threshold = 0.45
        
        self.chronic_activity = 0.1
        self.target_activity = 0.1
        self.plasticity_rate = 0.02
        self.hunt_direction = -1

    def _grow_ais_grating(self, target_freq, length):
        temp_cable = np.zeros(length)
        for t in np.arange(0, 2.0, self.dt):
            val = np.sin(2 * np.pi * target_freq * t)
            new_cable = np.zeros_like(temp_cable)
            new_cable[0] = val
            # TIGHTENED CABLE: 0.95 creates a sharp, physical comet-tail
            new_cable[1:] = temp_cable[:-1] * 0.95 
            temp_cable = new_cable
        norm = np.linalg.norm(temp_cable) + 1e-9
        return temp_cable / norm

    def adapt_morphology(self):
        # If starving, hunt for a new geometric attractor
        if self.chronic_activity < self.target_activity * 0.5:
            self.target_hz += self.hunt_direction * self.plasticity_rate
            
            # Bounce off the limits to keep hunting (Biological bounds)
            if self.target_hz < 4.0:
                self.target_hz = 4.0
                self.hunt_direction = 1
            elif self.target_hz > 15.0:
                self.target_hz = 15.0
                self.hunt_direction = -1
                
            new_length = int(120 * (10.0 / self.target_hz)) # Cable scales with frequency
            
            self.ais_grating = self._grow_ais_grating(self.target_hz, new_length)
            
            new_cable = np.zeros(new_length)
            copy_len = min(self.cable_length, new_length)
            new_cable[:copy_len] = self.cable[:copy_len]
            self.cable = new_cable
            self.cable_length = new_length

    def process(self, x_t, apply_plasticity=True, noise_level=0.05):
        ambient_noise = np.random.normal(0, noise_level)
        x_noisy = x_t + ambient_noise
        
        new_cable = np.zeros_like(self.cable)
        new_cable[0] = x_noisy
        # TIGHTENED CABLE: 0.95 matches the grating
        new_cable[1:] = self.cable[:-1] * 0.95 
        self.cable = new_cable
        
        cable_norm = self.cable / (np.linalg.norm(self.cable) + 1e-9)
        alignment = np.vdot(cable_norm, self.ais_grating)
        resonance = np.abs(alignment) ** 2
        
        self.membrane_potential = (self.membrane_leak * self.membrane_potential) + (self.charge_rate * resonance)
        
        spike = 0.0
        if self.membrane_potential > self.threshold:
            spike = 1.0
            self.membrane_potential = 0.0
            self.cable *= 0.4
            self.chronic_activity += 0.05
            
        self.chronic_activity = 0.995 * self.chronic_activity + 0.005 * spike
        
        if apply_plasticity:
            self.adapt_morphology()
            
        return spike, resonance, self.membrane_potential

# ============================================================
# 2. The Tkinter + Matplotlib 3D UI
# ============================================================
class GeometricNeuronUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Geometric Neuron: Phase Space Torus")
        self.root.geometry("1200x800")
        
        # Engine
        self.dt = 0.01
        self.t = 0.0
        self.gn = GeometricNeuronV4_UI(initial_hz=10.0, dt=self.dt)
        self.running = True
        
        # UI State
        self.env_freq = tk.DoubleVar(value=10.0)
        self.noise_level = tk.DoubleVar(value=0.05)
        self.plasticity_on = tk.BooleanVar(value=True)
        
        # History buffers for 2D plots
        self.hist_len = 300
        self.mem_hist = np.zeros(self.hist_len)
        self.spk_hist = np.zeros(self.hist_len)
        self.hz_hist = np.zeros(self.hist_len)
        self.env_hist = np.zeros(self.hist_len)
        
        self._build_ui()
        self._start_simulation()

    def _build_ui(self):
        # Top Control Panel
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(control_frame, text="Environment (External Signal) Hz:").pack(side=tk.LEFT, padx=5)
        env_slider = ttk.Scale(control_frame, from_=5.0, to=15.0, variable=self.env_freq, orient=tk.HORIZONTAL, length=200)
        env_slider.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(control_frame, text="Ephaptic Noise Level:").pack(side=tk.LEFT, padx=5)
        noise_slider = ttk.Scale(control_frame, from_=0.0, to=0.5, variable=self.noise_level, orient=tk.HORIZONTAL, length=150)
        noise_slider.pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(control_frame, text="Enable Plasticity (Hunting)", variable=self.plasticity_on).pack(side=tk.LEFT, padx=20)
        
        # Matplotlib Canvas
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(12, 8))
        
        # 3D Phase Space
        self.ax3d = self.fig.add_subplot(211, projection='3d')
        self.ax3d.set_title("Spatial Phase Space (The Torus)")
        self.ax3d.set_xlabel("Proximal Dendrite")
        self.ax3d.set_ylabel("Mid Dendrite")
        self.ax3d.set_zlabel("Distal Dendrite")
        
        # Live 3D Lines
        self.line_grating, = self.ax3d.plot([], [], [], color='purple', alpha=0.4, label='AIS Target (Ghost)')
        self.line_cable, = self.ax3d.plot([], [], [], color='cyan', linewidth=2, label='Live Signal (Solid)')
        self.ax3d.legend()
        
        # 2D Telemetry
        self.ax2d = self.fig.add_subplot(212)
        self.line_mem, = self.ax2d.plot([], [], color='white', label='Membrane')
        self.line_spk, = self.ax2d.plot([], [], color='red', linestyle='', marker='|', markersize=20, label='Spikes')
        self.line_hz, = self.ax2d.plot([], [], color='blue', label='Neuron Tuning Hz')
        self.line_env, = self.ax2d.plot([], [], color='gray', alpha=0.5, label='Env Signal')
        
        self.ax2d.set_xlim(0, self.hist_len)
        self.ax2d.set_ylim(-1.5, 15.5)
        self.ax2d.legend(loc='upper right')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def _get_takens_embedding(self, array):
        """Folds a 1D spatial array into 3D using a guaranteed 1/4 wavelength delay"""
        tau = max(1, int(0.25 / (self.gn.target_hz * self.dt)))
        
        if len(array) <= 2 * tau:
            return np.zeros(5), np.zeros(5), np.zeros(5)
            
        x = array[:-2*tau]
        
        # Compensate for the physical 0.95 dendritic cable signal decay in the UI
        decay_factor = 0.95
        y = array[tau:-tau] * (1.0 / (decay_factor ** tau))
        z = array[2*tau:] * (1.0 / (decay_factor ** (2 * tau)))
        
        return x, y, z

    def _simulation_step(self):
        while self.running:
            # Run 5 iterations per UI frame to speed up time
            for _ in range(5):
                self.t += self.dt
                env_val = np.sin(2 * np.pi * self.env_freq.get() * self.t)
                
                spike, res, mem = self.gn.process(
                    env_val, 
                    apply_plasticity=self.plasticity_on.get(),
                    noise_level=self.noise_level.get()
                )
                
                # Shift buffers
                self.mem_hist = np.roll(self.mem_hist, -1)
                self.spk_hist = np.roll(self.spk_hist, -1)
                self.hz_hist = np.roll(self.hz_hist, -1)
                self.env_hist = np.roll(self.env_hist, -1)
                
                self.mem_hist[-1] = mem
                self.spk_hist[-1] = spike if spike > 0 else np.nan
                self.hz_hist[-1] = self.gn.target_hz
                self.env_hist[-1] = env_val
            
            # Update 3D Visuals
            x_g, y_g, z_g = self._get_takens_embedding(self.gn.ais_grating * 5) # Scale for visibility
            self.line_grating.set_data(x_g, y_g)
            self.line_grating.set_3d_properties(z_g)
            
            x_c, y_c, z_c = self._get_takens_embedding(self.gn.cable)
            self.line_cable.set_data(x_c, y_c)
            self.line_cable.set_3d_properties(z_c)
            
            # Auto-scale 3D axes slightly
            limit = max(0.5, np.max(np.abs(self.gn.cable)))
            self.ax3d.set_xlim(-limit, limit)
            self.ax3d.set_ylim(-limit, limit)
            self.ax3d.set_zlim(-limit, limit)
            
            # Update 2D Visuals
            x_axis = np.arange(self.hist_len)
            self.line_mem.set_data(x_axis, self.mem_hist)
            self.line_spk.set_data(x_axis, self.spk_hist)
            self.line_hz.set_data(x_axis, self.hz_hist)
            self.line_env.set_data(x_axis, self.env_hist)
            
            self.canvas.draw_idle()
            time.sleep(0.03)

    def _start_simulation(self):
        self.sim_thread = threading.Thread(target=self._simulation_step, daemon=True)
        self.sim_thread.start()

    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GeometricNeuronUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()