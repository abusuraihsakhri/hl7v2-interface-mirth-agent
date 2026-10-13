import csv
from hl7v2_interface_mirth_agent.cli import parse_csv_bool, main
import pytest


@pytest.mark.parametrize("raw,expected", [
    ("true", True), ("TRUE", True), ("1", True),
    ("yes", True), ("False", False), ("false", False),
    ("0", False), ("no", False), ("", False), (False, False),
])
def test_parse_csv_bool(raw, expected):
    assert parse_csv_bool(raw) is expected


def test_parse_csv_bool_rejects_ambiguous_value():
    with pytest.raises(ValueError):
        parse_csv_bool("perhaps")


def test_batch_false_flag_does_not_generate_stat_alert(tmp_path):
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "result.csv"
    input_path.write_text(
        "case_id,primary_metric,secondary_metric,status_flag,is_stat\n"
        "CASE1,1,1,NORMAL,False\n"
        "CASE2,1,1,NORMAL,True\n",
        encoding="utf-8",
    )
    assert main(["batch", "-i", str(input_path), "-o", str(output_path)]) == 0
    with output_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["stat_critical_alerts"] == "0"
    assert rows[1]["stat_critical_alerts"] == "1"
