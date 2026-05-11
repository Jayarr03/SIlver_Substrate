# SIlver_Substrate

Threat modeling down the rabbit hole below firmware and architecture.

Silver Substrate is a starter pipeline for an interactive tool that generates silicon-layer threats and security requirements for components below the software/firmware layer. Threats are categorized by SDLC phase and prioritized for the specific component so hardware teams can design in durable mitigations before devices are deployed and no longer practical to update.

## Supported hardware levels

- Architecture / RTL / Gates
- Transistors
- Source, Drain, Gate, Channel, Body
- Doped Regions / Wells / Junctions
- Oxides, Dielectrics, Isolation Structures
- Contacts, Vias, Metal Interconnects
- Passivation and Protective Layers
- Die, Bond Pads, Package, Substrate, Pins
- Wafer Material, Process Chemistry, Lithography, Doping, Etching

## How the pipeline works

1. Capture a `ComponentInput` with a name, hardware level, description, assets, assumptions, interfaces, process context, and priority drivers.
2. Look up a level profile that contains examples, threat lenses, and evidence prompts specific to that layer.
3. Compose a stable system prompt and level-specific user payload.
4. Add SDLC-phase guidance so threats and requirements are categorized by where they are introduced, discovered, or must be mitigated.
5. Add component-specific priority drivers such as protected assets, physical exposure, deployment lifetime, and update constraints.
6. Emphasize robust design-time controls for devices that cannot be patched or updated once deployed.
7. Send the request to the OpenAI Responses API with a strict JSON schema for structured output that includes field descriptions, priority scores, and ranked actions.
8. Normalize the model response into deployment assumptions, prioritized threats, prioritized security requirements, ranked actions, and open questions for the UI.

See [docs/pipeline.md](docs/pipeline.md) for the process pipeline and suggested UI flow.

## Usage

All assessments are automatically saved to the `library/` folder as timestamped JSON files (e.g., `library/gate_oxide_20260511_143022.json`). The library folder is excluded from version control.

### Web Interface (Recommended)

Run the full-stack web application:

**Terminal 1 - Start Backend API:**
```bash
./start-backend.sh
# Or manually: PYTHONPATH=src python -m silver_substrate.api
```

**Terminal 2 - Start Frontend:**
```bash
./start-frontend.sh
# Or manually: cd frontend && npm run dev
```

Then open http://localhost:5173 in your browser.

The web interface provides:
- **Interactive assessment creation** - Just enter a component name, get AI suggestions, and generate
- **Assessment library** - Browse all generated assessments
- **Detailed threat view** - View threats, requirements, and prioritized actions
- **Clean UI** - Easy to navigate and understand

### CLI: Interactive Mode

Simply provide the component name and let AI suggest the hardware level, description, assets, interfaces, and priority drivers:

```bash
PYTHONPATH=src python -m silver_substrate.cli --component "gate oxide"
```

The tool will:
1. Analyze the component name
2. Suggest appropriate metadata (level, description, assets, interfaces, priority drivers)
3. Show you the suggestions with rationale
4. Prompt you to confirm before proceeding with the assessment
5. Save the results to `library/gate_oxide_YYYYMMDD_HHMMSS.json`

### Manual Mode

Preview the request that would be sent to the model:

```bash
PYTHONPATH=src python -m silver_substrate.cli \
  --component "bond pad" \
  --level die_package_substrate_pins \
  --description "Debug-related pad in a wire-bonded package" \
  --asset "debug authorization state" \
  --interface "package bond wire" \
  --priority-driver "externally accessible debug-related pad" \
  --priority-driver "no field update path" \
  --build-request
```

Generate an assessment with explicit parameters:

```bash
cp .env.example .env
# Edit .env with your real OPENAI_API_KEY and OPENAI_MODEL.
PYTHONPATH=src python -m silver_substrate.cli \
  --component "gate oxide" \
  --level oxides_dielectrics_isolation \
  --description "Thin gate oxide in a security-critical transistor" \
  --priority-driver "protects root key material"
```

Customize the library output directory:

```bash
PYTHONPATH=src python -m silver_substrate.cli \
  --component "bond pad" \
  --library-dir "assessments/2026"
```

Secrets are loaded from `.env` by default, and `.env` is ignored by git. The model is intentionally provided through `OPENAI_MODEL` in `.env` or `--model` so the application can choose the deployed model explicitly rather than baking in a stale default.

## Development

Install backend dependencies:

```bash
python -m pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

Run the tests:

```bash
python -m pytest
```
