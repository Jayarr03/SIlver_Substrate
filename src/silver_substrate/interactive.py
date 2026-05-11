"""Interactive component metadata generation for the CLI."""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Any

from .hierarchy import HardwareLevel


@dataclass(frozen=True)
class ComponentSuggestion:
    """AI-generated suggestions for component metadata."""

    level: HardwareLevel
    description: str
    assets: tuple[str, ...]
    interfaces: tuple[str, ...]
    priority_drivers: tuple[str, ...]
    rationale: str


def generate_component_suggestions(
    component_name: str,
    api_key: str,
    model: str,
    base_url: str = "https://api.openai.com/v1",
    timeout_seconds: int = 30,
) -> ComponentSuggestion:
    """Use OpenAI to suggest component metadata from just the name."""

    available_levels = [level.value for level in HardwareLevel]
    
    system_message = """You are a hardware security expert specializing in silicon-level threat modeling.
Given a hardware component name, suggest the most appropriate hardware abstraction level and relevant security context.

Your suggestions should be specific, security-focused, and appropriate for sub-firmware threat modeling."""

    user_message = f"""Component name: {component_name}

Please analyze this hardware component and provide:

1. **level**: The most appropriate hardware abstraction level from these options:
   - architecture_rtl_gates
   - transistors
   - terminals_channel_body
   - doped_regions_wells_junctions
   - oxides_dielectrics_isolation
   - contacts_vias_interconnects
   - passivation_protective_layers
   - die_package_substrate_pins
   - wafer_process_chemistry

2. **description**: A concise technical description (1-2 sentences) of this component's function and security relevance

3. **assets**: List of 1-4 critical assets this component might protect (e.g., cryptographic keys, authorization states, sensitive data)

4. **interfaces**: List of 1-4 physical, electrical, or process interfaces this component interacts with

5. **priority_drivers**: List of 1-4 component-specific security concerns (e.g., "no field update path", "externally accessible", "protects root keys")

6. **rationale**: Brief explanation (2-3 sentences) of why you chose this level and these security concerns

Respond with valid JSON only."""

    schema = {
        "type": "object",
        "properties": {
            "level": {
                "type": "string",
                "enum": available_levels,
                "description": "Hardware abstraction level for this component"
            },
            "description": {
                "type": "string",
                "description": "Concise technical description of the component"
            },
            "assets": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Critical assets protected by this component"
            },
            "interfaces": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Physical, electrical, or process interfaces"
            },
            "priority_drivers": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Component-specific security concerns"
            },
            "rationale": {
                "type": "string",
                "description": "Explanation of the suggestions"
            }
        },
        "required": ["level", "description", "assets", "interfaces", "priority_drivers", "rationale"],
        "additionalProperties": False
    }

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "component_metadata",
                "strict": True,
                "schema": schema
            }
        }
    }

    http_request = urllib.request.Request(
        url=f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(http_request, timeout=timeout_seconds) as response:
        response_data = json.loads(response.read().decode("utf-8"))

    content = response_data["choices"][0]["message"]["content"]
    suggestion_data = json.loads(content)

    return ComponentSuggestion(
        level=HardwareLevel(suggestion_data["level"]),
        description=suggestion_data["description"],
        assets=tuple(suggestion_data["assets"]),
        interfaces=tuple(suggestion_data["interfaces"]),
        priority_drivers=tuple(suggestion_data["priority_drivers"]),
        rationale=suggestion_data["rationale"],
    )


def format_suggestion_for_display(component_name: str, suggestion: ComponentSuggestion) -> str:
    """Format suggestions in a readable way for user confirmation."""

    lines = [
        "",
        "=" * 80,
        f"SUGGESTED METADATA FOR: {component_name}",
        "=" * 80,
        "",
        f"Hardware Level: {suggestion.level.value}",
        "",
        f"Description:",
        f"  {suggestion.description}",
        "",
        f"Protected Assets:",
    ]
    
    for asset in suggestion.assets:
        lines.append(f"  • {asset}")
    
    lines.extend([
        "",
        "Interfaces:",
    ])
    
    for interface in suggestion.interfaces:
        lines.append(f"  • {interface}")
    
    lines.extend([
        "",
        "Priority Drivers:",
    ])
    
    for driver in suggestion.priority_drivers:
        lines.append(f"  • {driver}")
    
    lines.extend([
        "",
        f"Rationale:",
        f"  {suggestion.rationale}",
        "",
        "=" * 80,
        "",
    ])
    
    return "\n".join(lines)


def confirm_suggestions() -> bool:
    """Prompt user to confirm suggestions."""

    while True:
        response = input("Proceed with this assessment? [Y/n/edit]: ").strip().lower()
        
        if response in ("", "y", "yes"):
            return True
        elif response in ("n", "no"):
            return False
        elif response in ("e", "edit"):
            print("\nEditing not yet implemented. Please run with explicit --level and options.")
            return False
        else:
            print("Please enter 'y' (yes), 'n' (no), or 'edit'.")
