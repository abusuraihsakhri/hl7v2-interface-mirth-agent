import pytest
from simulator import run_simulation


def test_simulator_rejects_zero_and_negative_iterations():
    with pytest.raises(ValueError, match="positive"):
        run_simulation(0)
    with pytest.raises(ValueError, match="positive"):
        run_simulation(-2)


def test_simulator_single_case(capsys):
    run_simulation(1)
    result = capsys.readouterr().out
    assert "Total Tasks Processed:     1" in result
    assert "100% Interception Rate" not in result
