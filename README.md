# ASTRA — Autonomous Spacecraft Trajectory & Mission Analysis

> A physics-first computational aerospace engineering platform for spacecraft orbital analysis, numerical trajectory simulation, mission analysis, validation, and transfer-strategy optimization.

---

## Table of Contents

1. [What is ASTRA?](#what-is-astra)
2. [ASTRA in 30 Seconds](#astra-in-30-seconds)
3. [The Engineering Problem](#the-engineering-problem)
4. [What ASTRA Does](#what-astra-does)
5. [How ASTRA Works](#how-astra-works)
6. [Engineering Architecture](#engineering-architecture)
7. [Core Physics](#core-physics)
8. [Orbital Mechanics](#orbital-mechanics)
9. [Hohmann Transfers](#hohmann-transfers)
10. [Rocket Propulsion and Delta-v](#rocket-propulsion-and-delta-v)
11. [Numerical Trajectory Simulation](#numerical-trajectory-simulation)
12. [Runge-Kutta 4 Integration](#runge-kutta-4-integration)
13. [Orbital Burn Modeling](#orbital-burn-modeling)
14. [Continuous Mission Simulation](#continuous-mission-simulation)
15. [Trajectory Analysis](#trajectory-analysis)
16. [Numerical Validation](#numerical-validation)
17. [Transfer Strategy Optimization](#transfer-strategy-optimization)
18. [Hohmann vs Bi-Elliptic Transfers](#hohmann-vs-bi-elliptic-transfers)
19. [Mission Feasibility](#mission-feasibility)
20. [Interactive Dashboard](#interactive-dashboard)
21. [Example Mission](#example-mission)
22. [Testing](#testing)
23. [Project Structure](#project-structure)
24. [Technology Stack](#technology-stack)
25. [Physical Model and Assumptions](#physical-model-and-assumptions)
26. [Current Limitations](#current-limitations)
27. [Future Development](#future-development)
28. [Engineering Design Principles](#engineering-design-principles)
29. [AI-Assisted Development](#ai-assisted-development)
30. [Engineering Concepts Demonstrated](#engineering-concepts-demonstrated)
31. [How to Run ASTRA](#how-to-run-astra)
32. [Project Status](#project-status)
33. [License](#license)

---

# What is ASTRA?

ASTRA stands for:

**Autonomous Spacecraft Trajectory & Mission Analysis**

ASTRA is a computational aerospace engineering project that models spacecraft motion around Earth and helps answer a practical mission-design question:

> **Given a spacecraft, a starting orbit, a target orbit, and a limited amount of propellant, what transfer should the spacecraft perform, how much delta-v will it require, and is the mission feasible?**

Instead of producing a single number, ASTRA builds a complete engineering workflow.

The system can:

1. Accept mission parameters.
2. Calculate orbital properties.
3. Calculate an analytical orbital transfer.
4. Estimate the propellant required.
5. Numerically simulate spacecraft motion.
6. Model orbital burns.
7. Compare numerical results with analytical expectations.
8. Measure numerical error.
9. Search alternative transfer strategies.
10. Determine the best feasible strategy.
11. Visualize the mission and its results.

ASTRA is therefore more than a calculator.

It is a small computational mission-analysis system built around physics, numerical methods, software engineering, validation, and optimization.

---

# ASTRA in 30 Seconds

Imagine a spacecraft is orbiting Earth at **400 km altitude** and needs to reach an **800 km altitude** orbit.

You give ASTRA:

```text
Starting altitude:      400 km
Target altitude:        800 km
Spacecraft mass:        1000 kg
Specific impulse:       300 s
Available propellant:   500 kg
```

ASTRA then works through the mission:

```text
                  USER INPUT
                      │
                      ▼
             Mission Parameters
                      │
                      ▼
              Orbital Mechanics
                      │
                      ▼
             Hohmann Transfer
                      │
                      ▼
                Required Δv
                      │
                      ▼
             Rocket Equation
                      │
                      ▼
             Required Propellant
                      │
                      ▼
          Numerical RK4 Simulation
                      │
                      ▼
              Burn Simulation
                      │
                      ▼
             Numerical Validation
                      │
                      ▼
           Transfer Optimization
                      │
                      ▼
              Mission Decision
                      │
                      ▼
              Visualization
```

For the representative 400 km → 800 km mission, ASTRA calculates approximately:

```text
Total Δv:              217 m/s
Required propellant:   71.11 kg
Remaining propellant:  428.89 kg
Transfer time:         0.80 hr
Mission status:        Feasible
Best strategy:         Hohmann
```

---

# The Engineering Problem

Changing a spacecraft's orbit is not simply a matter of telling the spacecraft to "go higher."

A spacecraft in orbit is continuously moving under gravity.

To change its orbit, its velocity must be changed in a controlled way.

That creates several engineering questions:

- How fast is the spacecraft currently moving?
- How fast should it move after the maneuver?
- How much delta-v is required?
- How much propellant does that delta-v consume?
- How long does the transfer take?
- Does the spacecraft remain on the expected trajectory?
- How accurate is the numerical simulation?
- Is another transfer strategy more efficient?
- Does the spacecraft have enough propellant?
- Which feasible strategy requires the least delta-v?

ASTRA attempts to answer these questions in a single computational workflow.

---

# What ASTRA Does

ASTRA currently includes the following major capabilities.

## 1. Orbital Mechanics

ASTRA calculates:

- Circular orbital velocity
- Escape velocity
- Circular orbital period
- Specific orbital energy

## 2. Transfer Analysis

ASTRA calculates:

- Hohmann transfer geometry
- Transfer semi-major axis
- First-burn delta-v
- Second-burn delta-v
- Total delta-v
- Transfer time

The transfer model supports both orbit raising and orbit lowering.

## 3. Propulsion Analysis

ASTRA uses the Tsiolkovsky rocket equation to connect required delta-v to spacecraft propellant requirements.

## 4. Numerical Simulation

ASTRA numerically propagates spacecraft position and velocity using a fourth-order Runge-Kutta integrator.

## 5. Burn Modeling

ASTRA can apply instantaneous:

- Prograde burns
- Retrograde burns

and records the spacecraft state before and after each burn.

## 6. Continuous Mission Simulation

The analytical transfer calculation and numerical simulator can be combined into one continuous mission timeline.

## 7. Numerical Validation

ASTRA compares numerical simulation results against analytical expectations and measures:

- Position/radius error
- Velocity error
- Percentage error
- Timestep sensitivity
- Orbital-energy drift

## 8. Transfer Optimization

ASTRA compares:

- Hohmann transfers
- Bi-elliptic transfers

and searches candidate intermediate apoapsis altitudes for bi-elliptic transfers.

## 9. Mission Feasibility

A strategy can be marked feasible or infeasible based on the available propellant.

## 10. Visualization

ASTRA provides an interactive dashboard showing:

- Mission parameters
- Mission summary
- Orbital trajectories
- Burn locations
- Transfer information
- Optimization results
- Numerical stability information

---

# How ASTRA Works

The complete computational workflow can be viewed as seven major stages.

## Stage 1 — Define the Mission

The user specifies:

```text
Initial orbit
Target orbit
Spacecraft mass
Engine specific impulse
Available propellant
```

These values define the mission constraints.

---

## Stage 2 — Calculate the Physics

ASTRA calculates the relevant orbital properties.

For example:

```text
Orbital radius
Circular velocity
Orbital period
Specific orbital energy
```

These calculations establish the physical state of the mission.

---

## Stage 3 — Calculate the Transfer

ASTRA determines the required orbital transfer.

For a circular-to-circular Hohmann transfer, it calculates:

```text
Transfer orbit
First burn
Second burn
Total Δv
Transfer time
```

---

## Stage 4 — Calculate Propellant

The required delta-v is passed into the rocket equation.

ASTRA estimates how much propellant is needed.

---

## Stage 5 — Simulate the Mission

The spacecraft is numerically propagated through time.

The simulator calculates the spacecraft's state repeatedly:

```text
Position → acceleration → velocity → new position
```

using RK4 integration.

---

## Stage 6 — Validate the Simulation

The numerical solution is compared against analytical expectations.

ASTRA asks:

```text
Did the spacecraft reach the expected radius?
Did it have the expected velocity?
How large is the numerical error?
Does a smaller timestep improve the result?
Is orbital energy approximately conserved?
```

---

## Stage 7 — Optimize the Mission

ASTRA can evaluate multiple transfer strategies.

Each candidate is checked for:

```text
Delta-v
Propellant requirement
Available propellant
Feasibility
```

The optimizer selects the lowest-delta-v feasible candidate.

---

# Engineering Architecture

ASTRA is deliberately divided into separate computational layers.

```text
┌──────────────────────────────┐
│       Mission Inputs         │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      Orbital Mechanics       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      Transfer Analysis       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│     Propulsion Analysis      │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│     Numerical Simulation     │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│   Validation & Error Analysis │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      Mission Optimizer       │
└──────────────┬───────────────┘
               ↓
┌──────────────────────────────┐
│      Mission Decision        │
└──────────────────────────────┘
```

Visualization sits above these computational components and presents the results through the dashboard.

This separation makes the system easier to:

- Test
- Debug
- Extend
- Validate
- Reuse

A change to the visualization layer should not require rewriting the orbital mechanics layer.

Likewise, the optimizer can use the transfer calculations without knowing how the dashboard displays them.

---

# Core Physics

ASTRA currently uses a simplified two-body Earth-centered gravitational model.

The central physical idea is:

> The spacecraft moves under Earth's gravitational attraction.

For the current model, Earth's gravitational parameter is treated as constant.

The standard gravitational parameter used by ASTRA is:

```text
μ = 3.986004418 × 10^14 m^3/s^2
```

Earth's mean radius is represented using:

```text
Rₑ = 6,371,000 m
```

The standard gravitational acceleration used for propulsion calculations is:

```text
g₀ = 9.80665 m/s²
```

---

# Orbital Mechanics

## What is an Orbit?

An orbit is a path followed by an object under gravity.

For a spacecraft around Earth, the spacecraft is constantly falling toward Earth while also moving sideways fast enough that it continues to miss the surface.

This is why orbital velocity matters.

---

## Orbital Radius vs Altitude

ASTRA distinguishes between:

**Altitude**

Distance above Earth's surface.

and:

**Orbital radius**

Distance from Earth's center.

They are related by:

```text
r = Rₑ + h
```

where:

```text
r  = orbital radius
Rₑ = Earth's radius
h  = altitude
```

This distinction is important because orbital equations use radius from the center of the Earth.

---

## Circular Orbital Velocity

For a circular orbit:

```text
v_c = sqrt(μ / r)
```

where:

```text
v_c = circular orbital velocity
μ   = Earth's gravitational parameter
r   = orbital radius
```

In simple terms:

> A spacecraft farther from Earth needs a lower circular orbital speed than a spacecraft closer to Earth.

---

## Escape Velocity

Escape velocity is:

```text
v_e = sqrt(2μ / r)
```

It is the theoretical velocity required to escape Earth's gravitational field under the idealized two-body model.

ASTRA includes this calculation as part of its orbital mechanics layer.

---

## Orbital Period

For a circular orbit:

```text
T = 2π sqrt(r^3 / μ)
```

where `T` is the orbital period.

In simple terms:

> The farther the spacecraft is from Earth, the longer one complete orbit takes.

---

## Specific Orbital Energy

For a circular orbit:

```text
ε = -μ / (2r)
```

Specific orbital energy is energy per unit spacecraft mass.

It is useful not only as a physics quantity but also as a numerical diagnostic.

For an ideal two-body orbit, the total specific orbital energy should remain approximately constant.

If the numerical simulation causes the energy to drift significantly, that indicates numerical error.

---

# Hohmann Transfers

A Hohmann transfer is a two-burn method for moving between two circular orbits that share the same central body.

For ASTRA's current Earth-centered model, the process is:

```text
Initial circular orbit
          ↓
       First burn
          ↓
   Elliptical transfer
          ↓
      Second burn
          ↓
   Final circular orbit
```

---

## Why Two Burns?

The first burn changes the spacecraft's velocity and places it onto an elliptical transfer orbit.

The spacecraft then naturally travels along that ellipse under gravity.

At the other end of the transfer orbit, a second burn changes the spacecraft's velocity again and circularizes the orbit.

---

## Transfer Semi-Major Axis

The semi-major axis of the Hohmann transfer orbit is:

```text
a_t = (r₁ + r₂) / 2
```

where:

```text
r₁ = initial orbital radius
r₂ = final orbital radius
```

---

## Transfer Velocity

ASTRA uses the vis-viva relationship:

```text
v = sqrt(μ(2/r - 1/a))
```

where:

```text
v = orbital velocity
μ = gravitational parameter
r = current radius
a = orbit semi-major axis
```

This equation is used to calculate velocities on the transfer ellipse.

---

## First Burn

For an orbit-raising Hohmann transfer:

```text
Initial circular orbit
        ↓
Prograde burn
        ↓
Higher elliptical transfer orbit
```

The spacecraft increases its speed.

For an orbit-lowering transfer, the first burn is retrograde.

---

## Second Burn

At the other end of the transfer:

```text
Transfer orbit
      ↓
Second burn
      ↓
Final circular orbit
```

For an orbit-raising transfer, the spacecraft performs a prograde burn.

For an orbit-lowering transfer, the spacecraft performs a retrograde burn.

---

## Total Delta-v

The total mission delta-v is:

```text
Δv_total = Δv₁ + Δv₂
```

Delta-v is one of the most important quantities in orbital mission design.

It represents the total amount of velocity change required by the maneuver sequence.

---

## Transfer Time

For a Hohmann transfer, the spacecraft travels through half of the transfer ellipse.

The transfer time is:

```text
t_transfer = π sqrt(a_t^3 / μ)
```

This is the time between the first and second burns.

---

# Rocket Propulsion and Delta-v

Orbital mechanics tells us how much delta-v is needed.

The rocket equation connects that delta-v to propellant.

ASTRA uses the Tsiolkovsky rocket equation:

```text
Δv = Isp g₀ ln(m₀ / mf)
```

where:

```text
Δv  = velocity change
Isp = specific impulse
g₀  = standard gravitational acceleration
m₀  = initial mass
mf  = final mass
```

---

## What is Specific Impulse?

Specific impulse, written as `Isp`, is a measure of rocket-engine efficiency.

For the same required delta-v:

> A higher-specific-impulse engine generally requires less propellant than a lower-specific-impulse engine.

ASTRA therefore treats propulsion performance as part of mission feasibility.

---

## Why Delta-v Alone Is Not Enough

Suppose two missions require different amounts of delta-v.

The spacecraft also has a limited amount of propellant.

Therefore ASTRA evaluates both:

```text
Required Δv
Required propellant
```

This makes the analysis more useful than reporting delta-v alone.

---

# Numerical Trajectory Simulation

Analytical equations can tell us what should happen under ideal conditions.

ASTRA also performs a numerical simulation to calculate how the spacecraft moves through time.

The spacecraft state is represented by:

```text
(x, y, vx, vy)
```

where:

```text
x  = x-position
y  = y-position
vx = x-velocity
vy = y-velocity
```

The current simulator is two-dimensional.

---

## Gravitational Acceleration

At each point in the simulation, the spacecraft experiences Earth's gravitational acceleration.

The magnitude is based on:

```text
a = μ / r²
```

The direction is toward Earth's center.

The simulator uses the spacecraft's current position to calculate the acceleration.

---

## Why Numerical Simulation?

A numerical simulator allows ASTRA to model the spacecraft's state over time rather than only calculating the beginning and end values.

This produces:

- Position history
- Velocity history
- Trajectory geometry
- Burn states
- Numerical error information

---

# Runge-Kutta 4 Integration

ASTRA uses the **fourth-order Runge-Kutta method**, commonly called **RK4**, to numerically integrate spacecraft motion.

The basic idea is:

> Instead of estimating the spacecraft's next state from only one point, RK4 samples the system multiple times during a timestep and combines those estimates.

This generally provides much better accuracy than a simple first-order integration method for the same timestep.

Conceptually:

```text
Current state
     │
     ├── Estimate 1
     │
     ├── Estimate 2
     │
     ├── Estimate 3
     │
     └── Estimate 4
           │
           ▼
      Weighted average
           │
           ▼
       Next state
```

The simulator repeats this process across the mission timeline.

---

## Timestep

The timestep determines how much simulated time passes during each numerical integration step.

For example:

```text
dt = 10 seconds
```

means the simulator advances approximately ten seconds at a time before calculating the next state.

A smaller timestep usually means:

- More calculations
- Higher computational cost
- Potentially higher numerical accuracy

A larger timestep usually means:

- Fewer calculations
- Lower computational cost
- Potentially larger numerical error

ASTRA explicitly tests timestep sensitivity.

---

# Orbital Burn Modeling

Real spacecraft change velocity using engines or other propulsion systems.

ASTRA currently represents burns as instantaneous velocity changes.

Two burn directions are supported.

## Prograde Burn

A prograde burn adds velocity in the current direction of motion.

```text
v_new = v_old + Δv
```

In the implementation, the burn is applied along the spacecraft's current velocity direction.

---

## Retrograde Burn

A retrograde burn subtracts velocity from the current direction of motion.

```text
v_new = v_old - Δv
```

Again, the direction is determined from the current velocity vector.

---

## Burn Events

Each burn is recorded as an event containing:

- Time
- Delta-v
- State before the burn
- State after the burn
- Burn name
- Burn direction

This creates an explicit mission timeline.

---

# Continuous Mission Simulation

ASTRA does not treat the Hohmann calculation and the numerical simulation as unrelated pieces.

They are combined into one continuous mission simulation.

The mission sequence is:

```text
Initial circular orbit
          ↓
       First burn
          ↓
    Transfer orbit
          ↓
   RK4 propagation
          ↓
      Second burn
          ↓
    Final circular orbit
          ↓
   Final propagation
```

This allows the system to preserve the spacecraft state throughout the mission.

---

## Why This Matters

A simple calculator might tell you:

```text
Required Δv = 217 m/s
```

ASTRA goes further.

It can represent:

```text
Where the spacecraft starts
        ↓
How its velocity changes
        ↓
How its orbit evolves
        ↓
Where the second burn occurs
        ↓
How the final orbit evolves
```

This makes the result inspectable rather than being only a final number.

---

# Trajectory Analysis

ASTRA stores the spacecraft trajectory as a sequence of states and times.

From those states, the system can calculate quantities such as:

- Radius
- Altitude
- Speed
- Orbital energy

These quantities can then be visualized and checked.

For example, a trajectory can be represented as:

```text
Time → Position
Time → Velocity
Time → Altitude
Time → Energy
```

This helps identify whether the simulated spacecraft behaves as expected.

---

# Numerical Validation

One of the important design principles of ASTRA is:

> **A simulation should not be trusted simply because its plot looks correct.**

A visually smooth trajectory can still contain numerical errors.

ASTRA therefore compares numerical results against analytical expectations.

---

## Transfer-Radius Error

At the transfer endpoint, ASTRA compares:

```text
Numerical radius
vs.
Expected final radius
```

The absolute error is:

```text
radius_error = |numerical_radius - expected_radius|
```

The percentage error is:

```text
radius_error_percent =
    radius_error / expected_radius × 100
```

---

## Transfer-Velocity Error

ASTRA similarly compares:

```text
Numerical velocity
vs.
Expected analytical velocity
```

and calculates absolute and percentage error.

---

## Timestep Convergence

ASTRA also checks whether reducing the timestep improves numerical accuracy.

For example:

```text
60 s timestep
      ↓
30 s timestep
      ↓
10 s timestep
      ↓
5 s timestep
```

The simulation can then be compared at each resolution.

A useful numerical method should generally become more accurate as the timestep becomes sufficiently smaller.

---

## Orbital-Energy Drift

For an ideal two-body orbit, specific orbital energy should remain approximately constant.

ASTRA therefore tracks energy during propagation.

Conceptually:

```text
Expected energy
       │
       ├───────────────
       │
Numerical energy
       ├───────────────
       │
       └── small deviation
```

The deviation gives another measure of numerical stability.

---

# Transfer Strategy Optimization

ASTRA includes an optimization layer rather than assuming that one transfer method is always best.

The current optimizer compares:

```text
Hohmann transfer
vs.
Bi-elliptic transfers
```

The optimizer can search a range of intermediate apoapsis altitudes for the bi-elliptic strategy.

---

## Candidate Evaluation

Each candidate is evaluated using:

```text
Total Δv
Required propellant
Available propellant
Feasibility
```

The optimizer then filters the candidates.

Conceptually:

```text
Generate candidate
       ↓
Calculate Δv
       ↓
Calculate propellant
       ↓
Check feasibility
       ↓
Keep candidate
       ↓
Compare with others
```

The selected result is the:

> **Lowest-delta-v feasible strategy.**

---

# Hohmann vs Bi-Elliptic Transfers

## Hohmann Transfer

A Hohmann transfer uses two burns.

```text
Initial orbit
     ↓
First burn
     ↓
Transfer ellipse
     ↓
Second burn
     ↓
Final orbit
```

It is simple and highly efficient for many circular-orbit transfers.

---

## Bi-Elliptic Transfer

A bi-elliptic transfer introduces an intermediate high orbit.

Conceptually:

```text
Initial orbit
     ↓
First burn
     ↓
High intermediate orbit
     ↓
Second burn
     ↓
Transfer toward final orbit
     ↓
Third burn
     ↓
Final orbit
```

The intermediate orbit creates another possible transfer geometry.

---

## Why Compare Them?

Orbital mechanics contains trade-offs.

A strategy that is best for one mission may not be best for another.

For relatively small ratios between initial and final orbital radii, Hohmann transfers are generally very competitive.

For sufficiently large orbital-radius ratios, a bi-elliptic transfer can require less total delta-v.

ASTRA's optimizer demonstrates this trade-off computationally rather than assuming the answer beforehand.

---

## Bi-Elliptic Search

ASTRA allows the user to specify:

```text
Minimum intermediate altitude
Maximum intermediate altitude
Search step
```

For each candidate intermediate altitude, ASTRA calculates the total delta-v and propellant requirement.

Example:

```text
Candidate 1 → 1500 km
Candidate 2 → 2000 km
Candidate 3 → 2500 km
Candidate 4 → 3000 km
...
```

The optimizer evaluates these candidates and selects the best feasible one.

---

# Mission Feasibility

A mission can be physically possible but infeasible for a particular spacecraft.

For example:

```text
Required propellant = 300 kg
Available propellant = 100 kg
```

The maneuver may be mathematically defined, but the spacecraft does not have enough propellant under the model.

ASTRA therefore explicitly evaluates:

```text
required_propellant <= available_propellant
```

If this condition is true:

```text
Feasible
```

Otherwise:

```text
Infeasible
```

The same concept is applied to transfer candidates during optimization.

---

# Interactive Dashboard

ASTRA includes an interactive **Streamlit** dashboard.

The dashboard turns the underlying engineering calculations into an interface where mission parameters can be changed and the results can be inspected.

---

## Mission Configuration

The dashboard allows the user to specify:

- Mission name
- Initial altitude
- Target altitude
- Spacecraft mass
- Specific impulse
- Available propellant

---

## Mission Summary

The dashboard displays:

- Required delta-v
- Fuel required
- Fuel remaining
- Transfer time
- Mission feasibility

---

## Trajectory Visualization

The dashboard visualizes:

- Earth
- Initial orbit
- Transfer trajectory
- Final orbit
- Burn locations
- Spacecraft trajectory

This provides an immediate geometric view of the mission.

---

## Transfer Analysis

The dashboard displays:

- First burn
- Second burn
- Transfer semi-major axis
- Transfer time
- Total delta-v

---

## Optimization

The dashboard includes:

- Hohmann baseline
- Bi-elliptic candidate search
- Best feasible strategy
- Delta-v savings
- Propellant savings
- Candidate comparison
- Strategy comparison graph

---

## Numerical Stability

The dashboard also exposes numerical validation results including:

- Altitude error
- Velocity error
- Energy drift
- Expected orbital quantities

This makes numerical quality visible rather than hiding it inside the code.

---

# Example Mission

Consider this mission:

| Parameter | Value |
|---|---:|
| Initial altitude | 400 km |
| Target altitude | 800 km |
| Spacecraft mass | 1000 kg |
| Specific impulse | 300 s |
| Available propellant | 500 kg |

ASTRA produces approximately:

| Result | Value |
|---|---:|
| Total Δv | 217 m/s |
| Required propellant | 71.11 kg |
| Remaining propellant | 428.89 kg |
| Transfer time | 0.80 hr |
| Mission status | Feasible |

For this relatively small orbital-radius change, the optimizer selects the Hohmann strategy.

---

## What Does 217 m/s Mean?

It means the spacecraft needs a total modeled velocity change of approximately:

```text
217 m/s
```

across the two burns.

Approximately:

```text
First burn  ≈ 109 m/s
Second burn ≈ 108 m/s
```

The exact values are calculated by ASTRA from the orbital equations.

---

## What Does 71.11 kg Mean?

The rocket equation predicts that approximately:

```text
71.11 kg
```

of propellant is required for the modeled delta-v and spacecraft propulsion parameters.

With:

```text
500 kg available
```

the modeled remaining propellant is approximately:

```text
428.89 kg
```

Therefore the mission is classified as feasible.

---

# Testing

ASTRA uses automated tests to protect the correctness of its computational components.

Testing is important because aerospace calculations can produce plausible-looking numbers even when an implementation contains an error.

The test suite covers:

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

The current development milestone has:

```text
99 passed
```

---

## Running Tests

From the project environment:

```text
pytest -q
```

A successful run should report the passing test count.

The test suite provides regression protection as ASTRA develops.

---

# Project Structure

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

# Technology Stack

ASTRA is built primarily with Python.

## Python

Used for:

- Physics calculations
- Numerical simulation
- Mission logic
- Optimization
- Validation

## Matplotlib

Used for engineering plots and trajectory visualization.

## Pandas

Used for structured data handling in the dashboard and analysis workflow.

## Streamlit

Used to provide the interactive mission-analysis dashboard.

## Pytest

Used for automated testing and regression protection.

## Git and GitHub

Used for version control and open-source project development.

The project targets:

```text
Python 3.13
```

---

# Physical Model and Assumptions

ASTRA currently uses an idealized Earth-centered two-body model.

This means the simulation focuses on the gravitational interaction between:

```text
Earth
+
Spacecraft
```

The current model assumes:

- Earth is the central gravitational body.
- Earth's gravitational parameter is constant.
- The spacecraft does not affect Earth's motion.
- Motion is two-dimensional.
- Burns are instantaneous.
- Propulsion is idealized.
- Atmospheric drag is ignored.
- Third-body gravity is ignored.
- Solar radiation pressure is ignored.

These assumptions are deliberate.

They allow the project to focus on understanding and validating fundamental orbital mechanics and numerical methods before adding higher-fidelity effects.

---

# Current Limitations

ASTRA is a computational engineering project and is **not a flight-certified mission-design system**.

The current model does not yet include:

## Gravity and Environment

- Earth's oblateness
- J2 perturbations
- Lunar gravity
- Solar gravity
- General third-body perturbations
- Solar radiation pressure
- Atmospheric drag

## Propulsion

- Finite-duration engine burns
- Throttle dynamics
- Thrust-vector control
- Detailed engine performance
- Propellant tank dynamics

## Spacecraft Dynamics

- Three-dimensional attitude dynamics
- Reaction wheels
- Control systems
- Flexible-body dynamics

## Mission Design

- Launch-window constraints
- Real spacecraft hardware limitations
- Full ephemeris data
- Detailed launch vehicle modeling
- Real operational constraints

## Numerical Model

- Full three-dimensional propagation
- Adaptive timestep integration
- High-fidelity force models

These limitations are important because they define exactly what the current version of ASTRA is intended to model.

---

# Future Development

ASTRA is designed so that more advanced engineering models can be added over time.

## Orbital Mechanics

Potential extensions include:

- Three-dimensional orbital propagation
- Inclination-change maneuvers
- Plane-change optimization
- J2 perturbation modeling
- Lambert-transfer calculations
- More general orbital-transfer methods

## Numerical Simulation

Potential extensions include:

- Adaptive timestep integration
- Higher-order numerical integrators
- Finite-duration thrust
- Thrust-vector control
- Atmospheric models
- Higher-fidelity force models

## Mission Design

Potential extensions include:

- Multi-burn missions
- Multi-orbit missions
- Launch-window analysis
- Interplanetary transfers
- Multi-body mission analysis
- Mission constraints

## Optimization

Potential extensions include:

- Multi-variable trajectory optimization
- Constrained optimization
- Global optimization
- Propellant-cost optimization
- Time-vs-delta-v trade studies
- Multi-objective optimization

## Visualization

Potential extensions include:

- Three-dimensional trajectories
- Orbital-element plots
- Interactive mission timelines
- Engineering reports
- Mission playback

---

# Engineering Design Principles

ASTRA is being developed around several principles.

## 1. Physics First

The system should use explicit physical relationships.

Important outputs should be traceable back to equations or numerical models.

---

## 2. Separate Calculation from Presentation

The physics engine should not depend on the dashboard.

This makes the computational components reusable.

---

## 3. Validate Numerical Results

A simulation should be compared against analytical expectations wherever possible.

---

## 4. Test Components Independently

Orbital calculations, transfers, propulsion, simulation, validation, and optimization should be testable separately.

---

## 5. Make Engineering Trade-offs Visible

The system should expose meaningful mission quantities such as:

- Delta-v
- Propellant
- Transfer time
- Numerical error
- Mission feasibility

---

## 6. Prefer Transparent Models

The current ASTRA model is intentionally understandable.

The equations and assumptions are visible instead of hiding the calculation behind an opaque system.

---

# AI-Assisted Development

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
- Numerical verification
- Integration
- Final project decisions

AI-assisted code was reviewed and tested before integration.

AI was **not** used to fabricate:

- Development hours
- Project activity
- Test results
- Engineering work

The purpose of using AI was to accelerate development while keeping engineering decisions, verification, and responsibility with the developer.

---

# Engineering Concepts Demonstrated

ASTRA combines multiple areas of computational engineering.

```text
                         ASTRA
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       PHYSICS         MATHEMATICS      PROGRAMMING
          │                │                │
          ▼                ▼                ▼
 Orbital Mechanics   Analytical Models  Scientific
 Propulsion          Numerical Methods  Computing
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                      SIMULATION
                           │
                           ▼
                  Trajectory Propagation
                           │
                           ▼
                      VALIDATION
                           │
                           ▼
                     OPTIMIZATION
                           │
                           ▼
                    Mission Strategy
```

The project demonstrates concepts including:

- Orbital mechanics
- Newtonian gravity
- Analytical modeling
- Numerical integration
- RK4 methods
- Error analysis
- Convergence testing
- Rocket propulsion
- Delta-v budgeting
- Mission feasibility
- Algorithmic optimization
- Scientific visualization
- Software architecture
- Automated testing

The goal is to combine these areas into one coherent computational aerospace workflow.

---

# How to Run ASTRA

## 1. Clone the Repository

```text
git clone https://github.com/HeamakeshBajina/astra-mission-designer.git
```

Then enter the project:

```text
cd astra-mission-designer
```

---

## 2. Create a Virtual Environment

On Windows:

```text
python -m venv .venv
```

Activate it:

```text
.venv\Scripts\activate
```

---

## 3. Install the Project

Install the project and its development dependencies using the project's package configuration.

```text
pip install -e ".[dev]"
```

---

## 4. Run the Tests

```text
pytest -q
```

The current development milestone has 99 passing tests.

---

## 5. Launch the Dashboard

Run:

```text
streamlit run app.py
```

Streamlit will start the local dashboard.

Open the local address provided by Streamlit in your browser.

---

# Understanding the Main Output

When ASTRA runs a mission, the most important results are:

## Required Delta-v

The total velocity change required by the modeled transfer.

Lower delta-v generally means a less demanding maneuver under the same assumptions.

## Required Propellant

The amount of propellant predicted by the rocket equation.

## Remaining Propellant

Available propellant minus modeled propellant required.

## Transfer Time

The modeled time required to move between the initial and target orbital states.

## Mission Feasibility

Whether the spacecraft has enough modeled propellant for the selected strategy.

## Numerical Error

A measurement of how closely the numerical simulation agrees with analytical expectations.

## Best Strategy

The lowest-delta-v strategy among the candidates that satisfy the propellant constraint.

---

# Why ASTRA Is More Than a Calculator

A basic orbital calculator might perform:

```text
Input → Equation → Number
```

ASTRA instead performs:

```text
Input
  ↓
Physics
  ↓
Analytical Model
  ↓
Propulsion Model
  ↓
Numerical Simulation
  ↓
Validation
  ↓
Optimization
  ↓
Engineering Decision
```

This distinction is important.

The project does not only calculate what should happen.

It also:

- Simulates what happens over time.
- Checks the numerical solution.
- Compares alternative strategies.
- Applies mission constraints.
- Presents the engineering trade-offs.

---

# Reproducibility

ASTRA is designed around deterministic calculations.

Given the same:

```text
Initial conditions
Mission parameters
Physical constants
Numerical timestep
Optimization settings
```

the computational workflow should produce reproducible results.

This makes the system suitable for:

- Regression testing
- Numerical experiments
- Parameter studies
- Optimization experiments
- Future research extensions

---

# Project Status

**Status: Active Development**

The current milestone includes:

- Core orbital mechanics
- Circular-orbit calculations
- Hohmann transfer analysis
- Rocket-equation calculations
- Numerical RK4 propagation
- Orbital burn modeling
- Continuous Hohmann mission simulation
- Trajectory analysis
- Numerical validation
- Timestep convergence testing
- Hohmann vs bi-elliptic optimization
- Propellant feasibility analysis
- Interactive dashboard
- Automated testing

The project is intended to evolve toward increasingly realistic computational spacecraft and mission-design models.

---

# License

ASTRA is released under the MIT License.

See the `LICENSE` file for the complete license text.

---

# 🚀 ASTRA

**Computational aerospace engineering through physics, simulation, validation, and optimization.**

Built as a physics-first exploration of how spacecraft missions can be modeled computationally.
