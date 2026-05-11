"""Command-line entry point for the Silver Substrate pipeline."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Sequence

from .hierarchy import HardwareLevel
from .models import ComponentInput
from .openai_client import OpenAIResponsesClient
from .pipeline import ThreatGenerationPipeline


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""

    parser = argparse.ArgumentParser(description="Generate sub-firmware hardware threat assessments.")
    parser.add_argument("--component", required=True, help="Component name, such as 'bond pad' or 'gate oxide'.")
    parser.add_argument("--level", required=True, choices=[level.value for level in HardwareLevel])
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
        "--build-request",
        action="store_true",
        help="Print the composed model request instead of calling the OpenAI API.",
    )
    args = parser.parse_args(argv)

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
    pipeline = ThreatGenerationPipeline(
        client=OpenAIResponsesClient(model=args.model, env_file=args.env_file),
        model=args.model,
    )

    if args.build_request:
        request = pipeline.build_request(component)
        print(json.dumps(asdict(request), indent=2, sort_keys=True, default=str))
        return 0

    assessment = pipeline.run(component)
    print(json.dumps(asdict(assessment), indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
