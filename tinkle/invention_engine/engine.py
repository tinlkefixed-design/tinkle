from __future__ import annotations

from itertools import product

from tinkle.hypothesis_universe import HypothesisRequest, HypothesisUniverse
from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph import (
    EdgeCreate,
    NodeType,
    RelationshipType,
    ResearchGraph,
    ResearchGraphNode,
)
from tinkle.scientific_core.domain_classifier import DomainClassifier

from .schemas import (
    Architecture,
    Constraint,
    DesignGenome,
    DesignObjective,
    ExperimentRequirement,
    FailureMode,
    FeasibilityAssessment,
    FeasibilityStatus,
    FictionalFunctionTranslation,
    FunctionalRequirement,
    Invention,
    InventionAnalysis,
    InventionGoal,
    InventionHypothesis,
    InventionRequest,
    InventionResult,
    Mechanism,
    NoveltyClass,
    PerformanceTarget,
    PhysicalPrinciple,
    SimulationRequirement,
    Tradeoff,
    ValidationRequirement,
)


class InventionGenerationEngine:
    """Deterministic design-space generator. It generates candidates; it never claims novelty as fact."""
    def __init__(self, graph: ResearchGraph | None = None) -> None:
        self.graph = graph or ResearchGraph()
        self.analyses: dict[str, InventionAnalysis] = {}

    def generate(self, req: InventionRequest) -> InventionResult:
        architectures=req.architectures or ['modular_system']
        mechanisms=req.mechanisms or ['direct_conversion']
        materials=req.materials or ['unspecified_material']
        processes=req.processes or ['standard_manufacturing']
        algorithms=req.algorithms or [None]
        space=len(architectures)*len(mechanisms)*len(materials)*len(processes)*len(algorithms)
        candidates=[]
        seen=set()
        for a,m,mat,proc,algo in product(architectures,mechanisms,materials,processes,algorithms):
            key=(a.strip().lower(),m.strip().lower(),mat.strip().lower(),proc.strip().lower(),str(algo).strip().lower())
            if key in seen: continue
            seen.add(key)
            novelty=self._novelty(a,m,mat,proc,algo,req.known_designs)
            genome=DesignGenome(architecture=a,materials=[mat],mechanisms=[m],parameters={},energy_flow=[m],control=[algo] if algo else [],geometry=[a],interfaces=[a])
            candidates.append(Invention(title=f'{a} + {m}',problem=req.problem,architecture=a,mechanism=m,materials=[mat],process=proc,algorithm=algo,genome=genome,novelty=novelty,novelty_rationale=['Novelty class is a search classification, not a patentability determination.', f'Compared against {len(req.known_designs)} caller-supplied known designs.'],assumptions=req.constraints,status='CANDIDATE',provenance={'generator':'InventionGenerationEngine','source':'CALCULATED'}))
            if len(candidates)>=req.max_candidates: break
        return InventionResult(problem=req.problem,candidates=candidates,search_space_size=space,generated_count=len(candidates),limitations=['Candidates are generated from caller-supplied design primitives.','No candidate is asserted to be scientifically valid, novel in the world, or patentable.','Real engineering feasibility requires constraints, simulation, prior-art review and validation.'])

    def analyze_invention_goal(self, req: InventionRequest) -> InventionAnalysis:
        text = ' '.join(req.problem.split())
        lower = text.casefold()
        primary = self._primary_function(text)
        functions = [primary, *self._subfunctions(lower)]
        domains = DomainClassifier().classify(text)
        requirements = self._requirements(text, lower)
        constraints = [Constraint(name=value, epistemic_state=ClaimStatus.UNKNOWN) for value in req.constraints]
        if not constraints:
            constraints = [Constraint(name='operating constraints', epistemic_state=ClaimStatus.UNKNOWN)]
        principles = self._principles(lower)
        mechanisms = self._mechanisms(primary, lower, domains)
        architectures = [Architecture(name=f'{mechanism.name} architecture', description=f'Candidate architecture centered on {mechanism.name}.', mechanism_names=[mechanism.name], component_names=['actuator', 'controller'], epistemic_state=ClaimStatus.UNVALIDATED) for mechanism in mechanisms]
        generated = self.generate(InventionRequest(problem=text, mechanisms=[item.name for item in mechanisms], constraints=req.constraints, max_candidates=req.max_candidates))
        candidates = generated.candidates
        tradeoffs = self._tradeoffs(candidates)
        failures = self._failures(candidates, requirements)
        feasibility = [self._feasibility(item, constraints, req.constraints) for item in candidates]
        hypotheses = [InventionHypothesis(statement=f'If the declared constraints are satisfied, {item.title} may perform {primary}.', predicted_outcome=f'{item.title} meets the functional requirements.', assumptions=req.constraints, unknowns=[constraint.name for constraint in constraints if constraint.epistemic_state == ClaimStatus.UNKNOWN], validation_requirement='Define and execute controlled verification against each critical requirement.') for item in candidates]
        hypothesis_result = HypothesisUniverse().run(HypothesisRequest(question=text, hypotheses=[item.statement for item in hypotheses], retest=False))
        validation = [ValidationRequirement(description=f'Verify {requirement.identifier}: {requirement.description}', acceptance_measure='Caller must define a measurable acceptance value before validation.') for requirement in requirements]
        simulations = [SimulationRequirement(description='Model the candidate mechanism under declared loads and boundary conditions.', parameters=['geometry', 'load', 'power', 'material properties'], outputs=['response', 'efficiency', 'temperature'])]
        experiments = [ExperimentRequirement(description='Plan a controlled test for the selected candidate after digital review.', measurements=['force', 'motion', 'power', 'temperature'])]
        gaps = [constraint.name for constraint in constraints if constraint.epistemic_state == ClaimStatus.UNKNOWN]
        gaps.extend(requirement.identifier for requirement in requirements if requirement.target is None)
        analysis = InventionAnalysis(
            goal=InventionGoal(text=text, primary_function=primary, epistemic_state=ClaimStatus.UNVALIDATED),
            functions=functions, requirements=requirements, constraints=constraints,
            performance_targets=[PerformanceTarget(metric=item.identifier, target=item.target, units=item.units, epistemic_state=ClaimStatus.UNKNOWN) for item in requirements],
            objectives=[DesignObjective(name='performance'), DesignObjective(name='mass'), DesignObjective(name='safety')],
            domains=domains, principles=principles, mechanisms=mechanisms, architectures=architectures,
            candidates=candidates, tradeoffs=tradeoffs, failures=failures, feasibility=feasibility,
            hypotheses=hypotheses, validation=validation, simulations=simulations, experiments=experiments,
            hypothesis_lifecycle=hypothesis_result.lifecycle,
            research_gaps=sorted(set(gaps)), limitations=generated.limitations + ['This analysis generates candidates and planning artifacts; it does not prove feasibility, novelty, safety, or experimental performance.'],
        )
        analysis.graph_node_ids = self._build_graph(analysis)
        self.analyses[str(analysis.id)] = analysis
        return analysis

    @staticmethod
    def translate_fictional_function(capability: str) -> FictionalFunctionTranslation:
        text = ' '.join(capability.split())
        return FictionalFunctionTranslation(
            fictional_capability=text,
            real_world_function='Translate the described capability into measurable force, motion, energy, control, and safety requirements.',
            physical_requirements=['Define load, range, speed, energy input, attachment, and environmental limits.'],
            candidate_mechanisms=['Actuator and transmission system', 'Anchoring or structural interface', 'Feedback and safety control'],
            limitations=['The fictional capability is not treated as real technology.', 'No physical feasibility, material property, or performance result is asserted.'],
            epistemic_state=ClaimStatus.UNVALIDATED,
        )

    @staticmethod
    def _primary_function(text: str) -> str:
        return text.rstrip('.').strip() or 'Unspecified function'

    @staticmethod
    def _subfunctions(lower: str) -> list[str]:
        functions = ['provide controlled assistance', 'sense system state', 'control output']
        if any(term in lower for term in ('wearable', 'human', 'arm', 'exosuit')):
            functions.insert(1, 'interface safely with a human operator')
        return functions

    @staticmethod
    def _requirements(text: str, lower: str) -> list[FunctionalRequirement]:
        return [
            FunctionalRequirement(identifier='FR-1', description=f'Perform the requested function: {text}', priority=5, epistemic_state=ClaimStatus.UNVALIDATED, confidence=0.5, assumptions=['Requirement inferred from natural-language goal.']),
            FunctionalRequirement(identifier='FR-2', description='Maintain controllable and observable operation.', priority=5, epistemic_state=ClaimStatus.UNVALIDATED, confidence=0.4),
            FunctionalRequirement(identifier='FR-3', description='Define mass, size, power, environment, and safety limits.', priority=5, epistemic_state=ClaimStatus.UNKNOWN, confidence=0.0),
        ]

    @staticmethod
    def _principles(lower: str) -> list[PhysicalPrinciple]:
        names = [('Newtonian mechanics', 'Relates applied force, mass, and acceleration.'), ('Feedback control', 'Provides a candidate basis for controlled response.')]
        if any(term in lower for term in ('battery', 'energy', 'power')):
            names.append(('Energy conversion', 'Frames energy input and output requirements.'))
        return [PhysicalPrinciple(name=name, relevance=relevance, epistemic_state=ClaimStatus.UNVALIDATED, confidence=0.0) for name, relevance in names]

    @staticmethod
    def _mechanisms(primary: str, lower: str, domains: list[str]) -> list[Mechanism]:
        names = ['electric motor + screw', 'pneumatic actuator', 'series elastic actuator'] if any(term in lower for term in ('move', 'motion', 'assist', 'force', 'arm', 'wearable')) else ['direct mechanical transmission', 'electromagnetic actuator']
        return [Mechanism(name=name, function=primary, principle='Candidate physical principle requiring verification', advantages=['Known mechanism category to investigate.'], disadvantages=['Sizing, efficiency, safety, and manufacturability are unresolved.'], requirements=['Define load, stroke, speed, and duty cycle.'], limitations=['No material property or performance value is asserted.'], domains=domains, materials=['UNSPECIFIED'], epistemic_state=ClaimStatus.UNVALIDATED) for name in names]

    @staticmethod
    def _tradeoffs(candidates: list[Invention]) -> list[Tradeoff]:
        if not candidates:
            return []
        return [Tradeoff(objective_a='mass', objective_b='performance', tension='Higher performance may require additional structure or energy capacity.', affected_concepts=[item.title for item in candidates]), Tradeoff(objective_a='compactness', objective_b='thermal margin', tension='Reduced volume may constrain cooling and serviceability.', affected_concepts=[item.title for item in candidates])]

    @staticmethod
    def _failures(candidates: list[Invention], requirements: list[FunctionalRequirement]) -> list[FailureMode]:
        return [FailureMode(description='Loss of controlled output', cause='Actuator, sensor, power, or controller fault', affected_component='actuator/controller', affected_requirement=requirements[0].identifier if requirements else 'UNKNOWN', mitigation='Define fail-safe behavior and verify bounded response.', epistemic_state=ClaimStatus.UNKNOWN) for _ in candidates[:3]]

    @staticmethod
    def _feasibility(candidate: Invention, constraints: list[Constraint], declared: list[str]) -> FeasibilityAssessment:
        if not declared:
            return FeasibilityAssessment(status=FeasibilityStatus.UNCERTAIN, reasons=['A candidate mechanism category exists, but constraints and target values are not supplied.'], limiting_factors=['Unknown requirements and material properties.'], unknowns=[item.name for item in constraints])
        return FeasibilityAssessment(status=FeasibilityStatus.CONDITIONALLY_FEASIBLE, reasons=['The candidate is an engineering investigation target, not a validated design.'], limiting_factors=['Declared constraints require independent analysis and testing.'], unknowns=[item.name for item in constraints if item.epistemic_state == ClaimStatus.UNKNOWN])

    def _build_graph(self, analysis: InventionAnalysis) -> list[str]:
        ids: list[str] = []
        def add(node_type: NodeType, name: str, state: ClaimStatus, description: str = '') -> ResearchGraphNode:
            node = self.graph.create_node(ResearchGraphNode(type=node_type, name=name, description=description, epistemic_state=state, metadata={'invention_analysis_id': str(analysis.id)}))
            ids.append(str(node.id))
            return node
        goal = add(NodeType.RESEARCH_PROJECT, analysis.goal.text, analysis.goal.epistemic_state)
        for requirement in analysis.requirements:
            req_node = add(NodeType.VARIABLE, requirement.identifier, requirement.epistemic_state, requirement.description)
            self.graph.create_edge(EdgeCreate(source_id=goal.id, target_id=req_node.id, relationship=RelationshipType.REQUIRES, epistemic_state=ClaimStatus.UNVALIDATED))
        for principle in analysis.principles:
            principle_node = add(NodeType.PRINCIPLE, principle.name, principle.epistemic_state, principle.relevance)
            self.graph.create_edge(EdgeCreate(source_id=goal.id, target_id=principle_node.id, relationship=RelationshipType.RELATED_TO, epistemic_state=ClaimStatus.UNVALIDATED))
        for mechanism in analysis.mechanisms:
            mechanism_node = add(NodeType.TECHNOLOGY, mechanism.name, mechanism.epistemic_state, mechanism.function)
            self.graph.create_edge(EdgeCreate(source_id=goal.id, target_id=mechanism_node.id, relationship=RelationshipType.GENERATES, epistemic_state=ClaimStatus.UNVALIDATED))
        for candidate in analysis.candidates:
            candidate_node = add(NodeType.DESIGN, candidate.title, ClaimStatus.UNVALIDATED, candidate.problem)
            self.graph.create_edge(EdgeCreate(source_id=goal.id, target_id=candidate_node.id, relationship=RelationshipType.GENERATES, epistemic_state=ClaimStatus.UNVALIDATED))
        for architecture in analysis.architectures:
            architecture_node = add(NodeType.DESIGN, architecture.name, architecture.epistemic_state, architecture.description)
            self.graph.create_edge(EdgeCreate(source_id=goal.id, target_id=architecture_node.id, relationship=RelationshipType.PART_OF, epistemic_state=ClaimStatus.UNVALIDATED))
        for failure in analysis.failures:
            failure_node = add(NodeType.FAILURE, failure.description, failure.epistemic_state, failure.cause)
            self.graph.create_edge(EdgeCreate(source_id=goal.id, target_id=failure_node.id, relationship=RelationshipType.FAILS_UNDER, epistemic_state=ClaimStatus.UNKNOWN))
        for tradeoff in analysis.tradeoffs:
            tradeoff_node = add(NodeType.UNKNOWN, f'{tradeoff.objective_a} vs {tradeoff.objective_b}', tradeoff.epistemic_state, tradeoff.tension)
            self.graph.create_edge(EdgeCreate(source_id=goal.id, target_id=tradeoff_node.id, relationship=RelationshipType.CONSTRAINS, epistemic_state=ClaimStatus.ESTIMATED))
        for hypothesis in analysis.hypotheses:
            hypothesis_node = add(NodeType.HYPOTHESIS, hypothesis.statement, hypothesis.epistemic_state, hypothesis.predicted_outcome)
            self.graph.create_edge(EdgeCreate(source_id=goal.id, target_id=hypothesis_node.id, relationship=RelationshipType.GENERATES, epistemic_state=ClaimStatus.UNVALIDATED))
        for requirement in [*analysis.validation, *analysis.simulations, *analysis.experiments]:
            item_node = add(NodeType.EXPERIMENT if requirement in analysis.experiments else NodeType.SIMULATION if requirement in analysis.simulations else NodeType.EXPERIMENT, requirement.description, requirement.epistemic_state)
            self.graph.create_edge(EdgeCreate(source_id=goal.id, target_id=item_node.id, relationship=RelationshipType.REQUIRES, epistemic_state=ClaimStatus.UNVALIDATED))
        return ids

    def get_analysis(self, analysis_id: str) -> InventionAnalysis:
        try:
            return self.analyses[analysis_id]
        except KeyError as exc:
            raise KeyError(f'Invention analysis not found: {analysis_id}') from exc

    def _novelty(self,a,m,mat,p,algo,known):
        text=' '.join([a,m,mat,p,str(algo)]).lower()
        exact=[x.lower() for x in known]
        if any(text==x or (a.lower() in x and m.lower() in x and mat.lower() in x) for x in exact): return NoveltyClass.KNOWN
        if any(a.lower() in x for x in exact): return NoveltyClass.IMPROVEMENT
        if len({a.lower(),m.lower(),mat.lower(),p.lower()})>=3: return NoveltyClass.COMBINATION
        return NoveltyClass.NOVEL_CANDIDATE
