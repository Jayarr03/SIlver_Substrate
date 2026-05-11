"""JSON schema used for structured model output."""

from __future__ import annotations

from typing import Any

HARDWARE_LEVEL_VALUES = [
    "architecture_rtl_gates",
    "transistors",
    "terminals_channel_body",
    "doped_regions_wells_junctions",
    "oxides_dielectrics_isolation",
    "contacts_vias_interconnects",
    "passivation_protective_layers",
    "die_package_substrate_pins",
    "wafer_process_chemistry",
]

SDLC_PHASE_VALUES = [
    "requirements",
    "architecture_design",
    "implementation",
    "verification_validation",
    "manufacturing_supply_chain",
    "deployment_operation",
    "end_of_life",
]

PRIORITY_VALUES = ["low", "medium", "high", "critical"]

ASSESSMENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "description": "Structured silicon-layer threat assessment grouped by SDLC phase and prioritized for the supplied component, with durable controls for devices that may not be updateable after deployment.",
    "properties": {
        "component_name": {"type": "string", "description": "Name of the assessed component."},
        "level": {
            "type": "string",
            "description": "Hardware abstraction level for the component.",
            "enum": HARDWARE_LEVEL_VALUES,
        },
        "summary": {
            "type": "string",
            "description": "Brief assessment summary focused on the selected hardware layer.",
        },
        "deployment_assumptions": {
            "type": "string",
            "description": "Assumptions about post-deployment immutability, physical access, lifetime, and update limitations.",
        },
        "prioritization_summary": {
            "type": "string",
            "description": "Summary of the component-specific prioritization drivers and scoring rationale used for this assessment.",
        },
        "threats": {
            "type": "array",
            "description": "Threats categorized by SDLC phase and prioritized for the supplied component.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string", "description": "Short threat title."},
                    "description": {
                        "type": "string",
                        "description": "Plain-language description of the threat and why it matters for this component.",
                    },
                    "sdlc_phase": {
                        "type": "string",
                        "description": "SDLC phase where this threat is introduced, discovered, or must be mitigated.",
                        "enum": SDLC_PHASE_VALUES,
                    },
                    "sdlc_phase_description": {
                        "type": "string",
                        "description": "Explanation of why the threat belongs in the selected SDLC phase.",
                    },
                    "scenario": {"type": "string", "description": "Concrete attacker or failure scenario."},
                    "attack_surface": {"type": "string", "description": "Physical, electrical, process, or lifecycle attack surface."},
                    "preconditions": {
                        "type": "array",
                        "description": "Conditions required for the scenario to be feasible.",
                        "items": {"type": "string"},
                    },
                    "potential_impact": {"type": "string", "description": "Security, safety, reliability, or business impact."},
                    "deployment_consequence": {
                        "type": "string",
                        "description": "Why this threat is harder to remediate after device release or field deployment.",
                    },
                    "priority": {
                        "type": "string",
                        "description": "Component-specific threat priority derived from impact, exposure, exploitability, design lock-in, and remediation difficulty.",
                        "enum": PRIORITY_VALUES,
                    },
                    "priority_score": {
                        "type": "integer",
                        "description": "Component-specific priority score from 1 to 100, where 100 is the most urgent to address.",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "priority_rationale": {
                        "type": "string",
                        "description": "Explanation of why this priority applies to the supplied component and its lifecycle context.",
                    },
                    "confidence": {
                        "type": "string",
                        "description": "Confidence in the threat based on provided context.",
                        "enum": ["low", "medium", "high"],
                    },
                },
                "required": [
                    "title",
                    "description",
                    "sdlc_phase",
                    "sdlc_phase_description",
                    "scenario",
                    "attack_surface",
                    "preconditions",
                    "potential_impact",
                    "deployment_consequence",
                    "priority",
                    "priority_score",
                    "priority_rationale",
                    "confidence",
                ],
            },
        },
        "security_requirements": {
            "type": "array",
            "description": "Robust-by-design requirements and verification activities linked to generated threats, prioritized for the supplied component.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string", "description": "Short requirement title."},
                    "description": {
                        "type": "string",
                        "description": "Plain-language description of the mitigation intent.",
                    },
                    "sdlc_phase": {
                        "type": "string",
                        "description": "Earliest SDLC phase where the requirement should be specified or verified.",
                        "enum": SDLC_PHASE_VALUES,
                    },
                    "requirement": {
                        "type": "string",
                        "description": "Specific, testable security requirement using shall/should language.",
                    },
                    "mitigates": {
                        "type": "array",
                        "description": "Threat titles mitigated by this requirement.",
                        "items": {"type": "string"},
                    },
                    "verification_method": {
                        "type": "string",
                        "description": "How the design or process should be verified before deployment.",
                    },
                    "owner": {"type": "string", "description": "Team or role accountable for implementation and evidence."},
                    "design_robustness": {
                        "type": "string",
                        "description": "How this mitigation remains effective when the deployed device cannot be patched or updated.",
                    },
                    "priority": {
                        "type": "string",
                        "description": "Component-specific implementation priority for this requirement.",
                        "enum": PRIORITY_VALUES,
                    },
                    "priority_score": {
                        "type": "integer",
                        "description": "Component-specific requirement priority score from 1 to 100, where 100 should be implemented first.",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "priority_rationale": {
                        "type": "string",
                        "description": "Explanation of why this requirement should be implemented at the assigned priority for this component.",
                    },
                },
                "required": [
                    "title",
                    "description",
                    "sdlc_phase",
                    "requirement",
                    "mitigates",
                    "verification_method",
                    "owner",
                    "design_robustness",
                    "priority",
                    "priority_score",
                    "priority_rationale",
                ],
            },
        },
        "prioritized_actions": {
            "type": "array",
            "description": "Ranked action list that combines the highest-priority threats and requirements for the supplied component.",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "rank": {
                        "type": "integer",
                        "description": "Ordered rank beginning at 1; lower ranks should be addressed first.",
                        "minimum": 1,
                    },
                    "action_type": {
                        "type": "string",
                        "description": "Whether the action is primarily about a threat to analyze or a requirement to implement.",
                        "enum": ["threat", "security_requirement"],
                    },
                    "title": {"type": "string", "description": "Threat or requirement title referenced by this action."},
                    "priority": {
                        "type": "string",
                        "description": "Priority label for this ranked action.",
                        "enum": PRIORITY_VALUES,
                    },
                    "priority_score": {
                        "type": "integer",
                        "description": "Priority score from 1 to 100 used to order this action.",
                        "minimum": 1,
                        "maximum": 100,
                    },
                    "rationale": {"type": "string", "description": "Why this action is ranked here for this component."},
                    "next_step": {"type": "string", "description": "Concrete next engineering, verification, or supply-chain step."},
                },
                "required": ["rank", "action_type", "title", "priority", "priority_score", "rationale", "next_step"],
            },
        },
        "open_questions": {
            "type": "array",
            "description": "Missing context needed to refine threats, requirements, and priorities.",
            "items": {"type": "string"},
        },
    },
    "required": [
        "component_name",
        "level",
        "summary",
        "deployment_assumptions",
        "prioritization_summary",
        "threats",
        "security_requirements",
        "prioritized_actions",
        "open_questions",
    ],
}


def responses_text_format() -> dict[str, Any]:
    """Return the Responses API structured-output configuration."""

    return {
        "format": {
            "type": "json_schema",
            "name": "component_threat_assessment",
            "strict": True,
            "schema": ASSESSMENT_SCHEMA,
        }
    }
