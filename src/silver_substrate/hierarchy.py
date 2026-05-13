"""Hardware abstraction levels supported by the threat generation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class HardwareLevel(StrEnum):
    """Industry-standard hardware design abstraction levels."""

    SYSTEM = "system"
    ARCHITECTURE = "architecture"
    MICROARCHITECTURE = "microarchitecture"
    RTL = "rtl"
    GATE = "gate"
    TRANSISTOR = "transistor"
    LAYOUT = "layout"
    PROCESS = "process"


@dataclass(frozen=True)
class LevelProfile:
    """Prompting metadata for one hardware abstraction level."""

    level: HardwareLevel
    display_name: str
    component_examples: tuple[str, ...]
    threat_lenses: tuple[str, ...]
    evidence_to_collect: tuple[str, ...]


LEVEL_PROFILES: dict[HardwareLevel, LevelProfile] = {
    HardwareLevel.SYSTEM: LevelProfile(
        level=HardwareLevel.SYSTEM,
        display_name="System Level",
        component_examples=("SoC", "multi-chip module", "FPGA system", "embedded platform", "chiplet-based system"),
        threat_lenses=(
            "cross-component vulnerabilities and trust boundaries",
            "supply chain insertion and system-level backdoors",
            "board-level attacks and physical tampering",
            "power/clock distribution exploitation",
            "system boot and secure provisioning",
        ),
        evidence_to_collect=("system architecture", "chip boundaries", "boot flow", "trust anchors", "physical security"),
    ),
    HardwareLevel.ARCHITECTURE: LevelProfile(
        level=HardwareLevel.ARCHITECTURE,
        display_name="Architecture Level",
        component_examples=("CPU core", "GPU", "memory controller", "DMA engine", "crypto accelerator", "interconnect fabric"),
        threat_lenses=(
            "architectural isolation and privilege violations",
            "shared resource conflicts (cache, TLB, branch predictor)",
            "side-channel vulnerabilities across architectural boundaries",
            "covert channel potential",
            "ISA-level security guarantees",
        ),
        evidence_to_collect=("functional specification", "isolation domains", "shared resources", "privilege levels", "security extensions"),
    ),
    HardwareLevel.MICROARCHITECTURE: LevelProfile(
        level=HardwareLevel.MICROARCHITECTURE,
        display_name="Microarchitecture Level",
        component_examples=("pipeline stage", "branch predictor", "cache hierarchy", "TLB", "execution units", "reorder buffer"),
        threat_lenses=(
            "speculative execution vulnerabilities (Spectre, Meltdown)",
            "microarchitectural side channels and timing attacks",
            "cache-based covert channels",
            "transient execution exploits",
            "performance counter leakage",
        ),
        evidence_to_collect=("pipeline depth", "speculation mechanisms", "cache structure", "timing behaviors", "shared buffers"),
    ),
    HardwareLevel.RTL: LevelProfile(
        level=HardwareLevel.RTL,
        display_name="RTL (Register Transfer Level)",
        component_examples=("state machine", "counter", "FIFO", "register file", "control logic", "datapath"),
        threat_lenses=(
            "RTL-level logic bugs and design flaws",
            "state machine vulnerabilities and illegal states",
            "RTL trojans and malicious modifications",
            "timing violations and race conditions",
            "functional verification gaps",
        ),
        evidence_to_collect=("RTL code", "state transitions", "control signals", "clock domains", "reset behavior"),
    ),
    HardwareLevel.GATE: LevelProfile(
        level=HardwareLevel.GATE,
        display_name="Gate Level",
        component_examples=("NAND gate", "NOR gate", "XOR gate", "D flip-flop", "multiplexer", "gate netlist"),
        threat_lenses=(
            "gate-level hardware trojans",
            "logic locking and obfuscation bypass",
            "netlist reverse engineering",
            "fault injection targeting specific gates",
            "scan chain and test infrastructure abuse",
        ),
        evidence_to_collect=("netlist topology", "gate criticality", "scan insertion", "redundancy", "test points"),
    ),
    HardwareLevel.TRANSISTOR: LevelProfile(
        level=HardwareLevel.TRANSISTOR,
        display_name="Transistor Level",
        component_examples=("NMOS", "PMOS", "FinFET", "pass transistor", "SRAM cell", "sense amplifier"),
        threat_lenses=(
            "transistor-level aging effects (BTI, HCI, TDDB)",
            "threshold voltage manipulation and body biasing",
            "single-event effects and radiation-induced faults",
            "analog and mixed-signal vulnerabilities",
            "device physics exploitation",
        ),
        evidence_to_collect=("device type", "operating point", "aging models", "bias conditions", "layout context"),
    ),
    HardwareLevel.LAYOUT: LevelProfile(
        level=HardwareLevel.LAYOUT,
        display_name="Layout / Physical Design",
        component_examples=("metal layers", "vias", "standard cells", "power grid", "clock tree", "I/O pads"),
        threat_lenses=(
            "layout-level trojan insertion",
            "focused ion beam (FIB) modification",
            "electromagnetic and power side-channel emissions",
            "physical probing and microprobing",
            "electromigration and reliability attacks",
        ),
        evidence_to_collect=("layer stack", "metal criticality", "shielding", "physical access", "EM hotspots"),
    ),
    HardwareLevel.PROCESS: LevelProfile(
        level=HardwareLevel.PROCESS,
        display_name="Process / Fabrication",
        component_examples=("photomask", "ion implantation", "chemical vapor deposition", "CMP", "process node (7nm, 5nm)"),
        threat_lenses=(
            "foundry-level hardware trojans",
            "mask tampering and lithography manipulation",
            "process variation exploitation",
            "supply chain insertion during fabrication",
            "metrology and inspection blind spots",
        ),
        evidence_to_collect=("fab location", "process technology", "mask security", "supply chain", "inspection coverage"),
    ),
}


def get_level_profile(level: HardwareLevel) -> LevelProfile:
    """Return prompting metadata for a hardware level."""

    return LEVEL_PROFILES[level]
