"""
Geometric Neuron v4.1 - Grok Edition
====================================
Core physicalist neuron model.

Computation emerges from wave geometry + AIS grating resonance.
Plasticity is secondary (only activates on prolonged starvation).
"""

import numpy as np

class GeometricNeuron:
    def __init__(self, 
                 initial_length: int = 120,
                 rc_alpha: float = 0.93,
                 initial_hz: float = 10.0,
                 dt: float = 0.01):
        """
        rc_alpha: Signal retention per compartment (higher = less attenuation)
        """
        self.dt = dt
        self.rc_alpha = rc_alpha
        
        # Morphology
        self.cable_length = initial_length
        self.target_hz = initial_hz
        self.cable = np.zeros(self.cable_length)
        
        # Build the physical AIS grating (the "computation")
        self.ais_grating = self._grow_ais_grating(self.target_hz, self.cable_length)
        
        # Membrane dynamics
        self.membrane_potential = 0.0
        self.membrane_leak = 0.88
        self.charge_rate = 0.12
        self.threshold = 0.48
        
        # Homeostasis & Plasticity (slow)
        self.chronic_activity = 0.1
        self.target_activity = 0.12
        self.plasticity_rate = 0.008
        self.hunt_direction = -1

    def _grow_ais_grating(self, target_freq: float, length: int) -> np.ndarray:
        """Simulate a pure wave to burn in the physical AIS grating."""
        temp_cable = np.zeros(length)
        for t in np.arange(0, 2.0, self.dt):
            val = np.sin(2 * np.pi * target_freq * t)
            new_cable = np.zeros_like(temp_cable)
            new_cable[0] = val
            new_cable[1:] = temp_cable[:-1] * self.rc_alpha
            temp_cable = new_cable
        
        norm = np.linalg.norm(temp_cable) + 1e-9
        return temp_cable / norm

    def adapt_morphology(self):
        """Morphological plasticity — only triggers on prolonged starvation."""
        if self.chronic_activity < self.target_activity * 0.35:  # quite hungry
            self.target_hz += self.hunt_direction * self.plasticity_rate
            
            # Bounce at biological bounds
            if self.target_hz < 4.0:
                self.target_hz = 4.0
                self.hunt_direction = 1
            elif self.target_hz > 15.0:
                self.target_hz = 15.0
                self.hunt_direction = -1
            
            new_length = int(120 * (10.0 / self.target_hz))
            
            self.ais_grating = self._grow_ais_grating(self.target_hz, new_length)
            
            # Resize cable
            new_cable = np.zeros(new_length)
            copy_len = min(self.cable_length, new_length)
            new_cable[:copy_len] = self.cable[:copy_len]
            self.cable = new_cable
            self.cable_length = new_length

    def process(self, x_t: float, apply_plasticity: bool = True, noise_level: float = 0.05):
        """Process one time step."""
        # 1. Ephaptic noise
        x_noisy = x_t + np.random.normal(0, noise_level)
        
        # 2. Physical wave propagation down the dendrite
        new_cable = np.zeros_like(self.cable)
        new_cable[0] = x_noisy
        new_cable[1:] = self.cable[:-1] * self.rc_alpha
        self.cable = new_cable
        
        # 3. Moiré Resonance with AIS grating
        cable_norm = self.cable / (np.linalg.norm(self.cable) + 1e-9)
        alignment = np.vdot(cable_norm, self.ais_grating)
        resonance = np.abs(alignment) ** 2
        
        # 4. Membrane integration
        self.membrane_potential = (self.membrane_leak * self.membrane_potential) + \
                                  (self.charge_rate * resonance)
        
        # 5. Spike decision
        spike = 0.0
        if self.membrane_potential > self.threshold:
            spike = 1.0
            self.membrane_potential = 0.0
            self.cable *= 0.35                    # refractory depletion
            self.chronic_activity += 0.08         # strong positive signal
        
        # Update chronic activity
        self.chronic_activity = 0.992 * self.chronic_activity + 0.008 * spike
        
        # 6. Plasticity (slow)
        if apply_plasticity:
            self.adapt_morphology()
        
        return {
            'spike': spike,
            'resonance': resonance,
            'membrane': self.membrane_potential,
            'tuning_hz': self.target_hz,
            'alignment': alignment
        }


# ====================== Simple Test ======================
if __name__ == "__main__":
    neuron = GeometricNeuron(initial_hz=10.0)
    
    print("Testing Geometric Neuron (AIS Grating based)")
    print(f"Initial tuning: {neuron.target_hz:.2f} Hz\n")
    
    # Test with matching frequency
    for i in range(300):
        signal = np.sin(2 * np.pi * 10.0 * i * 0.01)
        result = neuron.process(signal, apply_plasticity=False)
        if result['spike'] > 0 and i % 30 == 0:
            print(f"Spike at t={(i*0.01):.2f}s | Resonance: {result['resonance']:.3f}")