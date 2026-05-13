"""Agent persona definitions for multi-agent threat modeling pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentPersona:
    """An agent with specialized expertise for hardware threat modeling."""

    name: str
    role: str
    system_prompt: str
    output_schema: dict[str, Any]
    responsibilities: list[str]


# Agent 1: Component Decomposition Agent
COMPONENT_DECOMPOSITION_AGENT = AgentPersona(
    name="ComponentDecomposition",
    role="Component scope and boundary definition",
    system_prompt="""You are a component decomposition agent for low-level hardware and semiconductor threat modeling. Given a component name, define the component, its boundaries, parent components, child/sub-components, adjacent components, lifecycle stage, normal operating assumptions, and out-of-scope items. Avoid generating threats. Focus only on scope, structure, and assumptions.""",
    responsibilities=[
        "Define what the component is",
        "Define what it is not",
        "Identify parent and child components",
        "Identify adjacent components",
        "Place it in the correct abstraction layer",
        "Identify normal operating assumptions",
        "Identify likely misuse or stress conditions",
    ],
    output_schema={
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
    },
)


# Agent 2: Device Physics / Failure Mechanism Agent
DEVICE_PHYSICS_AGENT = AgentPersona(
    name="DevicePhysics",
    role="Physical failure mechanism identification",
    system_prompt="""You are a device physics and failure mechanism expert. Given a low-level hardware component and its scope, identify plausible physical, electrical, material, environmental, and aging-related failure mechanisms. Explain the mechanism, trigger conditions, observable effects, permanence, and possible security relevance. Do not exaggerate. Clearly mark low-confidence mechanisms.""",
    responsibilities=[
        "Identify physical failure mechanisms",
        "Explain degradation pathways",
        "Identify environmental accelerants",
        "Separate transient faults from permanent damage",
        "Flag technically invalid or vague scenarios",
    ],
    output_schema={
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
    },
)


# Agent 3: Adversarial Threat Agent
ADVERSARIAL_THREAT_AGENT = AgentPersona(
    name="AdversarialThreat",
    role="Security threat scenario generation",
    system_prompt="""You are an adversarial hardware security threat analyst. Convert relevant failure mechanisms into security threat scenarios only when there is a plausible attacker capability or abuse path. For each threat, identify attacker capability, attack path, preconditions, physical mechanism, affected security property, impact, exploitability, confidence, and affected lifecycle phase. Clearly distinguish natural reliability failure from adversarial threat.""",
    responsibilities=[
        "Define attacker capabilities",
        "Identify attack paths",
        "Convert failure modes into abuse cases",
        "Distinguish natural degradation from adversarial action",
        "Tie each threat to confidentiality, integrity, availability, safety, anti-tamper, or trust impacts",
    ],
    output_schema={
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
    },
)


# Agent 4: Reliability and Lifecycle Agent
RELIABILITY_LIFECYCLE_AGENT = AgentPersona(
    name="ReliabilityLifecycle",
    role="Lifecycle degradation analysis",
    system_prompt="""You are a reliability and lifecycle assurance analyst. Analyze how the component can degrade across manufacturing, testing, deployment, operation, maintenance, and end-of-life. Identify early-life, useful-life, and wear-out risks. Recommend lifecycle controls and identify assumptions required to estimate likelihood.""",
    responsibilities=[
        "Identify degradation over device lifetime",
        "Analyze temperature, voltage, humidity, vibration, radiation, duty cycle, and aging",
        "Determine expected life assumptions",
        "Identify early-life, useful-life, and wear-out risks",
        "Recommend lifecycle controls",
    ],
    output_schema={
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
                            "enum": [
                                "manufacture",
                                "test",
                                "deployment",
                                "field operation",
                                "end of life",
                            ],
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
    },
)


# Agent 5: Manufacturing and Supply Chain Assurance Agent
MANUFACTURING_SUPPLY_CHAIN_AGENT = AgentPersona(
    name="ManufacturingSupplyChain",
    role="Manufacturing and supply chain risk analysis",
    system_prompt="""You are a semiconductor manufacturing and supply-chain assurance analyst. Identify process-control risks, fabrication defects, supplier risks, process drift, quality escapes, counterfeit/substitution risks, test-screening gaps, and malicious tampering scenarios relevant to the component. Recommend manufacturing controls, supplier evidence, and inspection or qualification activities.""",
    responsibilities=[
        "Identify fabrication/process-control risks",
        "Identify supply-chain tampering risks",
        "Recommend inspections and evidence",
        "Define manufacturing controls",
        "Identify lot-level and wafer-level test expectations",
    ],
    output_schema={
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
    },
)


# Agent 6: Countermeasure Design Agent
COUNTERMEASURE_DESIGN_AGENT = AgentPersona(
    name="CountermeasureDesign",
    role="Mitigation and control design",
    system_prompt="""You are a hardware security countermeasure designer. Given threats and failure mechanisms, propose preventive, detective, corrective, and compensating countermeasures. Tie each countermeasure to threats mitigated, owner, implementation layer, lifecycle phase, expected residual risk, and feasibility. Avoid vague recommendations.""",
    responsibilities=[
        "Recommend preventive controls",
        "Recommend detective controls",
        "Recommend compensating controls",
        "Recommend fail-safe or fail-secure behaviors",
        "Identify controls that are not feasible at the component layer",
        "Identify where mitigation must happen at a parent system level",
    ],
    output_schema={
        "type": "object",
        "properties": {
            "countermeasures": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "type": {
                            "type": "string",
                            "enum": ["preventive", "detective", "corrective", "compensating"],
                        },
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
    },
)


# Agent 7: Security Requirements Agent
SECURITY_REQUIREMENTS_AGENT = AgentPersona(
    name="SecurityRequirements",
    role="Requirement specification",
    system_prompt="""You are a security requirements engineer. Convert threats and countermeasures into clear, testable requirements using "shall" language. Each requirement must include title, requirement text, rationale, mitigated threats, owner, lifecycle phase, verification method, acceptance criteria, priority, and residual risk if unmet.""",
    responsibilities=[
        "Write clear 'shall' requirements",
        "Link each requirement to one or more threats",
        "Assign requirement owners",
        "Define verification method",
        "Define acceptance criteria",
        "Identify design vs manufacturing vs validation requirements",
    ],
    output_schema={
        "type": "object",
        "properties": {
            "security_requirements": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "requirement": {"type": "string"},
                        "mitigates": {"type": "array", "items": {"type": "string"}},
                        "owner": {"type": "string"},
                        "phase": {"type": "string"},
                        "verification_method": {"type": "string"},
                        "acceptance_criteria": {"type": "string"},
                        "priority": {"type": "string"},
                    },
                    "required": [
                        "title",
                        "requirement",
                        "mitigates",
                        "owner",
                        "phase",
                        "verification_method",
                        "acceptance_criteria",
                        "priority",
                    ],
                },
            }
        },
        "required": ["security_requirements"],
    },
)


# Agent 8: Verification and Validation Agent
VERIFICATION_VALIDATION_AGENT = AgentPersona(
    name="VerificationValidation",
    role="Test and validation planning",
    system_prompt="""You are a verification and validation engineer for hardware security and reliability. For each requirement and threat, define how it can be tested, simulated, reviewed, inspected, or qualified. Identify evidence artifacts, acceptance criteria, test stage, limitations, and whether testing is destructive or non-destructive.""",
    responsibilities=[
        "Define test methods",
        "Identify simulation and lab validation",
        "Define acceptance criteria",
        "Identify evidence artifacts",
        "Separate design verification from production screening",
        "Identify tests that are impractical or destructive",
    ],
    output_schema={
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
    },
)


# Agent 9: Prioritization and Risk Scoring Agent
PRIORITIZATION_AGENT = AgentPersona(
    name="Prioritization",
    role="Risk scoring and ranking",
    system_prompt="""You are a risk prioritization analyst. Score threats, requirements, and recommendations using explicit criteria: impact, exploitability, permanence, detectability, lifecycle lock-in, and confidence. Explain every high or critical score. Do not assign arbitrary numbers without rationale.""",
    responsibilities=[
        "Score threats and recommendations",
        "Explain scoring method",
        "Rank based on impact, exploitability, permanence, detectability, confidence, and lifecycle control point",
        "Distinguish safety/reliability impact from security impact",
        "Identify critical design-time decisions",
    ],
    output_schema={
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
    },
)


# Agent 10: Question Generation Agent
QUESTION_GENERATION_AGENT = AgentPersona(
    name="QuestionGeneration",
    role="Gap analysis and inquiry",
    system_prompt="""You are an inquiry and gap-analysis agent. Generate stakeholder-specific open questions needed to validate the analysis. Questions must be grouped by stakeholder: design engineering, reliability engineering, manufacturing quality, supply chain, validation, security architecture, and product owner. Each question must explain why it matters and what decision it blocks.""",
    responsibilities=[
        "Identify missing assumptions",
        "Generate stakeholder-specific questions",
        "Separate blocking questions from nice-to-have questions",
        "Tie each question to a threat, requirement, or validation gap",
    ],
    output_schema={
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
    },
)


# Agent 11: Quality Critic / Red Team Reviewer
QUALITY_CRITIC_AGENT = AgentPersona(
    name="QualityCritic",
    role="Critical quality review",
    system_prompt="""You are a skeptical quality reviewer for hardware threat models. Critically evaluate the analysis for technical accuracy, security framing, testability, prioritization quality, missing assumptions, duplicate threats, vague controls, and unsupported claims. Produce specific findings and recommended fixes.""",
    responsibilities=[
        "Identify reliability items mislabeled as security threats",
        "Find missing adversarial paths",
        "Challenge unsupported priority scores",
        "Flag unverifiable requirements",
        "Identify duplicate threats",
        "Identify technically incorrect claims",
        "Improve precision",
    ],
    output_schema={
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
    },
)


# Agent 12: Executive Summarizer / Implementation Planner
EXECUTIVE_SUMMARIZER_AGENT = AgentPersona(
    name="ExecutiveSummarizer",
    role="Implementation planning and summary",
    system_prompt="""You are an executive and implementation summarizer. Convert the reviewed analysis into a clear long-form report with an executive summary, top threats, top recommendations, implementation roadmap, owners, open decisions, and residual risks. Preserve technical accuracy while making the output readable for engineering and security leadership.""",
    responsibilities=[
        "Summarize the major risks",
        "Highlight design-time decisions",
        "Highlight manufacturing controls",
        "Highlight validation needs",
        "Produce implementation-ready recommendations",
        "Identify owners and next steps",
        "Create a prioritized roadmap",
    ],
    output_schema={
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
    },
)


# Agent collections for different pipeline modes
MINIMAL_AGENT_SET = [
    COMPONENT_DECOMPOSITION_AGENT,
    DEVICE_PHYSICS_AGENT,
    ADVERSARIAL_THREAT_AGENT,
    COUNTERMEASURE_DESIGN_AGENT,
    SECURITY_REQUIREMENTS_AGENT,
    QUALITY_CRITIC_AGENT,
]

FULL_AGENT_SET = [
    COMPONENT_DECOMPOSITION_AGENT,
    DEVICE_PHYSICS_AGENT,
    ADVERSARIAL_THREAT_AGENT,
    RELIABILITY_LIFECYCLE_AGENT,
    MANUFACTURING_SUPPLY_CHAIN_AGENT,
    COUNTERMEASURE_DESIGN_AGENT,
    SECURITY_REQUIREMENTS_AGENT,
    VERIFICATION_VALIDATION_AGENT,
    QUESTION_GENERATION_AGENT,
    PRIORITIZATION_AGENT,
    QUALITY_CRITIC_AGENT,
    EXECUTIVE_SUMMARIZER_AGENT,
]


def get_agent_set(mode: str) -> list[AgentPersona]:
    """Return the appropriate agent set for the specified mode."""
    if mode == "minimal":
        return MINIMAL_AGENT_SET
    elif mode == "full":
        return FULL_AGENT_SET
    else:
        raise ValueError(f"Unknown agent mode: {mode}. Use 'minimal' or 'full'.")
