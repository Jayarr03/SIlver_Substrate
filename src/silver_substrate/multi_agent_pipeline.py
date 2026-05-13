"""Multi-agent threat generation pipeline for hardware components."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .hierarchy import HardwareLevel
from .lifecycle import SdlcPhase
from .models import (
    AttackerModel,
    ComponentAssessment,
    ComponentInput,
    ComponentScope,
    Countermeasure,
    CriticFinding,
    FailureMechanism,
    LifecycleRisk,
    ManufacturingRisk,
    OpenQuestion,
    PrioritizedAction,
    PrioritizedItem,
    QualityScore,
    SecurityRequirement,
    Threat,
    ThreatScenario,
    VerificationPlanItem,
    ImplementationSummary,
)
from .openai_client import AssessmentClient
from .orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MultiAgentPipeline:
    """Multi-agent pipeline for in-depth hardware threat modeling."""

    client: AssessmentClient
    agent_mode: str = "minimal"  # 'minimal' or 'full'
    model: str | None = None

    def run(self, component: ComponentInput) -> ComponentAssessment:
        """Generate enhanced assessment using multi-agent pipeline.
        
        Args:
            component: Component to analyze
            
        Returns:
            Enhanced ComponentAssessment with multi-agent insights
        """
        logger.info(f"Running {self.agent_mode} multi-agent pipeline for {component.name}")
        
        # Execute agent pipeline
        orchestrator = AgentOrchestrator(
            client=self.client,
            agent_mode=self.agent_mode,
            model=self.model,
        )
        
        agent_outputs, execution_results = orchestrator.execute_pipeline(component)
        
        # Transform agent outputs into ComponentAssessment
        assessment = self._build_assessment(component, agent_outputs)
        
        # Log any failed agents
        failed_agents = orchestrator.get_failed_agents(execution_results)
        if failed_agents:
            logger.warning(f"Agents failed: {', '.join(failed_agents)}")
        
        return assessment
    
    def _build_assessment(
        self,
        component: ComponentInput,
        agent_outputs: dict[str, Any],
    ) -> ComponentAssessment:
        """Build ComponentAssessment from agent outputs.
        
        Args:
            component: Original component input
            agent_outputs: Dictionary mapping agent names to their outputs
            
        Returns:
            Complete ComponentAssessment with all fields populated
        """
        # Extract outputs from each agent
        decomp = agent_outputs.get("ComponentDecomposition", {})
        physics = agent_outputs.get("DevicePhysics", {})
        adversarial = agent_outputs.get("AdversarialThreat", {})
        reliability = agent_outputs.get("ReliabilityLifecycle", {})
        manufacturing = agent_outputs.get("ManufacturingSupplyChain", {})
        countermeasures_data = agent_outputs.get("CountermeasureDesign", {})
        requirements = agent_outputs.get("SecurityRequirements", {})
        verification = agent_outputs.get("VerificationValidation", {})
        questions = agent_outputs.get("QuestionGeneration", {})
        prioritization = agent_outputs.get("Prioritization", {})
        critic = agent_outputs.get("QualityCritic", {})
        summarizer = agent_outputs.get("ExecutiveSummarizer", {})
        
        # Build scope from decomposition agent
        scope = None
        if decomp:
            scope = ComponentScope(
                component_definition=decomp.get("component_definition", ""),
                component_boundaries=decomp.get("component_boundaries", ""),
                parent_components=tuple(decomp.get("parent_components", [])),
                child_or_sub_components=tuple(decomp.get("child_or_sub_components", [])),
                adjacent_components=tuple(decomp.get("adjacent_components", [])),
                normal_operating_conditions=tuple(decomp.get("normal_operating_conditions", [])),
                out_of_scope_items=tuple(decomp.get("out_of_scope_items", [])),
            )
        
        # Build failure mechanisms from physics agent
        failure_mechanisms_raw = physics.get("failure_mechanisms", []) if physics else []
        failure_mechanisms = tuple(
            FailureMechanism(
                name=fm.get("name", "") if isinstance(fm, dict) else "",
                mechanism=fm.get("mechanism", "") if isinstance(fm, dict) else "",
                trigger_conditions=tuple(fm.get("trigger_conditions", [])) if isinstance(fm, dict) else (),
                observable_effects=tuple(fm.get("observable_effects", [])) if isinstance(fm, dict) else (),
                permanence=fm.get("permanence", "unknown") if isinstance(fm, dict) else "unknown",
                security_relevance=fm.get("security_relevance", "") if isinstance(fm, dict) else "",
            )
            for fm in failure_mechanisms_raw
            if isinstance(fm, dict)
        )
        
        # Build attacker model and threat scenarios from adversarial agent
        attacker_model = None
        threat_scenarios = ()
        if adversarial:
            attacker_caps = tuple(adversarial.get("attacker_models", []))
            attacker_model = AttackerModel(
                attacker_capabilities=attacker_caps,
                excluded_capabilities=(),  # Not in current schema but placeholder
                environmental_influences=(),  # Not in current schema but placeholder
            )
            
            threat_scenarios_raw = adversarial.get("threat_scenarios", [])
            threat_scenarios = tuple(
                ThreatScenario(
                    title=ts.get("title", "") if isinstance(ts, dict) else "",
                    attacker_capability=ts.get("attacker_capability", "") if isinstance(ts, dict) else "",
                    attack_path=ts.get("attack_path", "") if isinstance(ts, dict) else "",
                    physical_mechanism=ts.get("physical_mechanism", "") if isinstance(ts, dict) else "",
                    security_impact=ts.get("security_impact", "") if isinstance(ts, dict) else "",
                    preconditions=tuple(ts.get("preconditions", [])) if isinstance(ts, dict) else (),
                    confidence=ts.get("confidence", "medium") if isinstance(ts, dict) else "medium",
                )
                for ts in threat_scenarios_raw
                if isinstance(ts, dict)
            )
        
        # Build lifecycle risks from reliability agent
        lifecycle_risks_raw = reliability.get("lifecycle_risks", []) if reliability else []
        lifecycle_risks = tuple(
            LifecycleRisk(
                risk=lr.get("risk", "") if isinstance(lr, dict) else "",
                lifecycle_stage=lr.get("lifecycle_stage", "") if isinstance(lr, dict) else "",
                accelerating_conditions=tuple(lr.get("accelerating_conditions", [])) if isinstance(lr, dict) else (),
                impact=lr.get("impact", "") if isinstance(lr, dict) else "",
                recommended_controls=tuple(lr.get("recommended_controls", [])) if isinstance(lr, dict) else (),
            )
            for lr in lifecycle_risks_raw
            if isinstance(lr, dict)
        )
        
        # Build manufacturing risk from manufacturing agent
        manufacturing_risk = None
        if manufacturing:
            manufacturing_risk = ManufacturingRisk(
                manufacturing_risks=tuple(manufacturing.get("manufacturing_risks", [])),
                supply_chain_risks=tuple(manufacturing.get("supply_chain_risks", [])),
                process_controls=tuple(manufacturing.get("process_controls", [])),
                required_evidence=tuple(manufacturing.get("required_evidence", [])),
                open_supplier_questions=tuple(manufacturing.get("open_supplier_questions", [])),
            )
        
        # Build countermeasures
        countermeasures_raw = countermeasures_data.get("countermeasures", []) if countermeasures_data else []
        countermeasures = tuple(
            Countermeasure(
                title=cm.get("title", "") if isinstance(cm, dict) else "",
                type=cm.get("type", "preventive") if isinstance(cm, dict) else "preventive",
                description=cm.get("description", "") if isinstance(cm, dict) else "",
                implementation_layer=cm.get("implementation_layer", "") if isinstance(cm, dict) else "",
                mitigates=tuple(cm.get("mitigates", [])) if isinstance(cm, dict) else (),
                owner=cm.get("owner", "") if isinstance(cm, dict) else "",
                residual_risk=cm.get("residual_risk", "") if isinstance(cm, dict) else "",
            )
            for cm in countermeasures_raw
            if isinstance(cm, dict)
        )
        
        # Build security requirements (maintaining legacy format for compatibility)
        security_requirements_raw = requirements.get("security_requirements", []) if requirements else []
        security_requirements_list = tuple(
            SecurityRequirement(
                title=req.get("title", "") if isinstance(req, dict) else "",
                description="",  # Not in new schema
                sdlc_phase=SdlcPhase.REQUIREMENTS,  # Default
                requirement=req.get("requirement", "") if isinstance(req, dict) else "",
                mitigates=tuple(req.get("mitigates", [])) if isinstance(req, dict) else (),
                verification_method=req.get("verification_method", "") if isinstance(req, dict) else "",
                owner=req.get("owner", "") if isinstance(req, dict) else "",
                design_robustness="",  # Not in new schema
                priority=req.get("priority", "medium") if isinstance(req, dict) else "medium",
                priority_score=50,  # Default
                priority_rationale="",
            )
            for req in security_requirements_raw
            if isinstance(req, dict)
        )
        
        # Build verification plan
        verification_plan_raw = verification.get("verification_plan", []) if verification else []
        verification_plan = tuple(
            VerificationPlanItem(
                control_or_requirement=vp.get("control_or_requirement", "") if isinstance(vp, dict) else "",
                test_method=vp.get("test_method", "") if isinstance(vp, dict) else "",
                evidence_required=vp.get("evidence_required", "") if isinstance(vp, dict) else "",
                acceptance_criteria=vp.get("acceptance_criteria", "") if isinstance(vp, dict) else "",
                test_stage=vp.get("test_stage", "post-silicon") if isinstance(vp, dict) else "post-silicon",
            )
            for vp in verification_plan_raw
            if isinstance(vp, dict)
        )
        
        # Build open questions
        open_questions_raw = questions.get("open_questions", []) if questions else []
        open_questions_detailed = tuple(
            OpenQuestion(
                question=q.get("question", "") if isinstance(q, dict) else str(q),
                asked_of=q.get("asked_of", "") if isinstance(q, dict) else "Unknown",
                why_it_matters=q.get("why_it_matters", "") if isinstance(q, dict) else "",
                blocks=tuple(q.get("blocks", [])) if isinstance(q, dict) else (),
                priority=q.get("priority", "medium") if isinstance(q, dict) else "medium",
            )
            for q in open_questions_raw
        )
        
        # Build prioritized items
        prioritized_items_raw = prioritization.get("prioritized_items", []) if prioritization else []
        prioritized_items = tuple(
            PrioritizedItem(
                item_title=pi.get("item_title", "") if isinstance(pi, dict) else "",
                item_type=pi.get("item_type", "") if isinstance(pi, dict) else "",
                impact=pi.get("impact", 5) if isinstance(pi, dict) else 5,
                exploitability=pi.get("exploitability", 5) if isinstance(pi, dict) else 5,
                permanence=pi.get("permanence", 5) if isinstance(pi, dict) else 5,
                detectability=pi.get("detectability", 5) if isinstance(pi, dict) else 5,
                lifecycle_lock_in=pi.get("lifecycle_lock_in", 5) if isinstance(pi, dict) else 5,
                confidence=pi.get("confidence", 5) if isinstance(pi, dict) else 5,
                total_score=pi.get("total_score", 30) if isinstance(pi, dict) else 30,
                priority=pi.get("priority", "medium") if isinstance(pi, dict) else "medium",
                rationale=pi.get("rationale", "") if isinstance(pi, dict) else "",
            )
            for pi in prioritized_items_raw
            if isinstance(pi, dict)
        )
        
        # Build critic findings and quality score
        critic_findings_raw = critic.get("review_findings", []) if critic else []
        critic_findings = tuple(
            CriticFinding(
                finding=cf.get("finding", "") if isinstance(cf, dict) else "",
                severity=cf.get("severity", "medium") if isinstance(cf, dict) else "medium",
                evidence=cf.get("evidence", "") if isinstance(cf, dict) else "",
                recommended_fix=cf.get("recommended_fix", "") if isinstance(cf, dict) else "",
            )
            for cf in critic_findings_raw
            if isinstance(cf, dict)
        )
        
        quality_score = None
        if "quality_score" in critic:
            qs = critic["quality_score"]
            quality_score = QualityScore(
                technical_accuracy=qs.get("technical_accuracy", 0),
                security_framing=qs.get("security_framing", 0),
                actionability=qs.get("actionability", 0),
                testability=qs.get("testability", 0),
                prioritization_quality=qs.get("prioritization_quality", 0),
            )
        
        # Build implementation summary
        implementation_summary = None
        if summarizer:
            implementation_summary = ImplementationSummary(
                executive_summary=summarizer.get("executive_summary", ""),
                top_threats=tuple(summarizer.get("top_threats", [])),
                top_recommendations=tuple(summarizer.get("top_recommendations", [])),
                implementation_plan=tuple(summarizer.get("implementation_plan", [])),
                decision_points=tuple(summarizer.get("decision_points", [])),
                residual_risks=tuple(summarizer.get("residual_risks", [])),
            )
        
        # Build legacy threats from threat scenarios (for compatibility)
        threats = tuple(
            Threat(
                title=ts.title,
                description=f"{ts.attack_path} via {ts.physical_mechanism}",
                sdlc_phase=SdlcPhase.IMPLEMENTATION,  # Default
                sdlc_phase_description="Threat identified during multi-agent analysis",
                scenario=ts.attack_path,
                attack_surface=ts.physical_mechanism,
                preconditions=ts.preconditions,
                potential_impact=ts.security_impact,
                deployment_consequence="Requires design-time mitigation",
                priority="high" if ts.confidence == "high" else "medium",
                priority_score=80 if ts.confidence == "high" else 50,
                priority_rationale=f"Based on {ts.attacker_capability} capability",
                confidence=ts.confidence,
            )
            for ts in threat_scenarios
        )
        
        # Build legacy prioritized actions from prioritized items
        prioritized_actions = tuple(
            PrioritizedAction(
                rank=idx + 1,
                action_type=pi.item_type,
                title=pi.item_title,
                priority=pi.priority,
                priority_score=pi.total_score,
                rationale=pi.rationale,
                next_step="Review and implement",
            )
            for idx, pi in enumerate(prioritized_items[:10])  # Top 10
        )
        
        # Build summary and deployment assumptions
        summary = scope.component_definition if scope else f"Multi-agent analysis of {component.name}"
        deployment_assumptions = (
            "Multi-agent analysis includes device physics, adversarial threats, "
            "lifecycle risks, and manufacturing considerations"
        )
        
        # Use implementation summary if available, otherwise generate
        if implementation_summary:
            summary = implementation_summary.executive_summary[:500]  # Truncate for summary field
        
        # Legacy open questions as simple strings
        open_questions_simple = tuple(q.question for q in open_questions_detailed)
        
        return ComponentAssessment(
            component_name=component.name,
            level=component.level,
            summary=summary,
            deployment_assumptions=deployment_assumptions,
            prioritization_summary="Multi-dimensional scoring across 6 criteria",
            threats=threats,
            security_requirements=security_requirements_list,
            prioritized_actions=prioritized_actions,
            open_questions=open_questions_simple,
            # Multi-agent fields
            agent_mode=self.agent_mode,
            scope=scope,
            failure_mechanisms=failure_mechanisms,
            attacker_model=attacker_model,
            threat_scenarios=threat_scenarios,
            lifecycle_risks=lifecycle_risks,
            manufacturing_risk=manufacturing_risk,
            countermeasures=countermeasures,
            verification_plan=verification_plan,
            open_questions_detailed=open_questions_detailed,
            prioritized_items=prioritized_items,
            critic_findings=critic_findings,
            quality_score=quality_score,
            implementation_summary=implementation_summary,
        )
