"""Threat generation pipeline for sub-firmware hardware components."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ComponentAssessment, ComponentInput, PipelineRequest
from .openai_client import AssessmentClient
from .prompts import PromptComposer
from .schema import ASSESSMENT_SCHEMA


@dataclass(frozen=True)
class ThreatGenerationPipeline:
    """Compose prompts, call a model client, and normalize model output."""

    client: AssessmentClient
    composer: PromptComposer = PromptComposer()
    model: str | None = None

    def build_request(self, component: ComponentInput) -> PipelineRequest:
        """Build the model request without calling an API."""

        return PipelineRequest(
            component=component,
            messages=self.composer.compose(component),
            response_schema=ASSESSMENT_SCHEMA,
            model=self.model,
        )

    def run(self, component: ComponentInput) -> ComponentAssessment:
        """Generate a structured assessment for a component."""

        request = self.build_request(component)
        raw_assessment = self.client.generate(request)
        return ComponentAssessment.from_mapping(raw_assessment)
