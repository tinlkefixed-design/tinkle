from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tinkle.api.main import app
from tinkle.engineering_decision import EngineeringDecisionEngine
from tinkle.experiment_planning import (
    ExperimentalVariable,
    ExperimentObjective,
    ExperimentPlanningEngine,
    ExperimentPlanRequest,
    MeasurementSpecification,
    Prediction,
    ResearchObjective,
    VariableRole,
)
from tinkle.experiment_results import (
    ComparisonStatus,
    ExperimentResult,
    ExperimentResultsEngine,
    Observation,
    ResultQuality,
)
from tinkle.reality_engine import ClaimStatus


def setup():
    planner=ExperimentPlanningEngine(decisions=EngineeringDecisionEngine())
    research=planner.create_research_objective(ResearchObjective(title='test',description='test',hypothesis_ids=['H1']))
    objective=planner.create_experiment_objective(ExperimentObjective(objective_type='test',description='test',research_objective_id=research.id,hypothesis_ids=['H1']))
    planner.register_variable(ExperimentalVariable(id='velocity',name='velocity',units='m/s',role=VariableRole.DEPENDENT,epistemic_state=ClaimStatus.UNKNOWN))
    planner.register_measurement(MeasurementSpecification(id='m',variable_id='velocity',measurement_method='sensor',units='m/s'))
    prediction=planner.register_prediction(Prediction(expected_value=10,units='m/s',uncertainty={'sigma':1},source_refs=['H1']))
    plan=planner.create_plan(ExperimentPlanRequest(research_objective_id=research.id,experiment_objective_id=objective.id,variable_ids=['velocity'],measurement_ids=['m'],prediction_ids=[prediction.id]))
    return planner,plan,prediction

def test_result_creation_and_unknown_plan_rejection():
    planner,plan,_=setup(); engine=ExperimentResultsEngine(planner=planner)
    result=engine.create_result(ExperimentResult(plan_id=plan.id,source_reference='external lab',observations=[Observation(variable='velocity',value=10,units='m/s',uncertainty=.5)]))
    assert result.canonical_hash and result.evidence_state==ClaimStatus.MEASURED
    with pytest.raises(ValueError): engine.create_result(ExperimentResult(plan_id=uuid4(),source_reference='x',measurements={'x':1}))

def test_prediction_comparison_and_analysis_are_deterministic():
    planner,plan,_=setup(); engine=ExperimentResultsEngine(planner=planner)
    result=engine.create_result(ExperimentResult(plan_id=plan.id,source_reference='lab',conditions={'room':'lab'},observations=[Observation(variable='velocity',value=10.4,units='m/s',uncertainty=.5)]))
    analysis=engine.analyze(result.id); repeat=engine.analyze(result.id)
    assert analysis.canonical_hash==repeat.canonical_hash
    assert analysis.prediction_comparisons[0].comparison_status==ComparisonStatus.MATCHES_WITHIN_UNCERTAINTY
    assert analysis.quality_findings==[ResultQuality.ACCEPTABLE.value]
    assert analysis.hypothesis_impacts[0].state.value=='SUPPORTS'

def test_unit_mismatch_missing_data_and_simulation_preservation():
    planner,plan,_=setup(); engine=ExperimentResultsEngine(planner=planner)
    result=engine.create_result(ExperimentResult(plan_id=plan.id,source_reference='sim',evidence_state=ClaimStatus.SIMULATED,observations=[Observation(variable='velocity',value=10,units='km/h',evidence_state=ClaimStatus.SIMULATED)]))
    analysis=engine.analyze(result.id)
    assert analysis.prediction_comparisons[0].comparison_status==ComparisonStatus.INCOMPARABLE
    assert result.evidence_state==ClaimStatus.SIMULATED

def test_invalidation_history_and_api_authentication():
    planner,plan,_=setup(); engine=ExperimentResultsEngine(planner=planner)
    result=engine.create_result(ExperimentResult(plan_id=plan.id,source_reference='lab',conditions={'room':'lab'},measurements={'velocity':10}))
    engine.analyze(result.id); engine.invalidate(result.id,'corrupt source')
    assert result.status.value=='INVALIDATED' and len(engine.history[result.id])==3
    client=TestClient(app)
    assert client.post('/api/v1/experiment-results/results',json={'plan_id':str(plan.id),'source_reference':'x','measurements':{'x':1}}).status_code==401
