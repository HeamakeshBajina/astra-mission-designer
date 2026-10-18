import json
import pytest
from astra.mission.scenario_comparison import MissionScenario, compare_mission_scenarios

S = [MissionScenario("A", 400, 800), MissionScenario("B", 400, 2000),
     MissionScenario("C", 300, 500)]

def run(**kw):
    args = dict(scenarios=S, max_delta_v_m_s=5000,
                max_transfer_time_s=100000, objective="lowest_delta_v")
    args.update(kw)
    return compare_mission_scenarios(**args)

def test_ranks_all_scenarios():
    r = run()
    assert len(r.results) == 3
    assert [x.rank for x in r.results] == [1, 2, 3]

def test_delta_v_ranking():
    v = [x.total_delta_v_m_s for x in run().results]
    assert v == sorted(v)

def test_time_ranking():
    v = [x.transfer_time_s for x in run(objective="shortest_time").results]
    assert v == sorted(v)

def test_feasible_first():
    scenarios = [
        MissionScenario("small raise", 300, 500),
        MissionScenario("large raise", 400, 2000),
    ]
    r = run(
        scenarios=scenarios,
        max_delta_v_m_s=400,
        max_transfer_time_s=100000,
    )
    v = [x.feasible for x in r.results]
    assert any(v) and not all(v)
    assert v == sorted(v, reverse=True)

def test_equal_altitudes_rejected():
    with pytest.raises(ValueError):
        run(scenarios=[MissionScenario("same", 400, 400)])

def test_empty_rejected():
    with pytest.raises(ValueError):
        run(scenarios=[])

@pytest.mark.parametrize("v", [0, -1, float("nan"), float("inf")])
def test_bad_limit_rejected(v):
    with pytest.raises(ValueError):
        run(max_delta_v_m_s=v)

def test_duplicate_names_rejected():
    with pytest.raises(ValueError):
        run(scenarios=[MissionScenario("x", 400, 800), MissionScenario("x", 300, 500)])

def test_bad_objective_rejected():
    with pytest.raises(ValueError):
        run(objective="invalid")

def test_json_export():
    r = run().to_dict()
    assert json.loads(json.dumps(r))["scenario_count"] == 3
    assert r["limitations"]
