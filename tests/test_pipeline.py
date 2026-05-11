from __future__ import annotations

import os
from typing import Any

from silver_substrate import ComponentInput, HardwareLevel, ThreatGenerationPipeline, load_env_file
from silver_substrate.models import PipelineRequest


class FakeAssessmentClient:
    def __init__(self) -> None:
        self.last_request: PipelineRequest | None = None

    def generate(self, request: PipelineRequest) -> dict[str, Any]:
        self.last_request = request
        return {
            "component_name": "bond pad",
            "level": "die_package_substrate_pins",
            "summary": "Bond pad assessment summary.",
            "deployment_assumptions": "The device is fielded without practical post-deployment hardware updates.",
            "threats": [
                {
                    "title": "Microprobe access",
                    "description": "Physical pad access can expose sensitive state after shipment.",
                    "sdlc_phase": "deployment_operation",
                    "sdlc_phase_description": "The attack occurs after field deployment but must be designed out earlier.",
                    "scenario": "An attacker exposes the package and probes the pad.",
                    "attack_surface": "Bond pad metallization",
                    "preconditions": ["Physical access"],
                    "potential_impact": "Signal disclosure or forced state changes.",
                    "deployment_consequence": "A shipped package cannot rely on later metal or package redesign.",
                    "priority": "critical",
                    "priority_score": 95,
                    "priority_rationale": "Debug authorization is a high-value asset and pad exposure cannot be fixed after shipment.",
                    "confidence": "medium",
                }
            ],
            "security_requirements": [
                {
                    "title": "Detect pad probing",
                    "description": "Design tamper detection around sensitive pad access paths before release.",
                    "sdlc_phase": "architecture_design",
                    "requirement": "Sensitive pads shall be covered by monitored tamper structures where feasible.",
                    "mitigates": ["Microprobe access"],
                    "verification_method": "Layout review and tamper response test.",
                    "owner": "Package security",
                    "design_robustness": "Tamper coverage is built into the package and does not depend on field updates.",
                    "priority": "critical",
                    "priority_score": 92,
                    "priority_rationale": "Package tamper coverage must be designed before package release.",
                }
            ],
            "prioritization_summary": "Microprobe access is ranked highest because the component protects debug authorization and cannot be updated after shipment.",
            "prioritized_actions": [
                {
                    "rank": 1,
                    "action_type": "security_requirement",
                    "title": "Detect pad probing",
                    "priority": "critical",
                    "priority_score": 92,
                    "rationale": "Build tamper coverage before package release to mitigate irreversible field exposure.",
                    "next_step": "Add package-security layout review and tamper response validation to the release checklist.",
                }
            ],
            "open_questions": ["Is the pad externally accessible after encapsulation?"],
        }


def test_build_request_includes_level_specific_prompt() -> None:
    client = FakeAssessmentClient()
    pipeline = ThreatGenerationPipeline(client=client)
    component = ComponentInput(
        name="gate oxide",
        level=HardwareLevel.OXIDES_DIELECTRICS_ISOLATION,
        priority_drivers=("protects root key material", "no field update path"),
    )

    request = pipeline.build_request(component)

    assert request.response_schema["properties"]["threats"]["type"] == "array"
    assert "sdlc_phase" in request.response_schema["properties"]["threats"]["items"]["required"]
    assert "deployment_consequence" in request.response_schema["properties"]["threats"]["items"]["required"]
    assert "priority_score" in request.response_schema["properties"]["threats"]["items"]["required"]
    assert "Oxides, Dielectrics, Isolation Structures" in request.messages[1]["content"]
    assert "sdlc_phases" in request.messages[1]["content"]
    assert "prioritization_method" in request.messages[1]["content"]
    assert "protects root key material" in request.messages[1]["content"]
    assert "gate oxide" in request.messages[1]["content"]


def test_run_normalizes_assessment() -> None:
    client = FakeAssessmentClient()
    pipeline = ThreatGenerationPipeline(client=client)
    component = ComponentInput(name="bond pad", level=HardwareLevel.DIE_PACKAGE_SUBSTRATE_PINS)

    assessment = pipeline.run(component)

    assert assessment.component_name == "bond pad"
    assert assessment.level is HardwareLevel.DIE_PACKAGE_SUBSTRATE_PINS
    assert assessment.deployment_assumptions.startswith("The device is fielded")
    assert assessment.prioritization_summary.startswith("Microprobe access")
    assert assessment.threats[0].title == "Microprobe access"
    assert assessment.threats[0].sdlc_phase.value == "deployment_operation"
    assert assessment.threats[0].priority_score == 95
    assert assessment.security_requirements[0].sdlc_phase.value == "architecture_design"
    assert assessment.security_requirements[0].mitigates == ("Microprobe access",)
    assert assessment.security_requirements[0].priority == "critical"
    assert assessment.prioritized_actions[0].rank == 1
    assert client.last_request is not None


def test_assessment_schema_is_self_describing_for_json_consumers() -> None:
    client = FakeAssessmentClient()
    pipeline = ThreatGenerationPipeline(client=client)
    component = ComponentInput(name="via stack", level=HardwareLevel.CONTACTS_VIAS_INTERCONNECTS)

    schema = pipeline.build_request(component).response_schema

    assert "description" in schema
    assert "description" in schema["properties"]["deployment_assumptions"]
    assert "description" in schema["properties"]["threats"]["items"]["properties"]["sdlc_phase"]
    assert "description" in schema["properties"]["security_requirements"]["items"]["properties"]["design_robustness"]
    assert "description" in schema["properties"]["prioritized_actions"]
    assert "prioritized_actions" in schema["required"]


def test_load_env_file_preserves_existing_environment(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OPENAI_API_KEY=sk-from-file\n"
        "OPENAI_MODEL=from-file-model\n"
        "QUOTED_VALUE=\"quoted secret\"\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("OPENAI_MODEL", "existing-model")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("QUOTED_VALUE", raising=False)

    load_env_file(env_file)

    assert os.environ["OPENAI_API_KEY"] == "sk-from-file"
    assert os.environ["OPENAI_MODEL"] == "existing-model"
    assert os.environ["QUOTED_VALUE"] == "quoted secret"
