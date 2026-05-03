"""
Einstein's Brownian Motion
================================================
Based on Einstein's 1905 paper equations:

§4 Eq.32:  λₓ = √(2Dt)          — displacement formula
§3 Eq.21:  D = RT / N·6πkP      — Stokes-Einstein equation  
§5 Eq.35:  N = RT / 3πkP·λₓ²   — Avogadro's number

Requirements: pip install matplotlib numpy
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# 2D Brownian motion simulation
# ─────────────────────────────────────────────
def brownian_motion(n_steps=1000, dt=0.01, diffusion=1.0):
    """
    Simulate 2D Brownian motion.
    
    n_steps:   number of time steps
    dt:        time step size
    diffusion: diffusion coefficient
    """
    # Random increments: normal dist scaled by sqrt(2 * D * dt)
    # This directly implements Einstein's §4: ⟨Δ²⟩ = 2Dτ
    scale = np.sqrt(2 * diffusion * dt)
    dx = np.random.normal(0, scale, n_steps)
    dy = np.random.normal(0, scale, n_steps)

    # Cumulative sum gives the trajectory
    # This implements Einstein's random walk: x(t) = Σδᵢ
    x = np.cumsum(dx)
    y = np.cumsum(dy)

    return x, y


# ─────────────────────────────────────────────
# NEW: einstein's physical parameters
# From Einstein's §5 numerical example (page 18)
# ─────────────────────────────────────────────
R  = 8.314        # Gas constant (J/mol·K)
T  = 290          # Temperature in Kelvin (~17°C, same as Einstein used)
N  = 6.022e23     # Avogadro's number (what Einstein wanted to find)
k  = 1.35e-3      # Water viscosity (Pa·s) — same value Einstein used
P  = 0.5e-6       # Particle radius (0.5 micrometers)

# Stokes-Einstein equation (§3, Eq.21):
# D = RT / N · 6πkP
D_physical = R * T / (N * 6 * np.pi * k * P)
print(f"Stokes-Einstein D = {D_physical:.4e} m²/s")
print(f"(Einstein got ~8×10⁻¹³ m²/s for similar parameters)")


# ─────────────────────────────────────────────
# NEW: verify einstein's displacement equation
# λₓ = √(2Dt)  — §4, Eq.32
# ─────────────────────────────────────────────
def compute_msd(positions):
    """
    Compute Mean Squared Displacement over time.
    Verifies Einstein's §4 Eq.32: ⟨x²⟩ = 2Dt
    """
    origin = positions[0]
    n_steps = len(positions) - 1
    msd = np.zeros(n_steps + 1)
    for t in range(n_steps + 1):
        displacement = positions[t] - origin
        msd[t] = np.mean(displacement**2)
    return msd


# ─────────────────────────────────────────────
# NEW: calculated avogadro's number from simulation
# N = RT / 3πkP·λₓ²  — §5, Eq.35
# ─────────────────────────────────────────────
def calculate_avogadro(lambda_x_squared, t, T, k, P, R):
    """
    Einstein's final formula from page 18.
    Given measured displacement, calculate Avogadro's number.
    N = (1/λₓ²) · RT / 3πkP
    """
    N_calculated = (R * T) / (3 * np.pi * k * P * lambda_x_squared / t)
    return N_calculated


# ─────────────────────────────────────────────
# RUN SIMULATIONS
# ─────────────────────────────────────────────
N_PARTICLES = 100
N_STEPS     = 500
DT          = 1.0      # 1 second per step
D_SIM       = 1.0      # Normalised D for visualisation

print(f"\nRunning simulation with {N_PARTICLES} particles, {N_STEPS} steps...")

# Store all trajectories
all_x = []
all_y = []
for _ in range(N_PARTICLES):
    x, y = brownian_motion(n_steps=N_STEPS, dt=DT, diffusion=D_SIM)
    all_x.append(np.insert(x, 0, 0))  # prepend starting point 0
    all_y.append(np.insert(y, 0, 0))

all_x = np.array(all_x)  # shape: (N_PARTICLES, N_STEPS+1)
all_y = np.array(all_y)

# Compute MSD from x positions only (1D, matches Einstein's λₓ)
time_axis = np.arange(N_STEPS + 1) * DT
msd_x = np.mean(all_x**2, axis=0)           # simulated MSD
msd_theoretical = 2 * D_SIM * time_axis      # Einstein's §4: ⟨x²⟩ = 2Dt

# Fit line to MSD to extract D_measured
fit = np.polyfit(time_axis[1:], msd_x[1:], 1)
D_measured = fit[0] / 2
print(f"\nVerifying Einstein's §4 equation ⟨x²⟩ = 2Dt:")
print(f"  D (simulation input) = {D_SIM:.4f}")
print(f"  D (measured from MSD) = {D_measured:.4f}")
print(f"  Agreement: {100*(1-abs(D_measured-D_SIM)/D_SIM):.1f}%")

# Calculate Avogadro's number from final MSD (using physical D)
# Map simulation D to physical D for Avogadro calculation



# ─────────────────────────────────────────────
# PLOTTING — 4 panels
# ─────────────────────────────────────────────
fig = plt.figure(figsize=(16, 12))
fig.patch.set_facecolor('#0f0f1a')
gs = GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

ax1 = fig.add_subplot(gs[0, 0])  # Your original plot
ax2 = fig.add_subplot(gs[0, 1])  # Gaussian distribution (§4)
ax3 = fig.add_subplot(gs[1, 0])  # MSD verification (§4 Eq.32)
ax4 = fig.add_subplot(gs[1, 1])  # Avogadro verification (§5 Eq.35)

DARK    = '#0f0f1a'
GRID    = '#2a2a3a'
TEXT    = '#e0e0f0'
BLUE    = '#00d4ff'
RED     = '#ff6b6b'
GREEN   = '#00ff99'
YELLOW  = '#ffd700'

for ax in [ax1, ax2, ax3, ax4]:
    ax.set_facecolor(DARK)
    ax.tick_params(colors=TEXT)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)
    ax.grid(True, color=GRID, linestyle='--', alpha=0.5)

# ─────────────────────────────────────────────
# PLOTTING — 4 panels
# ─────────────────────────────────────────────


# ── PLOT 1: 2D trajectory of the LAST simulated particle ──
# FIX: draw into ax1, not a separate plt.figure()
ax1.plot(all_x[-1], all_y[-1], lw=0.5, alpha=0.7, color=BLUE)
ax1.scatter([0], [0], color=GREEN, zorder=5, s=40, label='Start')
ax1.scatter([all_x[-1, -1]], [all_y[-1, -1]], color=RED, zorder=5, s=40, label='End')
ax1.set_title("2D Brownian Motion (Einstein §4)")
ax1.set_xlabel("x")
ax1.set_ylabel("y")
ax1.set_aspect('equal')
ax1.legend(labelcolor=TEXT)

# ── PLOT 2: Gaussian distribution — Einstein's §4 Eq.31 ──
t_index = N_STEPS
positions_t = all_x[:, t_index]

ax2.hist(positions_t, bins=30, density=True, alpha=0.6, color=BLUE, label='Simulation')

sigma = np.sqrt(2 * D_SIM * time_axis[t_index])
x_vals = np.linspace(min(positions_t), max(positions_t), 200)
gaussian = (1 / np.sqrt(2 * np.pi * sigma**2)) * np.exp(-x_vals**2 / (2 * sigma**2))

ax2.plot(x_vals, gaussian, color=RED, lw=2, label='Theory (Gaussian)')
ax2.set_title("Displacement Distribution (Einstein §4 Eq.31)")
ax2.set_xlabel("x")
ax2.set_ylabel("Probability Density")
ax2.legend(labelcolor=TEXT)

# ── PLOT 3: MSD verification — Einstein's §4 Eq.32 ──
ax3.plot(time_axis, msd_x, color=BLUE, lw=2, label='Simulation ⟨x²⟩')
ax3.plot(time_axis, msd_theoretical, color=RED, linestyle='--', lw=2, label='Theory 2Dt')
ax3.set_title("Mean Squared Displacement vs Time")
ax3.set_xlabel("Time")
ax3.set_ylabel("⟨x²⟩")
ax3.legend(labelcolor=TEXT)

# Annotate measured D agreement
agreement = 100 * (1 - abs(D_measured - D_SIM) / D_SIM)
ax3.annotate(f"D agreement: {agreement:.1f}%", xy=(0.05, 0.88),
             xycoords='axes fraction', color=TEXT, fontsize=9)

# ── PLOT 4: Avogadro's number — Einstein's §5 Eq.35 ──
scale_factor = D_physical / D_SIM
lambda_x_squared_physical = msd_x * scale_factor

N_values = calculate_avogadro(
    lambda_x_squared_physical[1:],
    time_axis[1:],
    T, k, P, R
)

ax4.plot(time_axis[1:], N_values, color=GREEN, lw=2, label='Calculated N')
ax4.axhline(N, color=YELLOW, linestyle='--', lw=2, label=f'True N = {N:.3e}')
ax4.set_title("Avogadro's Number from Brownian Motion")
ax4.set_xlabel("Time")
ax4.set_ylabel("N")
ax4.set_ylim(0, 1.5 * N)
ax4.legend(labelcolor=TEXT)

# ── FINAL: show the complete 4-panel figure ──
fig.suptitle("Einstein's Brownian Motion — Full Verification (1905)",
             color=TEXT, fontsize=14, y=1.01)
plt.tight_layout()
plt.savefig("brownian_einstein.png", dpi=150, bbox_inches='tight',
            facecolor=DARK)
plt.show()
