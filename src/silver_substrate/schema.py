"""JSON schema used for structured model output."""

from __future__ import annotations

from typing import Any

HARDWARE_LEVEL_VALUES = [
    "system",
    "architecture",
    "microarchitecture",
    "rtl",
    "gate",
    "transistor",
    "layout",
    "process",
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


# Multi-agent pipeline schemas

COMPONENT_SCOPE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "component_definition": {"type": "string"},
        "component_boundaries": {"type": "string"},
        "parent_components": {"type": "array", "items": {"type": "string"}},
        "child_or_sub_components": {"type": "array", "items": {"type": "string"}},
        "adjacent_components": {"type": "array", "items": {"type": "string"}},
        "normal_operating_conditions": {"type": "array", "items": {"type": "string"}},
        "out_of_scope_items": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "component_definition",
        "component_boundaries",
        "parent_components",
        "child_or_sub_components",
        "adjacent_components",
        "normal_operating_conditions",
        "out_of_scope_items",
    ],
}


FAILURE_MECHANISM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "failure_mechanisms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "mechanism": {"type": "string"},
                    "trigger_conditions": {"type": "array", "items": {"type": "string"}},
                    "observable_effects": {"type": "array", "items": {"type": "string"}},
                    "permanence": {"type": "string", "enum": ["transient", "persistent", "permanent"]},
                    "security_relevance": {"type": "string"},
                },
                "required": [
                    "name",
                    "mechanism",
                    "trigger_conditions",
                    "observable_effects",
                    "permanence",
                    "security_relevance",
                ],
            },
        }
    },
    "required": ["failure_mechanisms"],
}


ATTACKER_MODEL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "attacker_models": {"type": "array", "items": {"type": "string"}},
        "threat_scenarios": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "attacker_capability": {"type": "string"},
                    "attack_path": {"type": "string"},
                    "physical_mechanism": {"type": "string"},
                    "security_impact": {"type": "string"},
                    "preconditions": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "string", "enum": ["low", "medium", "high"]},
                },
                "required": [
                    "title",
                    "attacker_capability",
                    "attack_path",
                    "physical_mechanism",
                    "security_impact",
                    "preconditions",
                    "confidence",
                ],
            },
        },
    },
    "required": ["attacker_models", "threat_scenarios"],
}


LIFECYCLE_RISK_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "lifecycle_risks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "risk": {"type": "string"},
                    "lifecycle_stage": {
                        "type": "string",
                        "enum": ["manufacture", "test", "deployment", "field operation", "end of life"],
                    },
                    "accelerating_conditions": {"type": "array", "items": {"type": "string"}},
                    "impact": {"type": "string"},
                    "recommended_controls": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "risk",
                    "lifecycle_stage",
                    "accelerating_conditions",
                    "impact",
                    "recommended_controls",
                ],
            },
        }
    },
    "required": ["lifecycle_risks"],
}


MANUFACTURING_RISK_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "manufacturing_risks": {"type": "array", "items": {"type": "string"}},
        "supply_chain_risks": {"type": "array", "items": {"type": "string"}},
        "process_controls": {"type": "array", "items": {"type": "string"}},
        "required_evidence": {"type": "array", "items": {"type": "string"}},
        "open_supplier_questions": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "manufacturing_risks",
        "supply_chain_risks",
        "process_controls",
        "required_evidence",
        "open_supplier_questions",
    ],
}


COUNTERMEASURE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "countermeasures": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "type": {"type": "string", "enum": ["preventive", "detective", "corrective", "compensating"]},
                    "description": {"type": "string"},
                    "implementation_layer": {"type": "string"},
                    "mitigates": {"type": "array", "items": {"type": "string"}},
                    "owner": {"type": "string"},
                    "residual_risk": {"type": "string"},
                },
                "required": [
                    "title",
                    "type",
                    "description",
                    "implementation_layer",
                    "mitigates",
                    "owner",
                    "residual_risk",
                ],
            },
        }
    },
    "required": ["countermeasures"],
}


VERIFICATION_PLAN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "verification_plan": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "control_or_requirement": {"type": "string"},
                    "test_method": {"type": "string"},
                    "evidence_required": {"type": "string"},
                    "acceptance_criteria": {"type": "string"},
                    "test_stage": {
                        "type": "string",
                        "enum": ["pre-silicon", "post-silicon", "manufacturing", "field monitoring"],
                    },
                },
                "required": [
                    "control_or_requirement",
                    "test_method",
                    "evidence_required",
                    "acceptance_criteria",
                    "test_stage",
                ],
            },
        }
    },
    "required": ["verification_plan"],
}


OPEN_QUESTIONS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "open_questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "asked_of": {"type": "string"},
                    "why_it_matters": {"type": "string"},
                    "blocks": {"type": "array", "items": {"type": "string"}},
                    "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                },
                "required": ["question", "asked_of", "why_it_matters", "blocks", "priority"],
            },
        }
    },
    "required": ["open_questions"],
}


PRIORITIZATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "prioritized_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item_title": {"type": "string"},
                    "item_type": {"type": "string"},
                    "impact": {"type": "integer", "minimum": 1, "maximum": 10},
                    "exploitability": {"type": "integer", "minimum": 1, "maximum": 10},
                    "permanence": {"type": "integer", "minimum": 1, "maximum": 10},
                    "detectability": {"type": "integer", "minimum": 1, "maximum": 10},
                    "lifecycle_lock_in": {"type": "integer", "minimum": 1, "maximum": 10},
                    "confidence": {"type": "integer", "minimum": 1, "maximum": 10},
                    "total_score": {"type": "integer"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                    "rationale": {"type": "string"},
                },
                "required": [
                    "item_title",
                    "item_type",
                    "impact",
                    "exploitability",
                    "permanence",
                    "detectability",
                    "lifecycle_lock_in",
                    "confidence",
                    "total_score",
                    "priority",
                    "rationale",
                ],
            },
        }
    },
    "required": ["prioritized_items"],
}


QUALITY_CRITIC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "review_findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "finding": {"type": "string"},
                    "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                    "evidence": {"type": "string"},
                    "recommended_fix": {"type": "string"},
                },
                "required": ["finding", "severity", "evidence", "recommended_fix"],
            },
        },
        "quality_score": {
            "type": "object",
            "properties": {
                "technical_accuracy": {"type": "integer", "minimum": 0, "maximum": 100},
                "security_framing": {"type": "integer", "minimum": 0, "maximum": 100},
                "actionability": {"type": "integer", "minimum": 0, "maximum": 100},
                "testability": {"type": "integer", "minimum": 0, "maximum": 100},
                "prioritization_quality": {"type": "integer", "minimum": 0, "maximum": 100},
            },
            "required": [
                "technical_accuracy",
                "security_framing",
                "actionability",
                "testability",
                "prioritization_quality",
            ],
        },
    },
    "required": ["review_findings", "quality_score"],
}


IMPLEMENTATION_SUMMARY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "executive_summary": {"type": "string"},
        "top_threats": {"type": "array", "items": {"type": "string"}},
        "top_recommendations": {"type": "array", "items": {"type": "string"}},
        "implementation_plan": {"type": "array", "items": {"type": "string"}},
        "decision_points": {"type": "array", "items": {"type": "string"}},
        "residual_risks": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "executive_summary",
        "top_threats",
        "top_recommendations",
        "implementation_plan",
        "decision_points",
        "residual_risks",
    ],
}


def _add_additional_properties_false(schema: dict[str, Any]) -> dict[str, Any]:
    """Recursively add additionalProperties: false to all objects in schema for strict mode."""
    if not isinstance(schema, dict):
        return schema
    
    result = schema.copy()
    
    # Add additionalProperties: false to this object if it's an object type
    if result.get("type") == "object" and "additionalProperties" not in result:
        result["additionalProperties"] = False
    
    # Recursively process nested schemas
    if "properties" in result:
        result["properties"] = {
            key: _add_additional_properties_false(value)
            for key, value in result["properties"].items()
        }
    
    if "items" in result:
        result["items"] = _add_additional_properties_false(result["items"])
    
    if "additionalProperties" in result and isinstance(result["additionalProperties"], dict):
        result["additionalProperties"] = _add_additional_properties_false(result["additionalProperties"])
    
    return result


def responses_text_format(schema: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the Responses API structured-output configuration.
    
    Args:
        schema: Optional custom schema. If not provided, uses ASSESSMENT_SCHEMA.
    """
    final_schema = schema if schema is not None else ASSESSMENT_SCHEMA
    
    # Recursively ensure all objects have additionalProperties: false for strict mode
    final_schema = _add_additional_properties_false(final_schema)
    
    return {
        "format": {
            "type": "json_schema",
            "name": "component_threat_assessment",
            "strict": True,
            "schema": final_schema,
        }
    }
