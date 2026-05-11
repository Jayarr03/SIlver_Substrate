"""SDLC phases used to categorize hardware threats and mitigations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SdlcPhase(StrEnum):
    """Lifecycle layers where hardware threats should be considered."""

    REQUIREMENTS = "requirements"
    ARCHITECTURE_DESIGN = "architecture_design"
    IMPLEMENTATION = "implementation"
    VERIFICATION_VALIDATION = "verification_validation"
    MANUFACTURING_SUPPLY_CHAIN = "manufacturing_supply_chain"
    DEPLOYMENT_OPERATION = "deployment_operation"
    END_OF_LIFE = "end_of_life"


@dataclass(frozen=True)
class SdlcPhaseProfile:
    """Prompting metadata for one SDLC phase."""

    phase: SdlcPhase
    display_name: str
    description: str


SDLC_PHASE_PROFILES: dict[SdlcPhase, SdlcPhaseProfile] = {
    SdlcPhase.REQUIREMENTS: SdlcPhaseProfile(
        phase=SdlcPhase.REQUIREMENTS,
        display_name="Requirements",
        description="Security objectives, threat assumptions, non-updatable constraints, and lifecycle guarantees.",
    ),
    SdlcPhase.ARCHITECTURE_DESIGN: SdlcPhaseProfile(
        phase=SdlcPhase.ARCHITECTURE_DESIGN,
        display_name="Architecture / Design",
        description="Partitioning, trust boundaries, defense-in-depth, redundancy, and permanent design choices.",
    ),
    SdlcPhase.IMPLEMENTATION: SdlcPhaseProfile(
        phase=SdlcPhase.IMPLEMENTATION,
        display_name="Implementation",
        description="RTL, layout, package, process, and physical implementation details that realize the design.",
    ),
    SdlcPhase.VERIFICATION_VALIDATION: SdlcPhaseProfile(
        phase=SdlcPhase.VERIFICATION_VALIDATION,
        display_name="Verification / Validation",
        description="Pre-silicon, post-silicon, reliability, abuse-case, and security validation before release.",
    ),
    SdlcPhase.MANUFACTURING_SUPPLY_CHAIN: SdlcPhaseProfile(
        phase=SdlcPhase.MANUFACTURING_SUPPLY_CHAIN,
        display_name="Manufacturing / Supply Chain",
        description="Fab, assembly, test, logistics, provenance, process-control, and supplier integrity risks.",
    ),
    SdlcPhase.DEPLOYMENT_OPERATION: SdlcPhaseProfile(
        phase=SdlcPhase.DEPLOYMENT_OPERATION,
        display_name="Deployment / Operation",
        description="Threats that appear after shipment, including physical access, environment, aging, and field abuse.",
    ),
    SdlcPhase.END_OF_LIFE: SdlcPhaseProfile(
        phase=SdlcPhase.END_OF_LIFE,
        display_name="End of Life",
        description="Decommissioning, remanence, recycling, destructive analysis, and recovery of deployed devices.",
    ),
}


def sdlc_prompt_payload() -> list[dict[str, str]]:
    """Return SDLC phases as JSON-serializable prompt context."""

    return [
        {
            "phase": profile.phase.value,
            "display_name": profile.display_name,
            "description": profile.description,
        }
        for profile in SDLC_PHASE_PROFILES.values()
    ]
