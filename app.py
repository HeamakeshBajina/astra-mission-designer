"""ASTRA interactive mission planning dashboard."""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from astra.mission.advanced_mission import analyze_advanced_mission
from astra.mission.burn_sequence import (
    MissionBurn,
    create_burn_sequence,
)
from astra.mission.constraints import (
    MissionConstraints,
    evaluate_delta_v_feasibility,
)
from astra.mission.mission_execution import (
    MissionExecutionEvent,
    create_mission_execution_plan,
    execute_mission,
)
from astra.mission.mission_timeline import (
    MissionEvent,
    MissionEventType,
    create_mission_timeline,
)
from astra.mission.optimizer import optimize_transfer_strategy
from astra.mission.planner import create_mission_plan
from astra.mission.propellant_analysis import (
    evaluate_propellant_feasibility,
)
from astra.physics.constants import EARTH_RADIUS, EARTH_MU
from astra.physics.burn_vector import BurnVector
from astra.physics.orbital import (
    circular_orbital_velocity,
    orbital_period,
)
from astra.physics.rocket import delta_v_from_mass_ratio
from astra.physics.transfers import hohmann_transfer
from astra.physics.thrust import ThrustModel
from astra.simulation.mission_executor import execute_burn_sequence
from astra.simulation.propagator_3d_thrust import State3DThrust
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


st.title("ASTRA Mission Designer")

st.write(
    "Computational aerospace mission analysis, orbital simulation, "
    "mission optimization, and numerical validation."
)

st.divider()


# ---------------------------------------------------------------------------
# Mission parameters
# ---------------------------------------------------------------------------

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
    "Spacecraft initial mass (kg)",
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

inclination_change_deg = st.sidebar.number_input(
    "Inclination change (deg)",
    min_value=0.0,
    max_value=180.0,
    value=0.0,
    step=1.0,
)


try:
    # -----------------------------------------------------------------------
    # Base mission plan
    # -----------------------------------------------------------------------

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
        "Required Delta-v",
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

    # -----------------------------------------------------------------------
    # Mission summary
    # -----------------------------------------------------------------------

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
            f"**Spacecraft initial mass:** "
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

    # -----------------------------------------------------------------------
    # Radii and analytical Hohmann transfer
    # -----------------------------------------------------------------------

    initial_radius = EARTH_RADIUS + profile.initial_altitude
    final_radius = EARTH_RADIUS + profile.final_altitude

    transfer = hohmann_transfer(
        initial_radius,
        final_radius,
    )

    # -----------------------------------------------------------------------
    # Advanced mission analysis
    # -----------------------------------------------------------------------

    st.subheader("Advanced Mission Analysis")

    st.caption(
        "Combines orbital-transfer delta-v with an analytical "
        "instantaneous plane-change maneuver."
    )

    advanced_mission = analyze_advanced_mission(
        initial_radius=initial_radius,
        final_radius=final_radius,
        inclination_change=inclination_change_deg,
    )

    advanced_col1, advanced_col2, advanced_col3, advanced_col4 = (
        st.columns(4)
    )

    advanced_col1.metric(
        "Hohmann Delta-v",
        f"{advanced_mission.hohmann_delta_v / 1_000:.3f} km/s",
    )

    advanced_col2.metric(
        "Plane Change Delta-v",
        f"{advanced_mission.plane_change_delta_v / 1_000:.3f} km/s",
    )

    advanced_col3.metric(
        "Combined Delta-v",
        f"{advanced_mission.combined_delta_v / 1_000:.3f} km/s",
    )

    advanced_col4.metric(
        "Transfer Time",
        f"{advanced_mission.transfer_time / 3600:.2f} hr",
    )

    if inclination_change_deg == 0:
        st.info(
            "No inclination change selected. "
            "The combined maneuver is equivalent to the Hohmann transfer."
        )
    else:
        st.info(
            f"Analytical plane change: "
            f"{inclination_change_deg:.1f} degrees at the target orbit."
        )

    # -----------------------------------------------------------------------
    # Propellant-constrained advanced analysis
    # -----------------------------------------------------------------------

    st.subheader("Propellant Feasibility")

    if available_propellant < spacecraft_mass:
        dry_mass = spacecraft_mass - available_propellant

        advanced_propellant = evaluate_propellant_feasibility(
            dry_mass=dry_mass,
            propellant_available=available_propellant,
            specific_impulse=specific_impulse,
            required_delta_v=advanced_mission.combined_delta_v,
        )

        prop_col1, prop_col2, prop_col3, prop_col4 = st.columns(4)

        prop_col1.metric(
            "Initial Mass",
            f"{advanced_propellant.initial_mass:.2f} kg",
        )

        prop_col2.metric(
            "Propellant Required",
            f"{advanced_propellant.propellant_required:.2f} kg",
        )

        prop_col3.metric(
            "Propellant Remaining",
            f"{max(advanced_propellant.propellant_remaining, 0):.2f} kg",
        )

        prop_col4.metric(
            "Advanced Mission",
            "FEASIBLE" if advanced_propellant.feasible else "INFEASIBLE",
        )

        if advanced_propellant.feasible:
            st.success(
                "ADVANCED MISSION FEASIBLE — the spacecraft has enough "
                "propellant for the combined maneuver."
            )
        else:
            st.error(
                "ADVANCED MISSION INFEASIBLE — the combined maneuver "
                "exceeds available propellant."
            )

    else:
        st.warning(
            "Advanced propellant analysis requires available propellant "
            "to be less than initial spacecraft mass."
        )

    # -----------------------------------------------------------------------
    # Delta-v constraint analysis
    # -----------------------------------------------------------------------

    st.subheader("Mission Constraints")

    if available_propellant < spacecraft_mass:
        final_mass = spacecraft_mass - available_propellant

        available_delta_v = delta_v_from_mass_ratio(
            initial_mass=spacecraft_mass,
            final_mass=final_mass,
            specific_impulse=specific_impulse,
        )

        constraints = MissionConstraints(
            dry_mass=final_mass,
            propellant_mass=available_propellant,
            specific_impulse=specific_impulse,
            maximum_delta_v=available_delta_v,
        )

        feasibility = evaluate_delta_v_feasibility(
            required_delta_v=advanced_mission.combined_delta_v,
            available_delta_v=constraints.maximum_delta_v,
        )

        constraint_col1, constraint_col2, constraint_col3 = st.columns(3)

        constraint_col1.metric(
            "Available Delta-v",
            f"{feasibility.available_delta_v / 1_000:.3f} km/s",
        )

        constraint_col2.metric(
            "Required Delta-v",
            f"{feasibility.required_delta_v / 1_000:.3f} km/s",
        )

        constraint_col3.metric(
            "Delta-v Margin",
            f"{feasibility.delta_v_margin / 1_000:.3f} km/s",
        )

        if feasibility.feasible:
            st.success(
                "CONSTRAINT CHECK PASSED — available delta-v "
                "covers the mission requirement."
            )
        else:
            st.error(
                "CONSTRAINT CHECK FAILED — mission delta-v exceeds "
                "available spacecraft capability."
            )

    # -----------------------------------------------------------------------
    # Continuous Hohmann simulation
    # -----------------------------------------------------------------------

    st.subheader("Continuous Mission Simulation")

    st.caption(
        "Numerically propagated spacecraft trajectory with two "
        "instantaneous Hohmann burns."
    )

    mission_trajectory = simulate_continuous_hohmann(
        initial_radius=initial_radius,
        final_radius=final_radius,
        dt=10.0,
    )

    figure, axis = plt.subplots(figsize=(9, 9))

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

    # -----------------------------------------------------------------------
    # Transfer details
    # -----------------------------------------------------------------------

    st.subheader("Transfer Details")

    transfer_col1, transfer_col2, transfer_col3 = st.columns(3)

    transfer_col1.metric(
        "First Burn Delta-v",
        f"{transfer.first_burn_delta_v / 1_000:.3f} km/s",
    )

    transfer_col2.metric(
        "Second Burn Delta-v",
        f"{transfer.second_burn_delta_v / 1_000:.3f} km/s",
    )

    transfer_col3.metric(
        "Total Delta-v",
        f"{transfer.total_delta_v / 1_000:.3f} km/s",
    )

    st.divider()

    # -----------------------------------------------------------------------
    # Burn sequence
    # -----------------------------------------------------------------------

    st.subheader("Mission Burn Sequence")

    planned_burns = [
        MissionBurn(
            name=burn.name,
            time=burn.time,
            delta_v=burn.delta_v,
            direction=burn.direction,
        )
        for burn in mission_trajectory.burns
    ]

    burn_sequence = create_burn_sequence(
        planned_burns,
    )

    burn_sequence_col1, burn_sequence_col2 = st.columns(2)

    burn_sequence_col1.metric(
        "Burn Count",
        str(burn_sequence.burn_count),
    )

    burn_sequence_col2.metric(
        "Sequence Delta-v",
        f"{burn_sequence.total_delta_v / 1_000:.3f} km/s",
    )

    burn_rows = []

    for burn in burn_sequence.burns:
        burn_rows.append(
            {
                "Burn": burn.name,
                "Time (hr)": round(burn.time / 3600, 3),
                "Delta-v (km/s)": round(burn.delta_v / 1_000, 4),
                "Direction": burn.direction,
            }
        )

    burn_dataframe = pd.DataFrame(burn_rows)

    st.dataframe(
        burn_dataframe,
        width="stretch",
        hide_index=True,
    )

    # -----------------------------------------------------------------------
    # Numerical mission execution
    # -----------------------------------------------------------------------

    st.subheader("Real Mission Execution Engine")

    st.caption(
        "Executes the planned Hohmann transfer using ASTRA's "
        "3D finite-thrust RK4 mission engine."
    )

    execution_col1, execution_col2 = st.columns(2)

    with execution_col1:
        execution_thrust = st.number_input(
            "Engine thrust (N)",
            min_value=1.0,
            value=1_000.0,
            step=100.0,
        )

    with execution_col2:
        include_j2 = st.checkbox(
            "Include Earth J2 perturbation",
            value=True,
        )

    mass_flow_rate = (
        execution_thrust
        / (specific_impulse * 9.80665)
    )

    first_delta_v = transfer.delta_v1
    second_delta_v = transfer.delta_v2

    first_final_mass = spacecraft_mass * (
        2.718281828459045
        ** (
            -first_delta_v
            / (specific_impulse * 9.80665)
        )
    )

    final_execution_mass = first_final_mass * (
        2.718281828459045
        ** (
            -second_delta_v
            / (specific_impulse * 9.80665)
        )
    )

    required_execution_propellant = (
        spacecraft_mass - final_execution_mass
    )

    dry_mass = spacecraft_mass - available_propellant

    if dry_mass <= 0:
        dry_mass = spacecraft_mass * 0.1

    if required_execution_propellant > available_propellant:
        st.error(
            "MISSION EXECUTION BLOCKED ? the modeled Hohmann "
            "transfer requires more propellant than available."
        )
    else:
        first_burn_duration = (
            (spacecraft_mass - first_final_mass)
            / mass_flow_rate
        )

        second_burn_duration = (
            (first_final_mass - final_execution_mass)
            / mass_flow_rate
        )

        transfer_coast_duration = (
            transfer.transfer_time
            - first_burn_duration
        )

        if transfer_coast_duration <= 0:
            st.error(
                "MISSION EXECUTION BLOCKED ? finite-thrust "
                "burn duration is incompatible with the "
                "Hohmann transfer time."
            )
        else:
            first_burn = MissionEvent(
                name="Hohmann Perigee Burn",
                start_time=0.0,
                duration=first_burn_duration,
                event_type=MissionEventType.BURN,
            )

            transfer_coast = MissionEvent(
                name="Hohmann Transfer Coast",
                start_time=first_burn.end_time,
                duration=transfer_coast_duration,
                event_type=MissionEventType.COAST,
            )

            second_burn = MissionEvent(
                name="Hohmann Apogee Burn",
                start_time=transfer.transfer_time,
                duration=second_burn_duration,
                event_type=MissionEventType.BURN,
            )

            timeline = create_mission_timeline(
                [
                    first_burn,
                    transfer_coast,
                    second_burn,
                ]
            )

            execution_plan = create_mission_execution_plan(
                [
                    MissionExecutionEvent(
                        event=first_burn,
                        thrust_model=ThrustModel(
                            thrust=execution_thrust,
                            specific_impulse=specific_impulse,
                        ),
                        burn_direction=BurnVector(
                            0.0,
                            1.0,
                            0.0,
                        ),
                        dry_mass=dry_mass,
                    ),
                    MissionExecutionEvent(
                        event=transfer_coast,
                    ),
                    MissionExecutionEvent(
                        event=second_burn,
                        thrust_model=ThrustModel(
                            thrust=execution_thrust,
                            specific_impulse=specific_impulse,
                        ),
                        burn_direction=BurnVector(
                            0.0,
                            -1.0,
                            0.0,
                        ),
                        dry_mass=dry_mass,
                    ),
                ]
            )

            initial_execution_state = State3DThrust(
                x=initial_radius,
                y=0.0,
                z=0.0,
                vx=0.0,
                vy=circular_orbital_velocity(initial_radius),
                vz=0.0,
                mass=spacecraft_mass,
            )

            try:
                executed_mission = execute_mission(
                    initial_state=initial_execution_state,
                    plan=execution_plan,
                    timestep=10.0,
                    include_j2=include_j2,
                )

                execution_col1, execution_col2, execution_col3, execution_col4 = (
                    st.columns(4)
                )

                execution_col1.metric(
                    "Mission Events",
                    str(executed_mission.event_count),
                )

                execution_col2.metric(
                    "Burns Executed",
                    str(execution_plan.burn_count),
                )

                execution_col3.metric(
                    "Propellant Used",
                    f"{executed_mission.total_propellant_consumed:.2f} kg",
                )

                execution_col4.metric(
                    "Final Mass",
                    f"{executed_mission.final_mass:.2f} kg",
                )

                history = executed_mission.history

                execution_x = [
                    point.state.x / 1_000
                    for point in history.points
                ]

                execution_y = [
                    point.state.y / 1_000
                    for point in history.points
                ]

                execution_figure, execution_axis = plt.subplots(
                    figsize=(9, 9),
                )

                execution_axis.plot(
                    execution_x,
                    execution_y,
                    label="Finite-thrust executed trajectory",
                )

                execution_axis.add_patch(
                    plt.Circle(
                        (0, 0),
                        EARTH_RADIUS / 1_000,
                        fill=True,
                        alpha=0.35,
                        label="Earth",
                    )
                )

                for event in executed_mission.events:
                    if event.event_type == MissionEventType.BURN:
                        burn_points = [
                            point
                            for point in history.points
                            if event.start_time
                            <= point.time
                            <= event.end_time
                        ]

                        if burn_points:
                            burn_point = burn_points[0]

                            execution_axis.scatter(
                                burn_point.state.x / 1_000,
                                burn_point.state.y / 1_000,
                                s=90,
                                marker="*",
                                label=event.name,
                            )

                execution_axis.set_xlabel("X Position (km)")
                execution_axis.set_ylabel("Y Position (km)")
                execution_axis.set_title(
                    "ASTRA Finite-Thrust Mission Execution"
                )
                execution_axis.set_aspect("equal")
                execution_axis.legend()

                st.pyplot(
                    execution_figure,
                    clear_figure=True,
                )

                plt.close(execution_figure)

                st.subheader("Executed Mission Events")

                event_dataframe = pd.DataFrame(
                    [
                        {
                            "Event": event.name,
                            "Type": event.event_type.value,
                            "Start (s)": round(event.start_time, 2),
                            "End (s)": round(event.end_time, 2),
                            "Initial Mass (kg)": round(
                                event.initial_mass,
                                3,
                            ),
                            "Final Mass (kg)": round(
                                event.final_mass,
                                3,
                            ),
                            "Propellant Used (kg)": round(
                                event.propellant_consumed,
                                3,
                            ),
                        }
                        for event in executed_mission.events
                    ]
                )

                st.dataframe(
                    event_dataframe,
                    width="stretch",
                    hide_index=True,
                )

                st.success(
                    f"MISSION EXECUTION COMPLETE ? "
                    f"{timeline.event_count} timeline events executed "
                    f"through the "
                    f"{'J2 + central-gravity' if include_j2 else 'central-gravity'} "
                    f"3D dynamics model."
                )

            except ValueError as error:
                st.error(
                    f"MISSION EXECUTION FAILED ? {error}"
                )

    st.divider()

    # -----------------------------------------------------------------------
    # Transfer strategy optimization
    # -----------------------------------------------------------------------

    st.subheader("Transfer Strategy Optimization")

    st.caption(
        "Compares a baseline Hohmann transfer against bi-elliptic "
        "transfer candidates."
    )

    optimizer_col1, optimizer_col2 = st.columns(2)

    with optimizer_col1:
        minimum_intermediate_altitude_km = st.number_input(
            "Minimum intermediate apoapsis (km)",
            min_value=1.0,
            value=max(
                final_altitude_km + 700.0,
                1500.0,
            ),
            step=500.0,
        )

    with optimizer_col2:
        maximum_intermediate_altitude_km = st.number_input(
            "Maximum intermediate apoapsis (km)",
            min_value=1.0,
            value=max(
                final_altitude_km + 4700.0,
                5500.0,
            ),
            step=500.0,
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

    optimization = st.session_state.get("optimization")
    optimization_error = st.session_state.get("optimization_error")

    if optimization_error:
        st.error(optimization_error)

    if optimization is not None:
        best = optimization.best_candidate

        st.success(
            "OPTIMIZATION COMPLETE — lowest-delta-v feasible "
            "strategy identified."
        )

        result_col1, result_col2, result_col3 = st.columns(3)

        result_col1.metric(
            "Best Strategy",
            best.strategy,
        )

        result_col2.metric(
            "Optimized Delta-v",
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
                "Hohmann remains the lowest-delta-v strategy "
                "for this mission."
            )
        else:
            st.success(
                f"{best.strategy} improves on the Hohmann "
                "baseline for this mission."
            )

        savings_col1, savings_col2, savings_col3 = st.columns(3)

        savings_col1.metric(
            "Delta-v Savings vs Hohmann",
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
                    "Intermediate Apoapsis (km)": intermediate_text,
                    "Delta-v (km/s)": round(
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
            candidate_rows,
        )

        st.dataframe(
            candidate_dataframe,
            width="stretch",
            hide_index=True,
        )

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

            optimization_figure, optimization_axis = plt.subplots(
                figsize=(10, 6),
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
                "Total Delta-v (km/s)"
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

            plt.close(optimization_figure)

    st.divider()

    # -----------------------------------------------------------------------
    # Initial orbit analysis
    # -----------------------------------------------------------------------

    st.subheader("Initial Orbit Analysis")

    initial_velocity = circular_orbital_velocity(
        initial_radius,
    )

    initial_period = orbital_period(
        initial_radius,
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
        dt=10.0,
    )

    analysis = analyze_trajectory(
        trajectory,
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

    stability_figure, stability_axes = plt.subplots(
        3,
        1,
        figsize=(10, 10),
    )

    stability_axes[0].plot(
        times,
        altitude_deviation_m,
    )

    stability_axes[0].axhline(
        0,
        linestyle="--",
        linewidth=1,
    )

    stability_axes[0].set_xlabel("Time (s)")
    stability_axes[0].set_ylabel("Altitude Error (m)")
    stability_axes[0].set_title(
        "Altitude Deviation from Circular-Orbit Baseline"
    )

    stability_axes[1].plot(
        times,
        speed_deviation_m_s,
    )

    stability_axes[1].axhline(
        0,
        linestyle="--",
        linewidth=1,
    )

    stability_axes[1].set_xlabel("Time (s)")
    stability_axes[1].set_ylabel("Velocity Error (m/s)")
    stability_axes[1].set_title(
        "Velocity Deviation from Circular-Orbit Baseline"
    )

    stability_axes[2].plot(
        times,
        energy_deviation_j_kg,
    )

    stability_axes[2].axhline(
        0,
        linestyle="--",
        linewidth=1,
    )

    stability_axes[2].set_xlabel("Time (s)")
    stability_axes[2].set_ylabel("Energy Error (J/kg)")
    stability_axes[2].set_title(
        "Specific Orbital Energy Drift"
    )

    stability_figure.tight_layout()

    st.pyplot(
        stability_figure,
        clear_figure=True,
    )

    plt.close(stability_figure)

    # -----------------------------------------------------------------------
    # Numerical stability
    # -----------------------------------------------------------------------

    st.subheader("Numerical Stability")

    st.caption(
        "These values quantify numerical integration error during "
        "one simulated circular orbit."
    )

    if (
        max_altitude_error_m < 1.0
        and max_speed_error_m_s < 0.01
    ):
        st.success(
            "NUMERICAL VALIDATION PASSED — the propagated circular "
            "orbit remains within the selected engineering tolerance."
        )
    else:
        st.warning(
            "NUMERICAL VALIDATION WARNING — the propagation error "
            "is larger than the expected tolerance."
        )

    stability_col1, stability_col2, stability_col3 = st.columns(3)

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

    # -----------------------------------------------------------------------
    # Initial orbit properties
    # -----------------------------------------------------------------------

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
