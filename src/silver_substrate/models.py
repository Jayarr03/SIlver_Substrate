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


@dataclass(frozen=True)
class ComponentAssessment:
    """Structured output returned by the LLM and normalized by the pipeline."""

    component_name: str
    level: HardwareLevel
    summary: str
    deployment_assumptions: str
    prioritization_summary: str
    threats: tuple[Threat, ...] = field(default_factory=tuple)
    security_requirements: tuple[SecurityRequirement, ...] = field(default_factory=tuple)
    prioritized_actions: tuple[PrioritizedAction, ...] = field(default_factory=tuple)
    open_questions: tuple[str, ...] = field(default_factory=tuple)

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
