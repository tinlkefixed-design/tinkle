from __future__ import annotations

from uuid import UUID

from tinkle.reality_engine import ClaimStatus
from tinkle.research_graph import (
    EdgeCreate,
    GraphProvenance,
    NodeType,
    RelationshipType,
    ResearchGraph,
    ResearchGraphNode,
)
from tinkle.research_lab.schemas import (
    Comparison,
    ExecutionType,
    ExperimentResult,
    HumanMeasurement,
    Prediction,
    ResearchExperiment,
    ResearchHistoryEvent,
    ResearchHypothesis,
    ResearchQuestion,
    ResearchWorkflow,
)
from tinkle.simulation_engine import PhysicsLabEngine


class ResearchLab:
    """Auditable question-to-evidence workflow over existing simulation and graph systems."""

    def __init__(self, physics: PhysicsLabEngine | None = None, graph: ResearchGraph | None = None) -> None:
        self.graph = graph or (physics.graph if physics else ResearchGraph())
        self.physics = physics or PhysicsLabEngine(self.graph)
        self.workflows: dict[UUID, ResearchWorkflow] = {}

    def create_workflow(self, question: ResearchQuestion, hypothesis: ResearchHypothesis, experiment: ResearchExperiment | None = None, prediction: Prediction | None = None) -> ResearchWorkflow:
        if hypothesis.question_id != question.id:
            raise ValueError("Hypothesis must reference the research question")
        if experiment and (experiment.question_id != question.id or experiment.hypothesis_id != hypothesis.id):
            raise ValueError("Experiment references do not match workflow artifacts")
        workflow = ResearchWorkflow(question=question, hypothesis=hypothesis, experiment=experiment, prediction=prediction, limitations=["Workflow state is process-local; artifacts and provenance are represented in the Research Graph.", "Supported lifecycle updates are conservative and do not establish scientific truth."])
        workflow.history = [ResearchHistoryEvent(event="QUESTION_CREATED", artifact_id=question.id, state=question.epistemic_state.value), ResearchHistoryEvent(event="HYPOTHESIS_CREATED", artifact_id=hypothesis.id, state=hypothesis.lifecycle_state)]
        workflow.graph_node_ids = self._graph_question_hypothesis(workflow)
        self.workflows[question.id] = workflow
        return workflow

    def create_prediction(self, question_id: UUID, prediction: Prediction) -> Prediction:
        workflow = self._workflow(question_id)
        if prediction.hypothesis_id != workflow.hypothesis.id:
            raise ValueError("Prediction must reference the workflow hypothesis")
        workflow.prediction = prediction
        workflow.history.append(ResearchHistoryEvent(event="PREDICTION_CREATED", artifact_id=prediction.id, state=prediction.epistemic_state.value))
        prediction_node = self.graph.create_node(ResearchGraphNode(type=NodeType.RESULT, name=f"Prediction {prediction.id}", properties={"expected_output": prediction.expected_output, "expected_range": prediction.expected_range}, epistemic_state=prediction.epistemic_state, metadata={"artifact_id": str(prediction.id), "workflow_id": str(question_id)}, provenance=GraphProvenance(notes="Research prediction")))
        self._link(workflow, NodeType.HYPOTHESIS, workflow.hypothesis.id, NodeType.RESULT, prediction.id, RelationshipType.GENERATES, prediction.epistemic_state)
        workflow.graph_node_ids.append(str(prediction_node.id))
        return prediction

    def run_simulation(self, question_id: UUID) -> ExperimentResult:
        workflow = self._workflow(question_id)
        experiment = workflow.experiment
        if experiment is None or experiment.simulation_request is None or workflow.prediction is None:
            raise ValueError("A simulation experiment and prediction are required")
        simulation = self.physics.simulate(experiment.simulation_request)
        values = simulation.outputs[-1] if simulation.outputs else {}
        result = ExperimentResult(experiment_id=experiment.id, execution_type=ExecutionType.SIMULATION, values=values, simulation_id=simulation.simulation_id, epistemic_state=ClaimStatus.SIMULATED, provenance={"source": "PhysicsLabEngine", "simulation_id": str(simulation.simulation_id)})
        workflow.result = result
        workflow.experiment.execution_type = ExecutionType.SIMULATION
        workflow.history.append(ResearchHistoryEvent(event="SIMULATION_COMPLETED", artifact_id=result.id, state=result.epistemic_state.value, details={"simulation_id": str(simulation.simulation_id)}))
        experiment_node = self.graph.create_node(ResearchGraphNode(type=NodeType.EXPERIMENT, name=f"Experiment {experiment.id}", properties={"execution_type": experiment.execution_type.value}, epistemic_state=experiment.epistemic_state, metadata={"artifact_id": str(experiment.id), "workflow_id": str(question_id)}, provenance=GraphProvenance(notes="Research experiment")))
        result_node = self.graph.create_node(ResearchGraphNode(type=NodeType.RESULT, name=f"Result {result.id}", properties={"values": result.values}, epistemic_state=result.epistemic_state, metadata={"artifact_id": str(result.id), "workflow_id": str(question_id)}, provenance=GraphProvenance(notes="Simulation result")))
        workflow.graph_node_ids.extend([str(experiment_node.id), str(result_node.id)])
        self._link(workflow, NodeType.HYPOTHESIS, workflow.hypothesis.id, NodeType.EXPERIMENT, experiment.id, RelationshipType.TESTED_BY, ClaimStatus.UNVALIDATED)
        self._link(workflow, NodeType.EXPERIMENT, experiment.id, NodeType.RESULT, result.id, RelationshipType.PRODUCES, ClaimStatus.SIMULATED)
        return result

    def record_measurement(self, question_id: UUID, measurement: HumanMeasurement) -> HumanMeasurement:
        workflow = self._workflow(question_id)
        if workflow.experiment is None or measurement.experiment_id != workflow.experiment.id:
            raise ValueError("Measurement must reference the workflow experiment")
        if measurement.epistemic_state == ClaimStatus.MEASURED and (not measurement.source.strip() or not measurement.method.strip()):
            raise ValueError("MEASURED observations require explicit source and method provenance")
        workflow.measurements.append(measurement)
        workflow.history.append(ResearchHistoryEvent(event="HUMAN_MEASUREMENT_RECORDED", artifact_id=measurement.id, state=measurement.epistemic_state.value, details={"source": measurement.source, "method": measurement.method}))
        return measurement

    def compare(self, question_id: UUID, predicted_range: dict[str, tuple[float, float]] | None = None) -> Comparison:
        workflow = self._workflow(question_id)
        if workflow.prediction is None or workflow.result is None:
            raise ValueError("Prediction and result are required for comparison")
        result = workflow.result
        observed = result.values if result.execution_type == ExecutionType.SIMULATION else {item.variable: item.value for item in workflow.measurements}
        ranges = predicted_range or workflow.prediction.expected_range
        if not observed or not ranges:
            state = "INSUFFICIENT_DATA"
        else:
            deviation = {key: float(observed[key]) - ranges[key][0] for key in ranges if key in observed and isinstance(observed[key], (int, float))}
            state = "COMPATIBLE" if all(ranges[key][0] <= float(observed[key]) <= ranges[key][1] for key in ranges if key in observed) else "INCOMPATIBLE"
        deviation = {key: float(observed[key]) - sum(ranges[key]) / 2 for key in ranges if key in observed and isinstance(observed[key], (int, float))}
        comparison = Comparison(prediction_id=workflow.prediction.id, result_id=result.id, predicted_range=ranges, observed_or_simulated=observed, deviation=deviation, state=state, limitations=["Comparison is deterministic range membership; no statistical significance is claimed."], provenance={"result_state": result.epistemic_state.value})
        workflow.comparison = comparison
        workflow.history.append(ResearchHistoryEvent(event="PREDICTION_COMPARED", artifact_id=comparison.id, state=comparison.epistemic_state.value, details={"comparison_state": state}))
        return comparison

    def update_hypothesis(self, question_id: UUID) -> ResearchHypothesis:
        workflow = self._workflow(question_id)
        hypothesis = workflow.hypothesis
        comparison = workflow.comparison
        if comparison is None or comparison.state == "INSUFFICIENT_DATA":
            hypothesis.lifecycle_state = "REQUIRES_DATA"
        elif comparison.state == "COMPATIBLE":
            hypothesis.lifecycle_state = "SUPPORTED"
        else:
            hypothesis.lifecycle_state = "FALSIFIED" if hypothesis.falsification_criterion else "CONTRADICTED"
        workflow.history.append(ResearchHistoryEvent(event="HYPOTHESIS_UPDATED", artifact_id=hypothesis.id, state=hypothesis.lifecycle_state, details={"comparison_id": str(comparison.id) if comparison else None}))
        return hypothesis

    def history(self, question_id: UUID) -> list[ResearchHistoryEvent]:
        return list(self._workflow(question_id).history)

    def _workflow(self, question_id: UUID) -> ResearchWorkflow:
        try:
            return self.workflows[question_id]
        except KeyError as exc:
            raise KeyError(f"Research workflow not found: {question_id}") from exc

    def _graph_question_hypothesis(self, workflow: ResearchWorkflow) -> list[str]:
        question = self.graph.create_node(ResearchGraphNode(type=NodeType.RESEARCH_QUESTION, name=workflow.question.question, epistemic_state=workflow.question.epistemic_state, metadata={"artifact_id": str(workflow.question.id), "workflow_id": str(workflow.question.id)}, provenance=GraphProvenance(notes="Research workflow question")))
        hypothesis = self.graph.create_node(ResearchGraphNode(type=NodeType.HYPOTHESIS, name=workflow.hypothesis.statement, epistemic_state=workflow.hypothesis.epistemic_state, metadata={"artifact_id": str(workflow.hypothesis.id), "workflow_id": str(workflow.question.id)}, provenance=GraphProvenance(notes="Research workflow hypothesis")))
        self.graph.create_edge(EdgeCreate(source_id=question.id, target_id=hypothesis.id, relationship=RelationshipType.PROPOSES, epistemic_state=ClaimStatus.UNVALIDATED))
        return [str(question.id), str(hypothesis.id)]

    def _link(self, workflow: ResearchWorkflow, source_type: NodeType, source_artifact: UUID, target_type: NodeType, target_artifact: UUID, relationship: RelationshipType, state: ClaimStatus) -> None:
        source = self.graph.search_graph(__import__('tinkle.research_graph', fromlist=['GraphSearchRequest']).GraphSearchRequest(query=str(source_artifact), node_type=source_type))
        target = self.graph.search_graph(__import__('tinkle.research_graph', fromlist=['GraphSearchRequest']).GraphSearchRequest(query=str(target_artifact), node_type=target_type))
        if source and target:
            self.graph.create_edge(EdgeCreate(source_id=source[0].id, target_id=target[0].id, relationship=relationship, epistemic_state=state))
