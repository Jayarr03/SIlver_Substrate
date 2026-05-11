"""Minimal OpenAI Responses API client for the pipeline."""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol

from .models import PipelineRequest
from .schema import responses_text_format
from .settings import load_env_file


class AssessmentClient(Protocol):
    """Client interface used by the pipeline to generate structured assessments."""

    def generate(self, request: PipelineRequest) -> dict[str, Any]:
        """Return a JSON object matching the assessment schema."""


@dataclass(frozen=True)
class OpenAIResponsesClient:
    """Call OpenAI's Responses API with structured output enabled."""

    api_key: str | None = None
    model: str | None = None
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: int = 60
    env_file: str = ".env"

    def generate(self, request: PipelineRequest) -> dict[str, Any]:
        """Generate and parse an assessment from OpenAI's Responses API."""

        load_env_file(self.env_file)
        api_key = self.api_key or os.environ["OPENAI_API_KEY"]
        model = request.model or self.model or os.environ["OPENAI_MODEL"]
        body = {
            "model": model,
            "input": list(request.messages),
            "text": responses_text_format(),
        }
        http_request = urllib.request.Request(
            url=f"{self.base_url.rstrip('/')}/responses",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(http_request, timeout=self.timeout_seconds) as response:
            response_body = json.loads(response.read().decode("utf-8"))
        return _extract_json_payload(response_body)


def _extract_json_payload(response_body: dict[str, Any]) -> dict[str, Any]:
    """Extract the structured JSON text from a Responses API result."""

    if isinstance(response_body.get("output_text"), str):
        return json.loads(response_body["output_text"])

    for output_item in response_body.get("output", []):
        for content_item in output_item.get("content", []):
            if content_item.get("type") in {"output_text", "text"} and "text" in content_item:
                return json.loads(content_item["text"])

    raise ValueError("OpenAI response did not contain output_text JSON.")
