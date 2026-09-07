"""Tests for multi-burn mission sequencing."""

import pytest

from astra.mission.burn_sequence import (
    MissionBurn,
    create_burn_sequence,
)


def test_single_burn_sequence():
    burn = MissionBurn(
        name="Injection burn",
        time=0,
        delta_v=500,
        direction="prograde",
    )

    sequence = create_burn_sequence([burn])

    assert sequence.burn_count == 1
    assert sequence.total_delta_v == pytest.approx(500)


def test_multiple_burns_are_ordered():
    burns = [
        MissionBurn(
            name="Burn 1",
            time=0,
            delta_v=500,
            direction="prograde",
        ),
        MissionBurn(
            name="Burn 2",
            time=1000,
            delta_v=200,
            direction="retrograde",
        ),
        MissionBurn(
            name="Burn 3",
            time=2000,
            delta_v=100,
            direction="prograde",
        ),
    ]

    sequence = create_burn_sequence(burns)

    assert sequence.burn_count == 3
    assert sequence.total_delta_v == pytest.approx(800)


def test_empty_sequence_is_rejected():
    with pytest.raises(ValueError):
        create_burn_sequence([])


def test_negative_burn_time_is_rejected():
    burn = MissionBurn(
        name="Invalid burn",
        time=-1,
        delta_v=100,
        direction="prograde",
    )

    with pytest.raises(ValueError):
        create_burn_sequence([burn])


def test_negative_delta_v_is_rejected():
    burn = MissionBurn(
        name="Invalid burn",
        time=0,
        delta_v=-100,
        direction="prograde",
    )

    with pytest.raises(ValueError):
        create_burn_sequence([burn])


def test_burns_must_be_time_ordered():
    burns = [
        MissionBurn(
            name="Burn 1",
            time=1000,
            delta_v=500,
            direction="prograde",
        ),
        MissionBurn(
            name="Burn 2",
            time=500,
            delta_v=200,
            direction="retrograde",
        ),
    ]

    with pytest.raises(ValueError):
        create_burn_sequence(burns)


def test_empty_burn_name_is_rejected():
    burn = MissionBurn(
        name="",
        time=0,
        delta_v=100,
        direction="prograde",
    )

    with pytest.raises(ValueError):
        create_burn_sequence([burn])


def test_empty_burn_direction_is_rejected():
    burn = MissionBurn(
        name="Burn",
        time=0,
        delta_v=100,
        direction="",
    )

    with pytest.raises(ValueError):
        create_burn_sequence([burn])