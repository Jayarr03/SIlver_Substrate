"""Hardware abstraction levels supported by the threat generation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class HardwareLevel(StrEnum):
    """Levels below software/firmware that can be assessed."""

    ARCHITECTURE_RTL_GATES = "architecture_rtl_gates"
    TRANSISTORS = "transistors"
    TERMINALS_CHANNEL_BODY = "terminals_channel_body"
    DOPED_REGIONS_WELLS_JUNCTIONS = "doped_regions_wells_junctions"
    OXIDES_DIELECTRICS_ISOLATION = "oxides_dielectrics_isolation"
    CONTACTS_VIAS_INTERCONNECTS = "contacts_vias_interconnects"
    PASSIVATION_PROTECTIVE_LAYERS = "passivation_protective_layers"
    DIE_PACKAGE_SUBSTRATE_PINS = "die_package_substrate_pins"
    WAFER_PROCESS_CHEMISTRY = "wafer_process_chemistry"


@dataclass(frozen=True)
class LevelProfile:
    """Prompting metadata for one layer of the silicon stack."""

    level: HardwareLevel
    display_name: str
    component_examples: tuple[str, ...]
    threat_lenses: tuple[str, ...]
    evidence_to_collect: tuple[str, ...]


LEVEL_PROFILES: dict[HardwareLevel, LevelProfile] = {
    HardwareLevel.ARCHITECTURE_RTL_GATES: LevelProfile(
        level=HardwareLevel.ARCHITECTURE_RTL_GATES,
        display_name="Architecture / RTL / Gates",
        component_examples=("bus fabric", "debug controller", "crypto datapath", "scan chain"),
        threat_lenses=(
            "privilege or isolation boundary violations",
            "logic Trojan insertion or trigger paths",
            "fault propagation through control and datapath logic",
            "test/debug feature misuse",
        ),
        evidence_to_collect=("netlist or RTL role", "clock/reset domains", "test access", "security boundary"),
    ),
    HardwareLevel.TRANSISTORS: LevelProfile(
        level=HardwareLevel.TRANSISTORS,
        display_name="Transistors",
        component_examples=("NMOS device", "PMOS device", "FinFET", "power transistor"),
        threat_lenses=(
            "device parameter manipulation",
            "aging, hot-carrier, or bias-temperature instability abuse",
            "fault injection sensitivity",
            "side-channel leakage from switching behavior",
        ),
        evidence_to_collect=("device type", "operating voltage", "criticality", "layout neighborhood"),
    ),
    HardwareLevel.TERMINALS_CHANNEL_BODY: LevelProfile(
        level=HardwareLevel.TERMINALS_CHANNEL_BODY,
        display_name="Source, Drain, Gate, Channel, Body",
        component_examples=("gate terminal", "source/drain extension", "channel", "body tie"),
        threat_lenses=(
            "threshold voltage shifts",
            "body-bias or latch-up misuse",
            "gate control integrity",
            "localized probing or modification",
        ),
        evidence_to_collect=("terminal function", "bias conditions", "physical accessibility", "guard structures"),
    ),
    HardwareLevel.DOPED_REGIONS_WELLS_JUNCTIONS: LevelProfile(
        level=HardwareLevel.DOPED_REGIONS_WELLS_JUNCTIONS,
        display_name="Doped Regions / Wells / Junctions",
        component_examples=("N-well", "P-well", "junction", "implant region"),
        threat_lenses=(
            "implant dose or mask tampering",
            "leakage and breakdown manipulation",
            "well isolation bypass",
            "process variation exploitation",
        ),
        evidence_to_collect=("doping role", "isolation intent", "mask/process step", "known variation window"),
    ),
    HardwareLevel.OXIDES_DIELECTRICS_ISOLATION: LevelProfile(
        level=HardwareLevel.OXIDES_DIELECTRICS_ISOLATION,
        display_name="Oxides, Dielectrics, Isolation Structures",
        component_examples=("gate oxide", "STI", "ILD", "high-k dielectric"),
        threat_lenses=(
            "dielectric breakdown or thinning",
            "isolation defeat",
            "charge trapping and retention effects",
            "focused-ion-beam or delayering impact",
        ),
        evidence_to_collect=("material", "thickness/geometry", "isolation boundary", "stress profile"),
    ),
    HardwareLevel.CONTACTS_VIAS_INTERCONNECTS: LevelProfile(
        level=HardwareLevel.CONTACTS_VIAS_INTERCONNECTS,
        display_name="Contacts, Vias, Metal Interconnects",
        component_examples=("via stack", "top metal route", "power grid", "bond-pad trace"),
        threat_lenses=(
            "open/short insertion",
            "electromigration acceleration",
            "probing and microprobing exposure",
            "routing-level Trojan or reroute",
        ),
        evidence_to_collect=("net criticality", "metal layer", "redundancy", "physical exposure"),
    ),
    HardwareLevel.PASSIVATION_PROTECTIVE_LAYERS: LevelProfile(
        level=HardwareLevel.PASSIVATION_PROTECTIVE_LAYERS,
        display_name="Passivation and Protective Layers",
        component_examples=("passivation opening", "top coat", "shield mesh", "tamper coating"),
        threat_lenses=(
            "tamper evidence bypass",
            "delayering and backside access enablement",
            "environmental protection degradation",
            "shield continuity or coverage gaps",
        ),
        evidence_to_collect=("layer stack", "openings", "tamper sensors", "environmental requirements"),
    ),
    HardwareLevel.DIE_PACKAGE_SUBSTRATE_PINS: LevelProfile(
        level=HardwareLevel.DIE_PACKAGE_SUBSTRATE_PINS,
        display_name="Die, Bond Pads, Package, Substrate, Pins",
        component_examples=("bond pad", "package substrate", "pin", "wire bond"),
        threat_lenses=(
            "pin-level abuse and unintended modes",
            "package probing or rework",
            "substrate coupling and fault injection",
            "supply-chain substitution or damage",
        ),
        evidence_to_collect=("pin function", "package type", "access controls", "board-level exposure"),
    ),
    HardwareLevel.WAFER_PROCESS_CHEMISTRY: LevelProfile(
        level=HardwareLevel.WAFER_PROCESS_CHEMISTRY,
        display_name="Wafer Material, Process Chemistry, Lithography, Doping, Etching",
        component_examples=("photoresist step", "etch chemistry", "implant recipe", "wafer substrate"),
        threat_lenses=(
            "recipe tampering",
            "contamination or material substitution",
            "lithography mask manipulation",
            "metrology and process-control blind spots",
        ),
        evidence_to_collect=("process step", "control limits", "metrology", "supplier/fab boundary"),
    ),
}


def get_level_profile(level: HardwareLevel) -> LevelProfile:
    """Return prompting metadata for a hardware level."""

    return LEVEL_PROFILES[level]
