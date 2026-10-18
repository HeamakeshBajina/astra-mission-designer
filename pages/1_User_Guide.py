"""ASTRA Mission Designer user guide."""

import streamlit as st

st.title("ASTRA User Guide")
st.write(
    "A step-by-step guide to planning, analysing, and understanding "
    "spacecraft orbital transfers with ASTRA."
)

st.info(
    "New here? Start with Section 1, configure the default mission, "
    "and work through the dashboard from top to bottom."
)

st.header("1. What is ASTRA?")

st.write(
    "ASTRA is an educational aerospace mission-analysis platform. "
    "It combines analytical orbital mechanics, numerical trajectory "
    "simulation, propellant feasibility checks, mission execution, "
    "and transfer-strategy optimization."
)

st.warning(
    "ASTRA is a research and learning tool, not flight-qualified "
    "software. Its models use assumptions and simplifications. "
    "Always validate results independently before using them for "
    "real spacecraft operations."
)

st.header("2. Your first mission")

st.write(
    "The mission dashboard uses the sidebar for the main spacecraft "
    "and orbit inputs. Start with the defaults, which describe a "
    "transfer from a 400 km orbit to an 800 km orbit."
)

with st.expander("Step 1 — Set the mission parameters", expanded=True):
    st.markdown(
        """
        - **Mission name:** A label to identify the scenario.
        - **Initial altitude (km):** Starting orbital altitude above
          Earth's reference radius.
        - **Target altitude (km):** Desired final orbital altitude.
        - **Spacecraft initial mass (kg):** Total initial spacecraft
          mass, including propellant.
        - **Specific impulse (s):** A measure of propulsion efficiency.
          Higher values generally mean less propellant for a given
          ideal delta-v.
        - **Available propellant (kg):** Fuel mass available for
          manoeuvres; it must be consistent with the initial mass.
        - **Inclination change (deg):** Requested orbital plane change
          used in advanced mission analysis.
        """
    )

with st.expander("Step 2 — Use sensible inputs"):
    st.markdown(
        """
        1. Keep the default values for your first run.
        2. Change one input at a time so you can understand its effect.
        3. Use non-negative orbital altitudes and positive spacecraft
           mass and specific impulse.
        4. Keep available propellant below initial spacecraft mass.
        5. If a mission is marked infeasible, inspect the required
           propellant and delta-v before changing parameters.
        """
    )

with st.expander("Step 3 — Read the mission summary"):
    st.markdown(
        """
        - **Required delta-v:** Ideal velocity change required by the
          mission model. Delta-v is a measure of manoeuvre demand,
          not the spacecraft's current speed.
        - **Fuel required:** Propellant estimated by the mission plan.
        - **Fuel remaining:** Estimated available propellant after the
          planned requirement.
        - **Transfer time:** Modelled time for the orbital transfer.
        - **Feasible / infeasible:** Indicates whether the relevant
          model's propellant or delta-v constraint is satisfied.
        """
    )

st.header("3. Understand the main analysis sections")

with st.expander("Advanced Mission Analysis"):
    st.write(
        "Compares the Hohmann transfer delta-v with an analytical "
        "inclination-change manoeuvre. A plane change can require "
        "substantial additional delta-v, depending on orbital speed "
        "and the requested angle."
    )

with st.expander("Propellant Feasibility and Mission Constraints"):
    st.write(
        "These sections compare modelled manoeuvre requirements with "
        "spacecraft capability. Check the stated assumptions and units "
        "before interpreting a feasible or infeasible result."
    )

with st.expander("Continuous Mission Simulation"):
    st.write(
        "Displays a numerically propagated Hohmann-transfer trajectory "
        "with two idealized instantaneous burns. The plot shows the "
        "modelled path around Earth; it is not a real-time spacecraft "
        "tracking display."
    )

with st.expander("Transfer Details and Mission Burn Sequence"):
    st.markdown(
        """
        - **First burn delta-v:** Ideal velocity change for the first
          transfer manoeuvre.
        - **Second burn delta-v:** Ideal velocity change for the
          second transfer manoeuvre.
        - **Total delta-v:** Sum of the ideal transfer burn magnitudes.
        - **Burn sequence:** Lists planned burn times, magnitudes,
          and directions.
        """
    )

with st.expander("Real Mission Execution Engine"):
    st.write(
        "Models finite-thrust burns using the selected engine thrust "
        "and specific impulse. The optional J2 setting adds Earth's "
        "oblateness perturbation to the supported dynamics model. "
        "Finite-thrust execution is not identical to an ideal "
        "instantaneous-burn Hohmann transfer."
    )

with st.expander("Transfer Strategy Optimization"):
    st.write(
        "Compares a Hohmann baseline with sampled bi-elliptic transfer "
        "candidates. The search range and resolution affect which "
        "candidates are evaluated. The best result is the best among "
        "the candidates evaluated, not necessarily a global optimum."
    )

with st.expander("Initial Orbit Analysis and Numerical Stability"):
    st.write(
        "Examines a propagated circular orbit, including altitude, "
        "speed, and specific orbital energy deviations. These checks "
        "help assess numerical behaviour for the selected simulation "
        "and tolerances; they do not validate every model in ASTRA."
    )

st.header("4. A recommended first workflow")

st.markdown(
    """
    1. Open **Mission Dashboard** from the page navigation.
    2. Keep the default 400 km to 800 km transfer.
    3. Review the mission summary and feasibility status.
    4. Compare the two burn values with the total delta-v.
    5. Inspect the trajectory and burn sequence.
    6. Review the execution model and numerical-stability results.
    7. Run transfer optimization and compare its result with the
       Hohmann baseline.
    8. Change one parameter and observe which outputs change.
    """
)

st.header("5. Troubleshooting")

with st.expander("Why is my mission infeasible?"):
    st.write(
        "The model may require more propellant or delta-v than the "
        "spacecraft configuration allows. Check initial mass, "
        "available propellant, specific impulse, and target altitude."
    )

with st.expander("Why do different sections show different results?"):
    st.write(
        "Some sections use analytical ideal-burn calculations, while "
        "others use numerical propagation or finite-thrust execution. "
        "Their assumptions differ, so outputs need not match exactly."
    )

with st.expander("Why did optimization fail?"):
    st.write(
        "Check that the intermediate-apoapsis search range is valid "
        "and that its maximum exceeds its minimum. A coarse search "
        "can skip useful candidates; a wider or finer search may take "
        "longer."
    )

with st.expander("What should I do if an error appears?"):
    st.write(
        "Record the section name, input values, and full error message. "
        "Avoid treating a missing result as a valid zero. Report the "
        "problem so the underlying calculation or interface can be "
        "investigated."
    )

st.divider()
st.caption(
    "ASTRA Mission Designer | User Guide | "
    "Educational aerospace mission analysis"
)

st.divider()

st.header("6. Mission Constraint Analysis")

st.markdown(
    """
    Mission Constraint Analysis independently checks an ideal
    Earth Hohmann transfer against two limits you choose. It supplements
    the main mission planner; it does not replace its propellant,
    advanced-mission, or finite-thrust calculations.

    ### Configure the limits

    Open **Mission Constraint Analysis** below the main dashboard and
    set the following limits:

    - **Maximum transfer delta-v (km/s):** the maximum allowed sum of
      the two ideal Hohmann burn magnitudes.
    - **Maximum transfer time (hours):** the longest permitted
      analytical transfer duration.

    The starting and target altitudes come from the main Mission
    Parameters sidebar. Select different altitudes to evaluate a transfer.

    ### Read the results

    - **Analytical delta-v:** the sum of the two ideal transfer burns.
    - **Transfer duration:** half the period of the transfer ellipse.
    - **Constraints passed:** the number of checks that passed.
    - **Constraint results:** each check's status, calculated value,
      allowed limit, and explanation.
    - **Both constraints pass:** the selected analytical transfer meets
      both configured limits. A failed check means that its limit is
      exceeded.

    The limits are inclusive: a calculated value equal to its limit
    passes the check.

    ### Export a report

    Select **Download constraint report (JSON)** to export the mission
    name, altitudes, configured limits, calculated results, individual
    checks, and stated model limitations. JSON is useful for inspection,
    reproducibility, and further analysis with other tools.

    ### Model assumptions and limitations

    This check models an ideal circular-to-circular Hohmann transfer
    under a two-body Earth gravity assumption. It does not include
    atmospheric drag, launch injection errors, orbital plane changes,
    finite-duration burns, third-body perturbations, or operational
    reserve policies.

    A passing result means only that the two configured analytical
    constraints are satisfied. It does not establish complete spacecraft
    feasibility or flight readiness. Other ASTRA sections may produce
    different results because they use different models and assumptions.
    """
)

st.info(
    "Tip: change one input at a time and compare the calculated delta-v "
    "and transfer duration. Keep units consistent when comparing results."
)


st.header("7. Mission Scenario Comparison")
st.markdown("""
Compare multiple ideal circular-to-circular Earth Hohmann transfers against
shared delta-v and transfer-time limits.

### Inputs and units
Choose the ranking objective, limits, and two to five scenarios. Altitudes are
kilometres above Earth's surface, delta-v limits are km/s, and transfer-time
limits are hours. Scenario names must be unique; initial and target altitudes
must differ.

### Ranking and export
Feasible scenarios rank before infeasible scenarios. Within each group, the
selected objective is used, with delta-v, transfer time, and name as tie-breakers.
The table reports each constraint check and overall feasibility. Download the
JSON report to retain inputs, outputs, ranking objective, constraints, and
limitations.

### Limitations
This analytical model assumes ideal two-body circular Earth orbits and a
Hohmann transfer. It excludes atmospheric drag, injection errors, plane changes,
finite-duration burns, third-body perturbations, and operational reserves.
A feasible result does not establish flight readiness.
""")

st.header("8. Mission Altitude Sensitivity & Trade-off Analysis")
st.markdown("""
This tool holds the initial orbit altitude fixed and evaluates a uniformly
spaced range of target altitudes. Each sample is passed to ASTRA's shared
mission validator.

### Inputs and units
- Initial altitude and target-altitude range are in kilometres above Earth's
  surface.
- Sample count is an integer from 2 to 500; both range endpoints are included.
- Delta-v budget is entered in km/s; transfer-time limit is entered in hours.
- The maximum target altitude must exceed the minimum.
- A sampled target altitude cannot equal the initial altitude, because the
  underlying transfer validator requires distinct initial and target altitudes.

### Outputs
- Delta-v versus target altitude and transfer time versus target altitude.
- A trade-off scatter plot of transfer time against delta-v.
- A table with individual constraint results and overall feasibility.
- A feasible-candidate count and downloadable JSON report containing inputs,
  sample results, and model limitations.

This is a parameter sweep, not an optimizer. It evaluates only the specified
sample locations; a target altitude between samples may produce different
results. A candidate marked feasible passes both configured analytical limits.

### Model assumptions and limitations
The calculations use an ideal circular-to-circular Earth Hohmann transfer under
two-body gravity. Atmospheric drag, launch injection errors, orbital plane
changes, finite-duration burns, third-body perturbations, and operational
reserves are excluded. Passing the two checks does not establish complete
spacecraft feasibility or flight readiness.
""")
