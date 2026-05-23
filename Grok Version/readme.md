# Geometric Neuron v4.1 (Grok Edition)

**Phase-Space Geometry meets Biological Reality**

A physicalist single-neuron model where computation emerges from wave geometry and the Axon Initial Segment (AIS) grating — not from scalar weights or backpropagation.

---

## Core Idea

Modern AI is built on the 1943 McCulloch-Pitts neuron: multiply, sum, activate.  
Real neurons don't do arithmetic — they do **geometry**.

This model simulates a neuron as:
- A **dendritic cable** (physical RC delay line)
- An **AIS grating** (fixed spatial resonance template based on Leterrier's 190nm periodic scaffold)
- **Moiré interference** between incoming wave and the grating → resonance → spiking

Learning happens primarily through **geometric alignment**. Morphological plasticity (AIS stretching/hunting) is only a slow fallback when the cell is starving.

---

## Features

- **Real-time 3D Phase Space Torus**: Watch the dendritic signal unfold via Takens-style spatial embedding.
- **AIS Target (Ghost)** vs **Live Signal (Solid)**: See geometric alignment directly.
- **Morphological Plasticity**: The neuron physically changes its resonant frequency when starved (inspired by Leterrier 2018).
- **Ephaptic Noise**: Ambient biological noise injection.
- **Sharp Frequency Selectivity**: Excellent lock when frequencies match, destructive interference otherwise.

---

## Repository Structure (Grok Version)

geometric-neuron/
├── grok_version/
│   ├── phase_space_torus.py          ← Main interactive UI
│   ├── geom_neuron.py                ← Clean core class (optional)
│   ├── requirements.txt
│   └── README.md                     ← This file
├── LICENSE
└── ...

## How to Run

```bash
cd grok_version
pip install -r requirements.txt
python phase_space_torus.py