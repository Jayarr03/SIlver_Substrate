# Threat Generation Pipeline

Silver Substrate feeds a hardware component into a repeatable pipeline before calling an LLM. The goal is to keep prompts grounded at the correct layer below software/firmware and return structured JSON threats plus security requirements categorized by SDLC phase and prioritized for the supplied component.

## Pipeline stages

1. **Component intake**: capture the component name, hardware level, description, protected assets, assumptions, interfaces, process context, and priority drivers.
2. **Level profiling**: map the hardware level to examples, threat lenses, and evidence that should be collected for that layer.
3. **SDLC categorization**: provide lifecycle phases from requirements through end of life so threats and mitigations are tagged to the phase where they must be addressed.
4. **Component prioritization**: score each threat and requirement using impact, exploitability, exposure, design lock-in, remediation difficulty, update constraints, and user-supplied priority drivers.
5. **Prompt composition**: combine a stable system prompt with level-specific, SDLC-specific, and prioritization guidance. The prompt assumes many devices cannot be updated after deployment and asks for robust design-time controls.
6. **Structured model request**: call the OpenAI Responses API with a described JSON schema so the output is predictable for the UI.
7. **Normalization**: parse the JSON into `ComponentAssessment`, `Threat`, and `SecurityRequirement` objects, preserving SDLC phase metadata.
8. **UI/API handoff**: render threats, SDLC categories, deployment consequences, linked mitigations, verification methods, owners, priorities, and open questions.

## Suggested UI flow

- Let a user select one of the supported hardware levels.
- Ask for the component name and a short description.
- Prompt for assets, assumptions, interfaces, process context, and priority drivers as optional chips or repeatable fields.
- Offer a preview mode that shows the composed request before an API call.
- Load local API secrets from `.env` and keep the real file out of version control.
- Display generated threats next to requirements so reviewers can trace each mitigation back to a threat, SDLC phase, priority score, and ranked next action.

## OpenAI integration notes

The implementation uses the Responses API request shape and structured JSON output. OpenAI's documentation recommends Structured Outputs when an application needs schema adherence rather than merely valid JSON, and the Responses API accepts text input and can return JSON outputs. Local API credentials and model selection are read from `.env` by default through `OPENAI_API_KEY` and `OPENAI_MODEL`. The schema includes descriptions for each output field, including SDLC phase, deployment consequence, priority score/rationale, ranked action, and design robustness, to keep downstream JSON consumers self-describing.


## Priority scoring

Each generated threat and security requirement includes a qualitative priority (`low`, `medium`, `high`, or `critical`), a numeric `priority_score` from 1 to 100, and a `priority_rationale`. The model is instructed to score priorities for the supplied component using protected asset criticality, physical/electrical exposure, exploitability, potential impact, SDLC phase urgency, design lock-in, post-deployment remediation difficulty, and any user-provided priority drivers. The final JSON also includes `prioritized_actions`, a ranked list that combines the highest-priority threats and requirements into concrete next steps.
