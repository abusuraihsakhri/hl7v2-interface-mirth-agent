"""
Automated Pytest for hl7v2_interface_mirth_agent core package.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from hl7v2_interface_mirth_agent.models import (
    ClinicalCasePayload,
    AgentAlert,
    UrgencyLevel,
    ClinicalIntegrityStatus,
)
from hl7v2_interface_mirth_agent.engine import ClinicalDomainEngine
from hl7v2_interface_mirth_agent.agents import (
    MessageHierarchyValidatorAgent,
    OBXResultAuditorAgent,
    HIPAASafeHarborSanitizerAgent,
    HL7InterfaceCoordinator,
)
from hl7v2_interface_mirth_agent.cli import main


def test_clinical_case_payload_creation():
    case = ClinicalCasePayload(
        case_id="CASE-001",
        patient_synthetic_id="SYNTH-01",
        primary_metric=15.0,
        secondary_metric=5.0,
        status_flag="NORMAL",
    )
    assert case.case_id == "CASE-001"
    assert case.is_stat is False
    assert case.timestamp != ""


def test_clinical_domain_engine_primary():
    # Below threshold
    assert ClinicalDomainEngine.evaluate_primary_index(10.0) is None
    # Above threshold
    result = ClinicalDomainEngine.evaluate_primary_index(25.0)
    assert result is not None
    assert "exceeds" in result["finding"].lower()


def test_clinical_domain_engine_secondary():
    # Below threshold, not stat
    assert ClinicalDomainEngine.evaluate_secondary_kinetics(5.0, False) is None
    # Above threshold
    result = ClinicalDomainEngine.evaluate_secondary_kinetics(15.0, False)
    assert result is not None
    # STAT flag
    result_stat = ClinicalDomainEngine.evaluate_secondary_kinetics(5.0, True)
    assert result_stat is not None


def test_clinical_domain_engine_biomarker():
    # Normal status
    assert ClinicalDomainEngine.evaluate_biomarker_concordance("NORMAL", {}) is None
    # Discordant
    result = ClinicalDomainEngine.evaluate_biomarker_concordance("DISCORDANT", {})
    assert result is not None
    assert "discordance" in result["finding"].lower() or "divergence" in result["finding"].lower()


def test_sub_agents():
    case_high_primary = ClinicalCasePayload(
        case_id="CASE-HI", patient_synthetic_id="SYNTH-01",
        primary_metric=35.0, secondary_metric=5.0, status_flag="NORMAL",
    )
    alerts = MessageHierarchyValidatorAgent().audit(case_high_primary)
    assert len(alerts) == 1
    assert alerts[0].urgency == UrgencyLevel.WARNING

    case_stat = ClinicalCasePayload(
        case_id="CASE-STAT", patient_synthetic_id="SYNTH-01",
        primary_metric=10.0, secondary_metric=5.0, status_flag="NORMAL", is_stat=True,
    )
    alerts = OBXResultAuditorAgent().audit(case_stat)
    assert len(alerts) == 1
    assert alerts[0].urgency == UrgencyLevel.STAT_CRITICAL

    case_discordant = ClinicalCasePayload(
        case_id="CASE-DISC", patient_synthetic_id="SYNTH-01",
        primary_metric=10.0, secondary_metric=5.0, status_flag="DISCORDANT",
    )
    alerts = HIPAASafeHarborSanitizerAgent().audit(case_discordant)
    assert len(alerts) == 1
    assert alerts[0].urgency == UrgencyLevel.ADVISORY


def test_coordinator_normal():
    coord = HL7InterfaceCoordinator()
    case = ClinicalCasePayload(
        case_id="CASE-NORMAL", patient_synthetic_id="SYNTH-01",
        primary_metric=10.0, secondary_metric=5.0, status_flag="NORMAL",
    )
    dossier = coord.process_case(case)
    assert dossier["overall_status"] == ClinicalIntegrityStatus.CONCORDANT_NORMAL.value
    assert dossier["total_alerts"] == 0


def test_coordinator_critical():
    coord = HL7InterfaceCoordinator()
    case = ClinicalCasePayload(
        case_id="CASE-CRIT", patient_synthetic_id="SYNTH-01",
        primary_metric=35.0, secondary_metric=15.0, status_flag="DISCORDANT", is_stat=True,
    )
    dossier = coord.process_case(case)
    assert dossier["overall_status"] == ClinicalIntegrityStatus.CRITICAL_ACTION_REQUIRED.value
    assert dossier["stat_critical_alerts"] > 0


def test_coordinator_chat():
    coord = HL7InterfaceCoordinator()
    ans = coord.query_supervisory_chat("What is the status?")
    assert "tracking" in ans.lower()
    ans = coord.query_supervisory_chat("Tell me about guidelines")
    assert "guideline" in ans.lower() or "standard" in ans.lower() or "protocol" in ans.lower()


def test_cli_audit():
    assert main(["audit", "--case-id", "CLI-PKG-01"]) == 0


def test_cli_chat():
    assert main(["chat", "What", "is", "the", "status?"]) == 0
