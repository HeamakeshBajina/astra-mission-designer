# ASTRA — Autonomous Spacecraft Trajectory & Mission Analysis

> A computational aerospace engineering platform for spacecraft orbital analysis, numerical trajectory simulation, mission analysis, and transfer-strategy optimization.

ASTRA is an open-source aerospace engineering project that combines **orbital mechanics, numerical methods, spacecraft propulsion analysis, simulation, and optimization** into a single computational workflow.

The project is designed around a physics-first question:

> **Given a spacecraft and a desired orbital transfer, how can we determine, simulate, validate, and optimize a feasible mission trajectory?**

---

## 🚀 What ASTRA Does

ASTRA takes mission parameters and turns them into an engineering analysis:

```text
Mission Parameters
        ↓
Orbital Mechanics
        ↓
Transfer Calculation
        ↓
Propulsion Analysis
        ↓
Numerical Simulation
        ↓
Trajectory Validation
        ↓
Transfer Optimization
        ↓
Best Feasible Mission Strategy
```

The system currently supports:

- Circular orbital mechanics
- Orbital velocity calculations
- Escape velocity calculations
- Orbital-period calculations
- Specific orbital energy
- Hohmann transfer analysis
- Rocket-equation propellant estimation
- Numerical trajectory propagation
- Fourth-order Runge–Kutta integration
- Instantaneous orbital burns
- Continuous Hohmann mission simulation
- Trajectory analysis
- Numerical stability validation
- Hohmann vs. bi-elliptic transfer optimization
- Propellant-feasibility analysis
- Interactive mission visualization

---

# 🛰️ Engineering Architecture

ASTRA is organized into several computational layers.

```text
Mission Inputs
      ↓
Orbital Mechanics
      ↓
Transfer Analysis
      ↓
Propulsion Analysis
      ↓
Numerical Simulator
      ↓
Validation & Error Analysis
      ↓
Transfer Optimizer
      ↓
Best Feasible Mission
```

The architecture intentionally separates **physics**, **simulation**, **mission analysis**, and **optimization** so that individual components can be tested independently.

---

# 📐 Orbital Mechanics

ASTRA implements fundamental two-body orbital mechanics relationships.

## Circular Orbital Velocity

For a circular orbit:

```text
v_c = sqrt(μ / r)
```

where:

- `v_c` = circular orbital velocity
- `μ` = gravitational parameter
- `r` = orbital radius from Earth's center

ASTRA uses Earth's standard gravitational parameter:

```text
μ = 3.986004418 × 10^14 m^3/s^2
```

## Escape Velocity

The escape velocity is:

```text
v_e = sqrt(2μ / r)
```

This represents the minimum theoretical velocity required to escape the gravitational field under the idealized two-body model.

## Orbital Period

For a circular orbit:

```text
T = 2π sqrt(r^3 / μ)
```

ASTRA uses this relationship to determine orbital periods and transfer durations.

## Specific Orbital Energy

For a circular orbit:

```text
ε = -μ / (2r)
```

Specific orbital energy is also used as a numerical diagnostic.

During ideal two-body propagation, orbital energy should remain approximately constant.

Any drift therefore provides a useful measure of numerical integration error.

---

# 🔄 Hohmann Transfer Analysis

ASTRA implements two-burn Hohmann transfers between circular Earth orbits.

A Hohmann transfer consists of:

1. A first velocity change that places the spacecraft onto an elliptical transfer orbit.
2. Propagation along the transfer orbit.
3. A second velocity change that circularizes the spacecraft at the destination orbit.

ASTRA calculates:

- Transfer semi-major axis
- First-burn Δv
- Second-burn Δv
- Total Δv
- Transfer time

The transfer model supports both:

- Orbit raising
- Orbit lowering

---

# ⛽ Propulsion Analysis

ASTRA connects orbital mechanics to spacecraft propulsion through the **Tsiolkovsky rocket equation**:

```text
Δv = Isp × g0 × ln(m0 / mf)
```

where:

- `Δv` = velocity change
- `Isp` = specific impulse
- `g0` = standard gravitational acceleration
- `m0` = initial spacecraft mass
- `mf` = final spacecraft mass

The system can estimate the propellant required to achieve a calculated mission Δv.

This allows mission strategies to be evaluated using both:

- Required Δv
- Required propellant

rather than Δv alone.

---

# 🧮 Numerical Trajectory Simulation

Analytical orbital equations are useful for determining ideal values, but ASTRA also numerically propagates spacecraft motion through time.

The simulator uses **fourth-order Runge–Kutta (RK4)** integration.

The spacecraft state is represented as:

```text
(x, y, vx, vy)
```

where:

- `x`, `y` represent position
- `vx`, `vy` represent velocity

The two-body gravitational acceleration is calculated from the spacecraft's instantaneous position.

The numerical propagator repeatedly advances the spacecraft state using the selected timestep.

---

# 🔥 Orbital Burn Modeling

ASTRA explicitly models instantaneous velocity changes.

The simulation currently supports:

- Prograde burns
- Retrograde burns

Burn events contain:

- Event time
- Δv
- State before the burn
- State after the burn
- Burn name
- Burn direction

This allows a mission to be represented as a continuous timeline rather than as independent orbital calculations.

---

# 🛰️ Continuous Hohmann Mission Simulation

ASTRA combines analytical transfer calculations with numerical propagation to simulate an entire Hohmann mission.

The mission sequence is:

```text
Initial Circular Orbit
        ↓
     First Burn
        ↓
   Transfer Orbit
        ↓
Numerical Propagation
        ↓
    Second Burn
        ↓
   Final Circular Orbit
        ↓
Final Orbit Propagation
```

This provides both analytical and numerical results.

### Analytical Results

From the Hohmann transfer equations:

- Expected Δv
- Expected transfer time
- Expected transfer geometry

### Numerical Results

From RK4 propagation:

- Spacecraft position
- Spacecraft velocity
- Trajectory history
- Burn states
- Numerical error

The two approaches can then be compared.

---

# 📊 Numerical Validation

One of ASTRA's goals is to avoid treating a simulation as correct simply because it produces a visually plausible trajectory.

The numerical simulator is therefore validated against analytical solutions.

Validation currently examines:

- Transfer-radius error
- Transfer-velocity error
- Percentage error
- Timestep sensitivity
- Orbital-energy drift

The project also tests whether reducing the timestep improves numerical accuracy.

The validation workflow is:

```text
Analytical Solution
        ↓
Numerical Simulation
        ↓
  Compare Results
        ↓
   Calculate Error
        ↓
   Change Timestep
        ↓
 Evaluate Convergence
```

This provides an engineering-based check on the numerical model.

---

# 🧠 Transfer Strategy Optimization

ASTRA does not assume that a Hohmann transfer is always the best possible strategy.

The optimizer currently evaluates:

- Hohmann transfers
- Bi-elliptic transfers

For bi-elliptic transfers, ASTRA searches across a configurable range of intermediate apoapsis altitudes.

Each candidate strategy is evaluated according to:

- Total Δv
- Required propellant
- Available propellant
- Mission feasibility

The optimizer then selects the **lowest-Δv feasible strategy**.

## Hohmann vs. Bi-Elliptic Search

The optimization process is:

```text
Mission
   ↓
┌───────────────┐
↓               ↓
Hohmann     Bi-Elliptic
   ↓               ↓
Calculate       Search
   Δv          Candidates
   ↓               ↓
Propellant     Propellant
   ↓               ↓
Feasible?      Feasible?
   └───────┬───────┘
           ↓
    Compare Candidates
           ↓
    Lowest-Δv Strategy
```

For relatively small orbital-radius ratios, Hohmann transfers remain highly competitive.

For sufficiently large orbital-radius ratios, the optimizer can identify cases where a bi-elliptic transfer requires less Δv.

---

# 📈 Example Mission

A representative ASTRA mission configuration is:

| Parameter | Value |
|---|---:|
| Initial altitude | 400 km |
| Target altitude | 800 km |
| Spacecraft mass | 1000 kg |
| Specific impulse | 300 s |
| Available propellant | 500 kg |

The resulting mission analysis is approximately:

| Result | Value |
|---|---:|
| Total Δv | 217 m/s |
| Required propellant | 71.11 kg |
| Remaining propellant | 428.89 kg |
| Transfer time | 0.80 hr |
| Mission status | Feasible |

For this particular low-radius-ratio transfer, ASTRA selects the **Hohmann transfer** as the best strategy.

---

# 🖥️ Interactive Dashboard

ASTRA includes an interactive Streamlit dashboard.

The dashboard allows users to modify mission parameters and immediately inspect the resulting engineering calculations.

The interface includes:

### Mission Configuration

- Mission name
- Initial altitude
- Target altitude
- Spacecraft mass
- Specific impulse
- Available propellant

### Mission Summary

- Required Δv
- Fuel required
- Fuel remaining
- Transfer time
- Mission feasibility

### Trajectory Visualization

- Earth representation
- Initial orbit
- Transfer trajectory
- Final orbit
- Burn locations
- Spacecraft trajectory

### Transfer Analysis

- First burn
- Second burn
- Transfer semi-major axis
- Transfer time
- Total Δv

### Optimization

- Hohmann baseline
- Bi-elliptic candidate search
- Best feasible strategy
- Δv savings
- Propellant savings
- Candidate comparison

### Numerical Stability

- Altitude error
- Velocity error
- Energy drift
- Expected orbital values

---

# 🧪 Testing

ASTRA contains an automated test suite covering the project's core computational layers.

Tests cover:

- Orbital mechanics
- Transfer calculations
- Rocket-equation calculations
- Mission analysis
- Mission profiles
- Numerical propagation
- Trajectory analysis
- Burn modeling
- Continuous mission trajectories
- Numerical validation
- Optimization
- Visualization

Run the test suite with:

```text
pytest -q
```

The current development milestone contains:

```text
99 passed
```

The tests are intended to provide regression protection as the project evolves.

---

# 🗂️ Project Structure

```text
astra-mission-designer/
│
├── app.py
├── demo.py
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
│
├── src/
│   └── astra/
│       │
│       ├── mission/
│       │   ├── __init__.py
│       │   ├── analysis.py
│       │   ├── optimizer.py
│       │   ├── planner.py
│       │   └── profile.py
│       │
│       ├── physics/
│       │   ├── __init__.py
│       │   ├── constants.py
│       │   ├── orbital.py
│       │   ├── rocket.py
│       │   └── transfers.py
│       │
│       ├── simulation/
│       │   ├── __init__.py
│       │   ├── burns.py
│       │   ├── mission_trajectory.py
│       │   ├── propagator.py
│       │   ├── trajectory.py
│       │   ├── trajectory_analysis.py
│       │   ├── transfer.py
│       │   └── validation.py
│       │
│       └── visualization.py
│
└── tests/
    ├── test_burns.py
    ├── test_mission_analysis.py
    ├── test_mission_trajectory.py
    ├── test_mission_profile.py
    ├── test_optimizer.py
    ├── test_orbital.py
    ├── test_planner.py
    ├── test_propagator.py
    ├── test_rocket.py
    ├── test_trajectory.py
    ├── test_trajectory_analysis.py
    ├── test_transfer.py
    ├── test_transfers.py
    ├── test_validation.py
    ├── test_validation_convergence.py
    └── test_visualization.py
```

---

# ⚙️ Technology Stack

ASTRA is built primarily with Python.

Core technologies include:

- **Python** — computational implementation
- **Matplotlib** — engineering visualization
- **Pandas** — data handling
- **Streamlit** — interactive dashboard
- **Pytest** — automated testing

The project targets Python 3.13.

---

# 🌍 Physical Model

The current ASTRA simulation uses an idealized **two-body Earth-centered gravitational model**.

The model assumes:

- Earth is the central gravitational body
- Earth has a constant gravitational parameter
- Spacecraft mass does not affect Earth's motion
- No atmospheric drag
- No third-body gravitational effects
- No solar radiation pressure
- Instantaneous burns
- Idealized propulsion
- Two-dimensional orbital motion

These assumptions intentionally keep the current system focused on fundamental orbital mechanics and numerical methods.

---

# ⚠️ Current Limitations

ASTRA is not currently intended to be a flight-certified mission-design system.

The current model does not yet include:

- Earth's oblateness and J2 perturbation
- Atmospheric drag
- Lunar gravity
- Solar gravity
- Third-body perturbations
- Solar radiation pressure
- Finite-duration engine burns
- Thrust-vector dynamics
- Spacecraft attitude dynamics
- Three-dimensional orbital propagation
- Launch-window constraints
- Real spacecraft hardware constraints
- Full ephemeris data

These limitations define the boundary of the current model and provide opportunities for future development.

---

# 🔬 Future Development

Potential future extensions include:

## Orbital Mechanics

- 3D orbital propagation
- Inclination-change maneuvers
- Plane-change optimization
- J2 perturbation modeling
- More general Lambert transfers

## Numerical Simulation

- Adaptive timestep integration
- Higher-order numerical integrators
- Finite-duration thrust
- Thrust-vector control
- Atmospheric models

## Mission Design

- Multi-burn missions
- Multi-orbit missions
- Launch-window analysis
- Interplanetary transfers
- Multi-body mission analysis

## Optimization

- Multi-variable trajectory optimization
- Constrained optimization
- Global optimization methods
- Propellant-cost optimization
- Time-vs-Δv trade studies

## Visualization

- 3D trajectory visualization
- Orbital-element plots
- Interactive mission timelines
- Automated engineering reports

---

# 🎯 Engineering Objectives

ASTRA is being developed around several core engineering principles:

### 1. Physics First

The system should be based on explicit physical relationships rather than opaque outputs.

### 2. Computational Reproducibility

Calculations should be deterministic and testable.

### 3. Numerical Verification

Numerical simulations should be compared against analytical solutions wherever possible.

### 4. Modular Architecture

Physics, simulation, mission analysis, and optimization should remain independently testable.

### 5. Engineering Trade-offs

Mission strategies should be evaluated using meaningful engineering quantities such as:

- Δv
- Propellant
- Transfer time
- Numerical accuracy
- Mission feasibility

---

# 🤖 AI-Assisted Development

AI tools were used as development assistants during the creation of ASTRA.

AI assistance included:

- Brainstorming
- Explaining technical concepts
- Debugging
- Reviewing implementation approaches
- Suggesting implementation strategies
- Improving documentation
- Exploring user-interface ideas

The developer remained responsible for:

- Project architecture
- Engineering decisions
- Implementation
- Testing
- Verification
- Integration
- Final project decisions

AI-assisted code was reviewed, modified where necessary, and tested before integration.

AI was **not** used to fabricate development hours, project activity, test results, or engineering work.

---

# 📚 Engineering Concepts Demonstrated

ASTRA brings together several areas of computational engineering:

```text
ASTRA
  │
  ├── Physics
  │     └── Orbital Mechanics
  │
  ├── Mathematics
  │     ├── Analytical Modeling
  │     └── Numerical Methods
  │
  ├── Programming
  │     └── Scientific Computing
  │
  ├── Simulation
  │     └── Trajectory Propagation
  │
  └── Optimization
        └── Mission Strategy
```

The project therefore demonstrates more than a single programming technique.

It combines mathematical modeling, physical reasoning, software engineering, numerical computation, validation, and optimization into one system.

---

# 📜 License

ASTRA is released under the MIT License.

See `LICENSE` for the complete license text.

---

# 👨‍💻 Project Status

**Current status: Active development**

The current milestone includes:

- Core orbital mechanics
- Hohmann transfer analysis
- Rocket-equation calculations
- Numerical RK4 propagation
- Burn-event simulation
- Continuous Hohmann missions
- Numerical validation
- Transfer optimization
- Interactive dashboard
- Automated testing

Future releases will expand ASTRA toward increasingly realistic spacecraft and mission-design models.

---

# 🚀 ASTRA

**Computational aerospace engineering through physics, simulation, validation, and optimization.**
