"""Prompt composition for hardware-layer threat generation."""

from __future__ import annotations

import json

from .hierarchy import get_level_profile
from .lifecycle import sdlc_prompt_payload
from .models import ComponentInput

SYSTEM_PROMPT = """You generate threat scenarios and security requirements for hardware below software/firmware.
Stay at the requested silicon/package/process abstraction level. Do not drift into software-only mitigations unless they directly verify or constrain the hardware component. Categorize each threat and requirement by SDLC phase. Assume many devices cannot be patched or updated after deployment, so recommendations must favor robust design-time controls, pre-deployment verification, supply-chain assurance, and durable mitigations that remain effective in the field. Produce concise, specific, testable structured JSON with descriptions and component-specific priorities.
"""


class PromptComposer:
    """Build level-specific prompts for the assessment model."""

    def compose(self, component: ComponentInput) -> tuple[dict[str, str], ...]:
        """Return Responses API-compatible messages for a component assessment."""

        profile = get_level_profile(component.level)
        instructions = {
            "task": "Generate threats and security requirements for the supplied component.",
            "level": profile.display_name,
            "component_examples_at_this_level": profile.component_examples,
            "threat_lenses_to_consider": profile.threat_lenses,
            "evidence_to_collect_or_request": profile.evidence_to_collect,
            "sdlc_phases": sdlc_prompt_payload(),
            "prioritization_method": (
                "Prioritize threats and requirements for this exact component using protected asset criticality, "
                "physical/electrical exposure, exploitability, potential impact, SDLC phase urgency, design lock-in, "
                "post-deployment remediation difficulty, and any component.priority_drivers supplied by the user. "
                "Use priority_score 1-100 and reserve critical for items that could cause severe irreversible impact "
                "or must be designed in before fabrication/package release."
            ),
            "immutability_guidance": (
                "Treat the device as difficult or impossible to update after release. Prefer requirements "
                "that can be designed in, verified before shipment, monitored through manufacturing controls, "
                "or made robust against later deployment threats without relying on field patches."
            ),
            "output_rules": (
                "Return JSON matching the provided schema. Include 3-6 threats categorized by SDLC phase, "
                "one or more robust design/security requirements per major threat class, descriptions for each "
                "threat and requirement, priority scores/rationales, ranked prioritized_actions, deployment consequences, "
                "and open questions where context is missing."
            ),
        }
        user_payload = {
            "component": component.to_prompt_payload(),
            "level_guidance": instructions,
        }
        return (
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, indent=2, sort_keys=True)},
        )
