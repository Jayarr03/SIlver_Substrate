"""Command-line entry point for the Silver Substrate pipeline."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Sequence

from .hierarchy import HardwareLevel
from .interactive import confirm_suggestions, format_suggestion_for_display, generate_component_suggestions
from .models import ComponentInput
from .multi_agent_pipeline import MultiAgentPipeline
from .openai_client import OpenAIResponsesClient
from .pipeline import ThreatGenerationPipeline
from .settings import load_env_file


def find_env_file(env_file_arg: str) -> str:
    """Find .env file by checking multiple locations."""
    # If user provided a specific path, use it
    if env_file_arg != ".env":
        return env_file_arg
    
    # Search common locations
    search_paths = [
        Path.cwd() / ".env",                    # Current directory
        Path.cwd().parent / ".env",             # Parent directory
        Path(__file__).parent.parent.parent / ".env",  # Project root
    ]
    
    for path in search_paths:
        if path.exists():
            return str(path)
    
    # Default to .env if not found (will be handled by load_env_file)
    return ".env"


def sanitize_filename(name: str) -> str:
    """Convert component name to a safe filename."""
    # Remove or replace unsafe characters
    safe = re.sub(r'[^\w\s-]', '', name.lower())
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe.strip('_')


def save_assessment_to_library(assessment_data: dict, component_name: str, library_dir: Path) -> Path:
    """Save assessment to library folder with timestamped filename."""
    # Create library directory if it doesn't exist
    library_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename: component_name_YYYYMMDD_HHMMSS.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = sanitize_filename(component_name)
    filename = f"{safe_name}_{timestamp}.json"
    filepath = library_dir / filename
    
    # Save JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(assessment_data, f, indent=2, sort_keys=True, default=str)
    
    return filepath


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""

    parser = argparse.ArgumentParser(description="Generate sub-firmware hardware threat assessments.")
    parser.add_argument("--component", required=True, help="Component name, such as 'bond pad' or 'gate oxide'.")
    parser.add_argument(
        "--level",
        choices=[level.value for level in HardwareLevel],
        help="Hardware level. If omitted, AI will suggest appropriate metadata interactively."
    )
    parser.add_argument("--description", default="", help="Short context description for the component.")
    parser.add_argument("--asset", action="append", default=[], help="Asset protected by the component. May repeat.")
    parser.add_argument("--assumption", action="append", default=[], help="Design or threat model assumption. May repeat.")
    parser.add_argument("--interface", action="append", default=[], help="Physical, electrical, or process interface. May repeat.")
    parser.add_argument("--process-context", action="append", default=[], help="Fabrication/package context. May repeat.")
    parser.add_argument(
        "--priority-driver",
        action="append",
        default=[],
        help=(
            "Component-specific prioritization driver, such as high-value asset, exposed package, "
            "or no field update path. May repeat."
        ),
    )
    parser.add_argument("--model", help="OpenAI model to use. Defaults to OPENAI_MODEL when omitted.")
    parser.add_argument("--env-file", default=".env", help="Dotenv file containing OPENAI_API_KEY and OPENAI_MODEL.")
    parser.add_argument(
        "--agent-mode",
        choices=["single", "minimal", "full"],
        default="single",
        help=(
            "Analysis mode: 'single' (current single-pass), 'minimal' (6-agent pipeline), "
            "'full' (12-agent pipeline with comprehensive review). Default: single"
        ),
    )
    parser.add_argument(
        "--library-dir",
        default="library",
        help="Directory to save assessment JSON files. Defaults to 'library' in project root."
    )
    parser.add_argument(
        "--build-request",
        action="store_true",
        help="Print the composed model request instead of calling the OpenAI API.",
    )
    args = parser.parse_args(argv)

    # Find and load environment file
    env_file_path = find_env_file(args.env_file)
    load_env_file(env_file_path)
    
    # Check for required environment variables
    if "OPENAI_API_KEY" not in os.environ:
        print("❌ Error: OPENAI_API_KEY not found in environment or .env file")
        print(f"   Searched: {env_file_path}")
        print("\nPlease create a .env file with:")
        print("   OPENAI_API_KEY=your-key-here")
        print("   OPENAI_MODEL=gpt-4o")
        return 1
    
    if "OPENAI_MODEL" not in os.environ:
        print("❌ Error: OPENAI_MODEL not found in environment or .env file")
        print(f"   Searched: {env_file_path}")
        print("\nPlease add OPENAI_MODEL to your .env file")
        return 1
    
    api_key = os.environ["OPENAI_API_KEY"]
    model = args.model or os.environ["OPENAI_MODEL"]

    # Interactive mode: only component name provided, generate suggestions
    if args.level is None:
        print(f"\n🔍 Analyzing component '{args.component}' to suggest metadata...\n")
        
        try:
            suggestion = generate_component_suggestions(
                component_name=args.component,
                api_key=api_key,
                model=model,
            )
        except Exception as e:
            print(f"❌ Error generating suggestions: {e}")
            print("\nPlease provide --level and other options explicitly.")
            return 1

        # Display suggestions
        print(format_suggestion_for_display(args.component, suggestion))
        
        # Get confirmation
        if not confirm_suggestions():
            print("\nAssessment cancelled.")
            return 0
        
        # Build component from suggestions
        component = ComponentInput(
            name=args.component,
            level=suggestion.level,
            description=suggestion.description,
            assets=suggestion.assets,
            assumptions=tuple(args.assumption),  # User can still provide these
            interfaces=suggestion.interfaces,
            process_context=tuple(args.process_context),
            priority_drivers=suggestion.priority_drivers,
        )
    else:
        # Explicit mode: all options provided by user
        component = ComponentInput(
            name=args.component,
            level=HardwareLevel(args.level),
            description=args.description,
            assets=tuple(args.asset),
            assumptions=tuple(args.assumption),
            interfaces=tuple(args.interface),
            process_context=tuple(args.process_context),
            priority_drivers=tuple(args.priority_driver),
        )

    # Select pipeline based on agent mode
    if args.agent_mode == "single":
        pipeline = ThreatGenerationPipeline(
            client=OpenAIResponsesClient(model=args.model, env_file=env_file_path),
            model=args.model,
        )
        mode_description = "single-pass analysis"
        
        if args.build_request:
            request = pipeline.build_request(component)
            print(json.dumps(asdict(request), indent=2, sort_keys=True, default=str))
            return 0
    else:
        if args.build_request:
            print("❌ --build-request is only supported for single-agent mode")
            return 1
        
        pipeline = MultiAgentPipeline(
            client=OpenAIResponsesClient(model=args.model, env_file=env_file_path),
            agent_mode=args.agent_mode,
            model=args.model,
        )
        agent_count = 6 if args.agent_mode == "minimal" else 12
        mode_description = f"{args.agent_mode} multi-agent pipeline ({agent_count} agents)"

    print(f"\n🚀 Generating threat assessment using {mode_description}...\n")
    assessment = pipeline.run(component)
    assessment_data = asdict(assessment)
    
    # Determine library directory path (relative to project root)
    if Path(args.library_dir).is_absolute():
        library_dir = Path(args.library_dir)
    else:
        # Find project root (where .env is located)
        env_path = Path(env_file_path)
        if env_path.exists():
            project_root = env_path.parent
        else:
            project_root = Path.cwd()
        library_dir = project_root / args.library_dir
    
    # Save to library
    saved_path = save_assessment_to_library(assessment_data, args.component, library_dir)
    
    # Print summary
    print("✅ Assessment complete!")
    print(f"📁 Saved to: {saved_path.relative_to(Path.cwd()) if saved_path.is_relative_to(Path.cwd()) else saved_path}")
    print(f"\n📊 Summary:")
    print(f"   Component: {assessment.component_name}")
    print(f"   Level: {assessment.level.value}")
    print(f"   Threats: {len(assessment.threats)}")
    print(f"   Requirements: {len(assessment.security_requirements)}")
    print(f"   Priority Actions: {len(assessment.prioritized_actions)}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
