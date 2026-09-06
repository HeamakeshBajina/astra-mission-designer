"""ASTRA interactive mission planning dashboard."""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from astra.mission.optimizer import optimize_transfer_strategy
from astra.mission.planner import create_mission_plan
from astra.physics.constants import EARTH_RADIUS, EARTH_MU
from astra.physics.orbital import (
    circular_orbital_velocity,
    orbital_period,
)
from astra.physics.transfers import hohmann_transfer
from astra.simulation.mission_trajectory import (
    simulate_continuous_hohmann,
)
from astra.simulation.propagator import State
from astra.simulation.trajectory import propagate_trajectory
from astra.simulation.trajectory_analysis import analyze_trajectory


st.set_page_config(
    page_title="ASTRA Mission Designer",
    page_icon="🚀",
    layout="wide",
)


st.title("🚀 ASTRA Mission Designer")

st.write(
    "Computational aerospace mission analysis, orbital simulation, "
    "and mission optimization."
)

st.divider()


# =========================================================
# Mission parameters
# =========================================================

st.sidebar.header("Mission Parameters")

mission_name = st.sidebar.text_input(
    "Mission name",
    value="LEO Raise",
)

initial_altitude_km = st.sidebar.number_input(
    "Initial altitude (km)",
    min_value=0.0,
    value=400.0,
    step=10.0,
)

final_altitude_km = st.sidebar.number_input(
    "Target altitude (km)",
    min_value=0.0,
    value=800.0,
    step=10.0,
)

spacecraft_mass = st.sidebar.number_input(
    "Spacecraft mass (kg)",
    min_value=0.1,
    value=1000.0,
    step=50.0,
)

specific_impulse = st.sidebar.number_input(
    "Specific impulse (s)",
    min_value=0.1,
    value=300.0,
    step=10.0,
)

available_propellant = st.sidebar.number_input(
    "Available propellant (kg)",
    min_value=0.0,
    value=500.0,
    step=25.0,
)


try:
    # =====================================================
    # Mission analysis
    # =====================================================

    plan = create_mission_plan(
        mission_name=mission_name,
        initial_altitude=initial_altitude_km * 1_000,
        final_altitude=final_altitude_km * 1_000,
        spacecraft_mass=spacecraft_mass,
        specific_impulse=specific_impulse,
        available_propellant=available_propellant,
    )

    profile = plan.profile

    st.subheader(plan.mission_name)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Required Δv",
        f"{profile.required_delta_v / 1_000:.3f} km/s",
    )

    col2.metric(
        "Fuel Required",
        f"{profile.required_propellant:.2f} kg",
    )

    col3.metric(
        "Fuel Remaining",
        f"{max(profile.remaining_propellant, 0):.2f} kg",
    )

    col4.metric(
        "Transfer Time",
        f"{profile.transfer_time / 3600:.2f} hr",
    )

    st.divider()

    if profile.feasible:
        st.success(
            "MISSION FEASIBLE — available propellant is sufficient."
        )
    else:
        st.error(
            "MISSION INFEASIBLE — available propellant is insufficient."
        )

    # =====================================================
    # Mission summary
    # =====================================================

    st.subheader("Mission Summary")

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:
        st.write(
            f"**Initial orbit:** "
            f"{profile.initial_altitude / 1_000:.1f} km"
        )

        st.write(
            f"**Target orbit:** "
            f"{profile.final_altitude / 1_000:.1f} km"
        )

        st.write(
            f"**Spacecraft mass:** "
            f"{profile.spacecraft_mass:.1f} kg"
        )

    with summary_col2:
        st.write(
            f"**Specific impulse:** "
            f"{profile.specific_impulse:.1f} s"
        )

        st.write(
            f"**Available propellant:** "
            f"{profile.available_propellant:.1f} kg"
        )

        st.write(
            f"**Required propellant:** "
            f"{profile.required_propellant:.2f} kg"
        )

    st.divider()

    # =====================================================
    # Orbital radii
    # =====================================================

    initial_radius = (
        EARTH_RADIUS + profile.initial_altitude
    )

    final_radius = (
        EARTH_RADIUS + profile.final_altitude
    )

    transfer = hohmann_transfer(
        initial_radius,
        final_radius,
    )

    # =====================================================
    # Continuous mission simulation
    # =====================================================

    st.subheader("Continuous Mission Simulation")

    st.caption(
        "Numerically propagated spacecraft trajectory with "
        "two instantaneous Hohmann burns."
    )

    mission_trajectory = simulate_continuous_hohmann(
        initial_radius=initial_radius,
        final_radius=final_radius,
        dt=10,
    )

    figure, axis = plt.subplots(
        figsize=(9, 9),
    )

    x_positions = [
        state.x / 1_000
        for state in mission_trajectory.states
    ]

    y_positions = [
        state.y / 1_000
        for state in mission_trajectory.states
    ]

    axis.plot(
        x_positions,
        y_positions,
        label="Spacecraft trajectory",
    )

    earth = plt.Circle(
        (0, 0),
        EARTH_RADIUS / 1_000,
        fill=True,
        alpha=0.35,
        label="Earth",
    )

    axis.add_patch(earth)

    for index, burn in enumerate(
        mission_trajectory.burns,
        start=1,
    ):
        axis.scatter(
            burn.state_before.x / 1_000,
            burn.state_before.y / 1_000,
            s=80,
            marker="*",
            label=f"Burn {index}",
        )

    axis.set_xlabel("X Position (km)")
    axis.set_ylabel("Y Position (km)")
    axis.set_title("ASTRA Continuous Hohmann Mission")
    axis.set_aspect("equal")
    axis.legend()

    st.pyplot(
        figure,
        clear_figure=True,
    )

    plt.close(figure)

    # =====================================================
    # Transfer details
    # =====================================================

    st.subheader("Transfer Details")

    transfer_col1, transfer_col2, transfer_col3 = st.columns(3)

    transfer_col1.metric(
        "First Burn Δv",
        f"{transfer.first_burn_delta_v / 1_000:.3f} km/s",
    )

    transfer_col2.metric(
        "Second Burn Δv",
        f"{transfer.second_burn_delta_v / 1_000:.3f} km/s",
    )

    transfer_col3.metric(
        "Total Δv",
        f"{transfer.total_delta_v / 1_000:.3f} km/s",
    )

    st.divider()

    # =====================================================
    # Burn timeline
    # =====================================================

    st.subheader("Burn Timeline")

    for burn in mission_trajectory.burns:
        st.write(
            f"**{burn.name}** — "
            f"t = {burn.time / 3600:.3f} hr — "
            f"Δv = {burn.delta_v / 1_000:.3f} km/s"
        )

    st.divider()

    # =====================================================
    # Transfer strategy optimization
    # =====================================================

    st.subheader("Transfer Strategy Optimization")

    st.caption(
        "Compares a baseline Hohmann transfer against "
        "bi-elliptic transfer candidates."
    )

    optimizer_col1, optimizer_col2 = st.columns(2)

    with optimizer_col1:
        minimum_intermediate_altitude_km = (
            st.number_input(
                "Minimum intermediate apoapsis (km)",
                min_value=1.0,
                value=max(
                    final_altitude_km + 700.0,
                    1500.0,
                ),
                step=500.0,
            )
        )

    with optimizer_col2:
        maximum_intermediate_altitude_km = (
            st.number_input(
                "Maximum intermediate apoapsis (km)",
                min_value=1.0,
                value=max(
                    final_altitude_km + 4700.0,
                    5500.0,
                ),
                step=500.0,
            )
        )

    search_resolution_km = st.number_input(
        "Search resolution (km)",
        min_value=1.0,
        value=500.0,
        step=100.0,
    )

    run_optimization = st.button(
        "Run Transfer Optimization",
        type="primary",
    )

    if run_optimization:
        try:
            optimization = optimize_transfer_strategy(
                initial_altitude=profile.initial_altitude,
                final_altitude=profile.final_altitude,
                spacecraft_mass=profile.spacecraft_mass,
                specific_impulse=profile.specific_impulse,
                available_propellant=profile.available_propellant,
                minimum_intermediate_altitude=(
                    minimum_intermediate_altitude_km * 1_000
                ),
                maximum_intermediate_altitude=(
                    maximum_intermediate_altitude_km * 1_000
                ),
                step=search_resolution_km * 1_000,
            )

            st.session_state["optimization"] = optimization
            st.session_state.pop(
                "optimization_error",
                None,
            )

        except ValueError as error:
            st.session_state["optimization_error"] = str(error)

    optimization = st.session_state.get(
        "optimization"
    )

    optimization_error = st.session_state.get(
        "optimization_error"
    )

    if optimization_error:
        st.error(optimization_error)

    if optimization is not None:
        best = optimization.best_candidate

        st.success(
            "OPTIMIZATION COMPLETE — "
            "lowest-Δv feasible strategy identified."
        )

        result_col1, result_col2, result_col3 = st.columns(3)

        result_col1.metric(
            "Best Strategy",
            best.strategy,
        )

        result_col2.metric(
            "Optimized Δv",
            f"{best.total_delta_v / 1_000:.3f} km/s",
        )

        result_col3.metric(
            "Required Propellant",
            f"{best.required_propellant:.2f} kg",
        )

        hohmann_candidate = next(
            candidate
            for candidate in optimization.candidates
            if candidate.strategy == "Hohmann"
        )

        delta_v_savings = (
            hohmann_candidate.total_delta_v
            - best.total_delta_v
        )

        propellant_savings = (
            hohmann_candidate.required_propellant
            - best.required_propellant
        )

        if best.strategy == "Hohmann":
            st.info(
                "Hohmann remains the lowest-Δv strategy "
                "for this mission."
            )
        else:
            st.success(
                f"{best.strategy} improves on the Hohmann "
                "baseline for this mission."
            )

        savings_col1, savings_col2, savings_col3 = st.columns(3)

        savings_col1.metric(
            "Δv Savings vs Hohmann",
            f"{delta_v_savings:.1f} m/s",
        )

        savings_col2.metric(
            "Propellant Savings",
            f"{propellant_savings:.2f} kg",
        )

        if best.intermediate_altitude is None:
            optimal_apoapsis_text = "N/A"
        else:
            optimal_apoapsis_text = (
                f"{best.intermediate_altitude / 1_000:.0f} km"
            )

        savings_col3.metric(
            "Optimal Intermediate Apoapsis",
            optimal_apoapsis_text,
        )

        # -------------------------------------------------
        # Candidate table
        # -------------------------------------------------

        st.subheader("Strategy Comparison")

        candidate_rows = []

        for candidate in optimization.candidates:
            if candidate.intermediate_altitude is None:
                intermediate_text = "None"
            else:
                intermediate_text = (
                    f"{candidate.intermediate_altitude / 1_000:.0f}"
                )

            candidate_rows.append(
                {
                    "Strategy": candidate.strategy,
                    "Intermediate Apoapsis (km)": (
                        intermediate_text
                    ),
                    "Δv (km/s)": round(
                        candidate.total_delta_v / 1_000,
                        4,
                    ),
                    "Propellant (kg)": round(
                        candidate.required_propellant,
                        4,
                    ),
                    "Feasible": candidate.feasible,
                }
            )

        candidate_dataframe = pd.DataFrame(
            candidate_rows
        )

        st.dataframe(
            candidate_dataframe,
            use_container_width=True,
            hide_index=True,
        )

        # -------------------------------------------------
        # Optimization plot
        # -------------------------------------------------

        bielliptic_candidates = [
            candidate
            for candidate in optimization.candidates
            if candidate.strategy == "Bi-elliptic"
        ]

        if bielliptic_candidates:
            apoapsis_values = [
                candidate.intermediate_altitude / 1_000
                for candidate in bielliptic_candidates
            ]

            delta_v_values = [
                candidate.total_delta_v / 1_000
                for candidate in bielliptic_candidates
            ]

            optimization_figure, optimization_axis = (
                plt.subplots(
                    figsize=(10, 6)
                )
            )

            optimization_axis.plot(
                apoapsis_values,
                delta_v_values,
                marker="o",
                label="Bi-elliptic",
            )

            optimization_axis.axhline(
                hohmann_candidate.total_delta_v / 1_000,
                linestyle="--",
                label="Hohmann baseline",
            )

            if best.intermediate_altitude is not None:
                optimization_axis.scatter(
                    best.intermediate_altitude / 1_000,
                    best.total_delta_v / 1_000,
                    s=120,
                    marker="*",
                    label="Best candidate",
                )

            optimization_axis.set_xlabel(
                "Intermediate Apoapsis (km)"
            )

            optimization_axis.set_ylabel(
                "Total Δv (km/s)"
            )

            optimization_axis.set_title(
                "Orbital Transfer Strategy Search"
            )

            optimization_axis.legend()

            optimization_figure.tight_layout()

            st.pyplot(
                optimization_figure,
                clear_figure=True,
            )

            plt.close(
                optimization_figure
            )

    st.divider()

    # =====================================================
    # Initial orbit analysis
    # =====================================================

    st.subheader("Initial Orbit Analysis")

    initial_velocity = circular_orbital_velocity(
        initial_radius
    )

    initial_period = orbital_period(
        initial_radius
    )

    initial_state = State(
        x=initial_radius,
        y=0.0,
        vx=0.0,
        vy=initial_velocity,
    )

    trajectory = propagate_trajectory(
        initial_state=initial_state,
        duration=initial_period,
        dt=10,
    )

    analysis = analyze_trajectory(
        trajectory
    )

    times = trajectory.times

    altitudes_km = [
        altitude / 1_000
        for altitude in analysis.altitudes
    ]

    speeds_km_s = [
        speed / 1_000
        for speed in analysis.speeds
    ]

    energies_mj_kg = [
        energy / 1_000_000
        for energy in analysis.specific_energies
    ]

    # =====================================================
    # Analytical circular-orbit baselines
    # =====================================================

    expected_altitude_km = (
        profile.initial_altitude / 1_000
    )

    expected_speed_km_s = (
        initial_velocity / 1_000
    )

    expected_energy_mj_kg = (
        -EARTH_MU
        / (2 * initial_radius)
        / 1_000_000
    )

    # =====================================================
    # Numerical deviations
    # =====================================================

    altitude_deviation_m = [
        (altitude - expected_altitude_km) * 1_000
        for altitude in altitudes_km
    ]

    speed_deviation_m_s = [
        (speed - expected_speed_km_s) * 1_000
        for speed in speeds_km_s
    ]

    energy_deviation_j_kg = [
        (energy - expected_energy_mj_kg) * 1_000_000
        for energy in energies_mj_kg
    ]

    max_altitude_error_m = max(
        abs(value)
        for value in altitude_deviation_m
    )

    max_speed_error_m_s = max(
        abs(value)
        for value in speed_deviation_m_s
    )

    max_energy_error_j_kg = max(
        abs(value)
        for value in energy_deviation_j_kg
    )

    # =====================================================
    # Numerical error plots
    # =====================================================

    stability_figure, stability_axes = plt.subplots(
        3,
        1,
        figsize=(10, 10),
    )

    # -----------------------------------------------------
    # Altitude error
    # -----------------------------------------------------

    stability_axes[0].plot(
        times,
        altitude_deviation_m,
    )

    stability_axes[0].axhline(
        0,
        linestyle="--",
        linewidth=1,
    )

    stability_axes[0].set_xlabel(
        "Time (s)"
    )

    stability_axes[0].set_ylabel(
        "Altitude Error (m)"
    )

    stability_axes[0].set_title(
        "Altitude Deviation from Circular-Orbit Baseline"
    )

    # -----------------------------------------------------
    # Velocity error
    # -----------------------------------------------------

    stability_axes[1].plot(
        times,
        speed_deviation_m_s,
    )

    stability_axes[1].axhline(
        0,
        linestyle="--",
        linewidth=1,
    )

    stability_axes[1].set_xlabel(
        "Time (s)"
    )

    stability_axes[1].set_ylabel(
        "Velocity Error (m/s)"
    )

    stability_axes[1].set_title(
        "Velocity Deviation from Circular-Orbit Baseline"
    )

    # -----------------------------------------------------
    # Energy error
    # -----------------------------------------------------

    stability_axes[2].plot(
        times,
        energy_deviation_j_kg,
    )

    stability_axes[2].axhline(
        0,
        linestyle="--",
        linewidth=1,
    )

    stability_axes[2].set_xlabel(
        "Time (s)"
    )

    stability_axes[2].set_ylabel(
        "Energy Error (J/kg)"
    )

    stability_axes[2].set_title(
        "Specific Orbital Energy Drift"
    )

    stability_figure.tight_layout()

    st.pyplot(
        stability_figure,
        clear_figure=True,
    )

    plt.close(
        stability_figure
    )

    # =====================================================
    # Numerical stability
    # =====================================================

    st.subheader("Numerical Stability")

    st.caption(
        "These values quantify numerical integration error "
        "during one simulated circular orbit."
    )

    if (
        max_altitude_error_m < 1.0
        and max_speed_error_m_s < 0.01
    ):
        st.success(
            "NUMERICAL VALIDATION PASSED — "
            "the propagated circular orbit remains "
            "within the selected engineering tolerance."
        )
    else:
        st.warning(
            "NUMERICAL VALIDATION WARNING — "
            "the propagation error is larger than "
            "the expected tolerance."
        )

    stability_col1, stability_col2, stability_col3 = (
        st.columns(3)
    )

    stability_col1.metric(
        "Maximum Altitude Error",
        f"{max_altitude_error_m:.6f} m",
    )

    stability_col2.metric(
        "Maximum Velocity Error",
        f"{max_speed_error_m_s:.9f} m/s",
    )

    stability_col3.metric(
        "Maximum Energy Drift",
        f"{max_energy_error_j_kg:.6f} J/kg",
    )

    st.write(
        f"**Expected altitude:** "
        f"{expected_altitude_km:.3f} km"
    )

    st.write(
        f"**Expected circular velocity:** "
        f"{expected_speed_km_s:.6f} km/s"
    )

    st.write(
        f"**Expected specific orbital energy:** "
        f"{expected_energy_mj_kg:.9f} MJ/kg"
    )

    st.divider()

    # =====================================================
    # Initial orbit properties
    # =====================================================

    st.subheader("Initial Orbit Properties")

    orbit_col1, orbit_col2, orbit_col3 = st.columns(3)

    orbit_col1.metric(
        "Orbital Velocity",
        f"{initial_velocity / 1_000:.3f} km/s",
    )

    orbit_col2.metric(
        "Orbital Period",
        f"{initial_period / 3600:.2f} hr",
    )

    orbit_col3.metric(
        "Orbit Altitude",
        f"{profile.initial_altitude / 1_000:.1f} km",
    )


except ValueError as error:
    st.error(str(error))