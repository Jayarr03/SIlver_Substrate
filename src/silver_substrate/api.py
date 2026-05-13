"""Flask API for the Silver Substrate web interface."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS

from .hierarchy import HardwareLevel
from .interactive import generate_component_suggestions
from .settings import load_env_file

app = Flask(__name__)
CORS(app)

# Find project root and library directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
LIBRARY_DIR = PROJECT_ROOT / "library"
ENV_FILE = PROJECT_ROOT / ".env"


def get_api_credentials() -> tuple[str, str]:
    """Load API credentials from environment."""
    load_env_file(str(ENV_FILE))
    return os.environ["OPENAI_API_KEY"], os.environ["OPENAI_MODEL"]


@app.route("/api/health", methods=["GET"])
def health_check() -> tuple[dict[str, str], int]:
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/api/hardware-levels", methods=["GET"])
def get_hardware_levels() -> tuple[dict[str, Any], int]:
    """Get all available hardware levels."""
    levels = [
        {
            "value": level.value,
            "name": level.value.replace("_", " ").title(),
        }
        for level in HardwareLevel
    ]
    return jsonify({"levels": levels}), 200


@app.route("/api/assessments", methods=["GET"])
def list_assessments() -> tuple[dict[str, Any], int]:
    """List all assessment files in the library."""
    if not LIBRARY_DIR.exists():
        return jsonify({"assessments": []}), 200

    assessments = []
    for file_path in sorted(LIBRARY_DIR.glob("*.json"), reverse=True):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Get top threat preview for card display
            top_threat = None
            threats = data.get("threats", [])
            if threats:
                # Sort by priority_score descending to get highest priority threat
                sorted_threats = sorted(threats, key=lambda t: t.get("priority_score", 0), reverse=True)
                if sorted_threats:
                    top = sorted_threats[0]
                    top_threat = {
                        "title": top.get("title", ""),
                        "attack_surface": top.get("attack_surface", ""),
                        "scenario": top.get("scenario", ""),
                        "priority": top.get("priority", ""),
                        "priority_score": top.get("priority_score", 0),
                    }
            
            assessments.append({
                "filename": file_path.name,
                "component_name": data.get("component_name", "Unknown"),
                "level": data.get("level", "unknown"),
                "threat_count": len(data.get("threats", [])),
                "requirement_count": len(data.get("security_requirements", [])),
                "summary": data.get("summary", ""),
                "created": file_path.stat().st_mtime,
                "top_threat": top_threat,
            })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

    return jsonify({"assessments": assessments}), 200


@app.route("/api/assessments/<filename>", methods=["GET"])
def get_assessment(filename: str) -> tuple[dict[str, Any], int]:
    """Get a specific assessment by filename."""
    file_path = LIBRARY_DIR / filename
    
    if not file_path.exists() or not file_path.is_file():
        return jsonify({"error": "Assessment not found"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to read assessment: {str(e)}"}), 500


@app.route("/api/suggest", methods=["POST"])
def suggest_metadata() -> tuple[dict[str, Any], int]:
    """Generate metadata suggestions for a component name."""
    data = request.get_json()
    component_name = data.get("component_name", "").strip()
    
    if not component_name:
        return jsonify({"error": "component_name is required"}), 400

    try:
        api_key, model = get_api_credentials()
        suggestion = generate_component_suggestions(
            component_name=component_name,
            api_key=api_key,
            model=model,
        )
        
        return jsonify({
            "level": suggestion.level.value,
            "description": suggestion.description,
            "assets": list(suggestion.assets),
            "interfaces": list(suggestion.interfaces),
            "priority_drivers": list(suggestion.priority_drivers),
            "rationale": suggestion.rationale,
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to generate suggestions: {str(e)}"}), 500


@app.route("/api/assess", methods=["POST"])
def create_assessment() -> tuple[dict[str, Any], int]:
    """Create a new threat assessment."""
    data = request.get_json()
    component_name = data.get("component_name", "").strip()
    
    if not component_name:
        return jsonify({"error": "component_name is required"}), 400

    # Build CLI command
    cmd = [
        sys.executable, "-m", "silver_substrate.cli",
        "--component", component_name,
    ]
    
    # Add agent mode (default to single for backward compatibility)
    agent_mode = data.get("agent_mode", "single")
    if agent_mode not in ["single", "minimal", "full"]:
        return jsonify({"error": "agent_mode must be 'single', 'minimal', or 'full'"}), 400
    cmd.extend(["--agent-mode", agent_mode])
    
    # Add optional parameters if provided
    if "level" in data and data["level"]:
        cmd.extend(["--level", data["level"]])
    
    if "description" in data and data["description"]:
        cmd.extend(["--description", data["description"]])
    
    for asset in data.get("assets", []):
        if asset:
            cmd.extend(["--asset", asset])
    
    for interface in data.get("interfaces", []):
        if interface:
            cmd.extend(["--interface", interface])
    
    for driver in data.get("priority_drivers", []):
        if driver:
            cmd.extend(["--priority-driver", driver])

    try:
        # Adjust timeout based on agent mode
        # Single: 120s, Minimal (6 agents): 300s, Full (12 agents): 600s
        timeout_map = {"single": 120, "minimal": 300, "full": 600}
        timeout = timeout_map.get(agent_mode, 120)
        
        # Set PYTHONPATH to include src directory
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
        
        # Run the CLI command
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        
        if result.returncode != 0:
            return jsonify({
                "error": "Assessment generation failed",
                "details": result.stderr,
            }), 500

        # Find the most recent assessment file
        if LIBRARY_DIR.exists():
            assessment_files = sorted(LIBRARY_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if assessment_files:
                latest_file = assessment_files[0]
                with open(latest_file, "r", encoding="utf-8") as f:
                    assessment_data = json.load(f)
                
                return jsonify({
                    "filename": latest_file.name,
                    "assessment": assessment_data,
                }), 201

        return jsonify({"error": "Assessment file not found after generation"}), 500
    
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Assessment generation timed out"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to create assessment: {str(e)}"}), 500


def run_api(host: str = "127.0.0.1", port: int = 5000, debug: bool = True) -> None:
    """Run the Flask API server."""
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_api()
