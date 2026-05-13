"""Data models for silicon-layer threat assessments."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .hierarchy import HardwareLevel
from .lifecycle import SdlcPhase


@dataclass(frozen=True)
class ComponentInput:
    """A component and operating context to feed into the assessment pipeline."""

    name: str
    level: HardwareLevel
    description: str = ""
    assets: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    interfaces: tuple[str, ...] = ()
    process_context: tuple[str, ...] = ()
    priority_drivers: tuple[str, ...] = ()

    def to_prompt_payload(self) -> dict[str, Any]:
        """Return a JSON-serializable representation for model prompting."""

        payload = asdict(self)
        payload["level"] = self.level.value
        return payload


@dataclass(frozen=True)
class PipelineRequest:
    """A fully composed model request produced by the pipeline."""

    component: ComponentInput
    messages: tuple[dict[str, str], ...]
    response_schema: dict[str, Any]
    model: str | None = None


@dataclass(frozen=True)
class Threat:
    """One generated threat at the selected hardware level and SDLC phase."""

    title: str
    description: str
    sdlc_phase: SdlcPhase
    sdlc_phase_description: str
    scenario: str
    attack_surface: str
    preconditions: tuple[str, ...]
    potential_impact: str
    deployment_consequence: str
    priority: str
    priority_score: int
    priority_rationale: str
    confidence: str


@dataclass(frozen=True)
class SecurityRequirement:
    """A mitigation or verification requirement linked to generated threats."""

    title: str
    description: str
    sdlc_phase: SdlcPhase
    requirement: str
    mitigates: tuple[str, ...]
    verification_method: str
    owner: str
    design_robustness: str
    priority: str
    priority_score: int
    priority_rationale: str


@dataclass(frozen=True)
class PrioritizedAction:
    """A ranked threat/requirement action for a specific component."""

    rank: int
    action_type: str
    title: str
    priority: str
    priority_score: int
    rationale: str
    next_step: str


# Multi-agent specific data models


@dataclass(frozen=True)
class ComponentScope:
    """Component boundaries and relationships from decomposition agent."""

    component_definition: str
    component_boundaries: str
    parent_components: tuple[str, ...]
    child_or_sub_components: tuple[str, ...]
    adjacent_components: tuple[str, ...]
    normal_operating_conditions: tuple[str, ...]
    out_of_scope_items: tuple[str, ...]


@dataclass(frozen=True)
class FailureMechanism:
    """Physical failure mechanism identified by device physics agent."""

    name: str
    mechanism: str
    trigger_conditions: tuple[str, ...]
    observable_effects: tuple[str, ...]
    permanence: str  # transient | persistent | permanent
    security_relevance: str


@dataclass(frozen=True)
class AttackerModel:
    """Attacker capabilities and threat scenarios from adversarial agent."""

    attacker_capabilities: tuple[str, ...]
    excluded_capabilities: tuple[str, ...]
    environmental_influences: tuple[str, ...]


@dataclass(frozen=True)
class ThreatScenario:
    """Individual threat scenario from adversarial threat agent."""

    title: str
    attacker_capability: str
    attack_path: str
    physical_mechanism: str
    security_impact: str
    preconditions: tuple[str, ...]
    confidence: str


@dataclass(frozen=True)
class LifecycleRisk:
    """Lifecycle degradation risk from reliability agent."""

    risk: str
    lifecycle_stage: str
    accelerating_conditions: tuple[str, ...]
    impact: str
    recommended_controls: tuple[str, ...]


@dataclass(frozen=True)
class ManufacturingRisk:
    """Manufacturing and supply chain risk information."""

    manufacturing_risks: tuple[str, ...]
    supply_chain_risks: tuple[str, ...]
    process_controls: tuple[str, ...]
    required_evidence: tuple[str, ...]
    open_supplier_questions: tuple[str, ...]


@dataclass(frozen=True)
class Countermeasure:
    """Security countermeasure from countermeasure design agent."""

    title: str
    type: str  # preventive | detective | corrective | compensating
    description: str
    implementation_layer: str
    mitigates: tuple[str, ...]
    owner: str
    residual_risk: str


@dataclass(frozen=True)
class VerificationPlanItem:
    """Verification plan item from validation agent."""

    control_or_requirement: str
    test_method: str
    evidence_required: str
    acceptance_criteria: str
    test_stage: str


@dataclass(frozen=True)
class OpenQuestion:
    """Open question for stakeholders from question generation agent."""

    question: str
    asked_of: str
    why_it_matters: str
    blocks: tuple[str, ...]
    priority: str


@dataclass(frozen=True)
class PrioritizedItem:
    """Prioritized item with multi-dimensional scoring."""

    item_title: str
    item_type: str
    impact: int
    exploitability: int
    permanence: int
    detectability: int
    lifecycle_lock_in: int
    confidence: int
    total_score: int
    priority: str
    rationale: str


@dataclass(frozen=True)
class CriticFinding:
    """Quality review finding from critic agent."""

    finding: str
    severity: str
    evidence: str
    recommended_fix: str


@dataclass(frozen=True)
class QualityScore:
    """Quality scoring from critic agent."""

    technical_accuracy: int
    security_framing: int
    actionability: int
    testability: int
    prioritization_quality: int


@dataclass(frozen=True)
class ImplementationSummary:
    """Implementation planning from executive summarizer."""

    executive_summary: str
    top_threats: tuple[str, ...]
    top_recommendations: tuple[str, ...]
    implementation_plan: tuple[str, ...]
    decision_points: tuple[str, ...]
    residual_risks: tuple[str, ...]


@dataclass(frozen=True)
class ComponentAssessment:
    """Structured output returned by the LLM and normalized by the pipeline.
    
    Supports both single-agent (legacy) and multi-agent pipeline outputs.
    Multi-agent fields are optional for backward compatibility.
    """

    component_name: str
    level: HardwareLevel
    summary: str
    deployment_assumptions: str
    prioritization_summary: str
    threats: tuple[Threat, ...] = field(default_factory=tuple)
    security_requirements: tuple[SecurityRequirement, ...] = field(default_factory=tuple)
    prioritized_actions: tuple[PrioritizedAction, ...] = field(default_factory=tuple)
    open_questions: tuple[str, ...] = field(default_factory=tuple)
    
    # Multi-agent pipeline fields (optional for backward compatibility)
    agent_mode: str | None = None  # 'single' | 'minimal' | 'full'
    scope: ComponentScope | None = None
    failure_mechanisms: tuple[FailureMechanism, ...] = field(default_factory=tuple)
    attacker_model: AttackerModel | None = None
    threat_scenarios: tuple[ThreatScenario, ...] = field(default_factory=tuple)
    lifecycle_risks: tuple[LifecycleRisk, ...] = field(default_factory=tuple)
    manufacturing_risk: ManufacturingRisk | None = None
    countermeasures: tuple[Countermeasure, ...] = field(default_factory=tuple)
    verification_plan: tuple[VerificationPlanItem, ...] = field(default_factory=tuple)
    open_questions_detailed: tuple[OpenQuestion, ...] = field(default_factory=tuple)
    prioritized_items: tuple[PrioritizedItem, ...] = field(default_factory=tuple)
    critic_findings: tuple[CriticFinding, ...] = field(default_factory=tuple)
    quality_score: QualityScore | None = None
    implementation_summary: ImplementationSummary | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "ComponentAssessment":
        """Create an assessment from the JSON object returned by a model."""

        return cls(
            component_name=str(data["component_name"]),
            level=HardwareLevel(data["level"]),
            summary=str(data["summary"]),
            deployment_assumptions=str(data["deployment_assumptions"]),
            prioritization_summary=str(data["prioritization_summary"]),
            threats=tuple(
                Threat(
                    title=str(item["title"]),
                    description=str(item["description"]),
                    sdlc_phase=SdlcPhase(item["sdlc_phase"]),
                    sdlc_phase_description=str(item["sdlc_phase_description"]),
                    scenario=str(item["scenario"]),
                    attack_surface=str(item["attack_surface"]),
                    preconditions=tuple(str(value) for value in item["preconditions"]),
                    potential_impact=str(item["potential_impact"]),
                    deployment_consequence=str(item["deployment_consequence"]),
                    priority=str(item["priority"]),
                    priority_score=int(item["priority_score"]),
                    priority_rationale=str(item["priority_rationale"]),
                    confidence=str(item["confidence"]),
                )
                for item in data["threats"]
            ),
            security_requirements=tuple(
                SecurityRequirement(
                    title=str(item["title"]),
                    description=str(item["description"]),
                    sdlc_phase=SdlcPhase(item["sdlc_phase"]),
                    requirement=str(item["requirement"]),
                    mitigates=tuple(str(value) for value in item["mitigates"]),
                    verification_method=str(item["verification_method"]),
                    owner=str(item["owner"]),
                    design_robustness=str(item["design_robustness"]),
                    priority=str(item["priority"]),
                    priority_score=int(item["priority_score"]),
                    priority_rationale=str(item["priority_rationale"]),
                )
                for item in data["security_requirements"]
            ),
            prioritized_actions=tuple(
                PrioritizedAction(
                    rank=int(item["rank"]),
                    action_type=str(item["action_type"]),
                    title=str(item["title"]),
                    priority=str(item["priority"]),
                    priority_score=int(item["priority_score"]),
                    rationale=str(item["rationale"]),
                    next_step=str(item["next_step"]),
                )
                for item in data["prioritized_actions"]
            ),
            open_questions=tuple(str(value) for value in data["open_questions"]),
        )
