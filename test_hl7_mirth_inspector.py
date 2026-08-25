import pytest
from hl7_mirth_inspector import MessageHierarchyValidatorAgent, OBXResultAuditorAgent, HIPAASafeHarborSanitizerAgent, HL7InterfaceCoordinator, main


def test_sub_agents():
    a1 = MessageHierarchyValidatorAgent()
    alerts1 = a1.evaluate({"metric_primary": 35.0})
    assert len(alerts1) == 1

    a2 = OBXResultAuditorAgent()
    alerts2 = a2.evaluate({"critical_flag": True})
    assert len(alerts2) == 1

    a3 = HIPAASafeHarborSanitizerAgent()
    alerts3 = a3.evaluate({"status_text": "DISCORDANT_FINDING"})
    assert len(alerts3) == 1


def test_coordinator():
    coord = HL7InterfaceCoordinator()
    dossier = coord.audit_case({"case_id": "TEST-100", "metric_primary": 10.0, "metric_secondary": 2.0})
    assert dossier["overall_status"] == "CONCORDANT_NORMAL"
    assert dossier["total_alerts"] == 0

    ans = coord.query_assistant("What are the guidelines?")
    assert "guidelines" in ans or "standards" in ans


def test_cli():
    assert main(["audit", "--case-id", "CLI-01"]) == 0
    assert main(["chat", "What", "is", "the", "system", "status?"]) == 0


def test_domain_registry():
    from hl7_mirth_inspector import DomainKnowledgeRegistry
    assert DomainKnowledgeRegistry.ZERO_PHI_COMPLIANCE is True
    assert "PRO" in DomainKnowledgeRegistry.SYSTEM_VERSION
