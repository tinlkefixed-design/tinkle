from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from tinkle.reality_engine import ClaimStatus


def utc_now() -> datetime:
    return datetime.now(UTC)


class NodeType(str, Enum):
    RESEARCH_PROJECT = "ResearchProject"
    RESEARCH_QUESTION = "ResearchQuestion"
    PROBLEM = "Problem"
    SCIENTIFIC_DOMAIN = "ScientificDomain"
    CONCEPT = "Concept"
    PRINCIPLE = "Principle"
    VARIABLE = "Variable"
    PARAMETER = "Parameter"
    EQUATION = "Equation"
    PROPERTY = "Property"
    MATERIAL = "Material"
    TECHNOLOGY = "Technology"
    MODEL = "Model"
    HYPOTHESIS = "Hypothesis"
    EXPERIMENT = "Experiment"
    SIMULATION = "Simulation"
    RESULT = "Result"
    CLAIM = "Claim"
    EVIDENCE = "Evidence"
    SOURCE = "Source"
    ASSUMPTION = "Assumption"
    UNKNOWN = "Unknown"
    FAILURE = "Failure"
    DESIGN = "Design"
    COMPONENT = "Component"


class RelationshipType(str, Enum):
    BELONGS_TO = "BELONGS_TO"
    PART_OF = "PART_OF"
    DEPENDS_ON = "DEPENDS_ON"
    DERIVED_FROM = "DERIVED_FROM"
    USES = "USES"
    REQUIRES = "REQUIRES"
    CONSTRAINS = "CONSTRAINS"
    AFFECTS = "AFFECTS"
    MEASURES = "MEASURES"
    DESCRIBES = "DESCRIBES"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    VALIDATES = "VALIDATES"
    FALSIFIES = "FALSIFIES"
    ASSUMES = "ASSUMES"
    HAS_PROPERTY = "HAS_PROPERTY"
    HAS_PARAMETER = "HAS_PARAMETER"
    USES_MATERIAL = "USES_MATERIAL"
    USES_TECHNOLOGY = "USES_TECHNOLOGY"
    MODELS = "MODELS"
    SIMULATES = "SIMULATES"
    PRODUCES = "PRODUCES"
    RESULT_OF = "RESULT_OF"
    EVIDENCE_FOR = "EVIDENCE_FOR"
    CITED_BY = "CITED_BY"
    RELATED_TO = "RELATED_TO"
    GENERATES = "GENERATES"
    TESTS = "TESTS"
    FAILS_UNDER = "FAILS_UNDER"
    COMPONENT_OF = "COMPONENT_OF"
    PROPOSES = "PROPOSES"
    TESTED_BY = "TESTED_BY"
    COMPARED_WITH = "COMPARED_WITH"
    SATISFIES = "SATISFIES"
    CONSTRAINED_BY = "CONSTRAINED_BY"
    EVALUATED_BY = "EVALUATED_BY"
    OUTPERFORMS = "OUTPERFORMS"
    VIOLATES = "VIOLATES"
    REQUIRES_DATA = "REQUIRES_DATA"
    INFORMS = "INFORMS"
    SUPPORTS_DECISION = "SUPPORTS_DECISION"
    REJECTS = "REJECTS"
    TRADEOFF_WITH = "TRADEOFF_WITH"
    SELECTS = "SELECTS"
    REQUIRES_VALIDATION = "REQUIRES_VALIDATION"
    SUPPORTED_BY = "SUPPORTED_BY"
    TRACEABLE_TO = "TRACEABLE_TO"
    REPRODUCED_BY = "REPRODUCED_BY"
    INVALIDATED_BY = "INVALIDATED_BY"


class GraphProvenance(BaseModel):
    source_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    provenance_record_ids: list[str] = Field(default_factory=list)
    notes: str | None = None


class ResearchGraphNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: NodeType
    name: str = Field(min_length=1, max_length=500)
    description: str = ""
    properties: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    provenance: GraphProvenance = Field(default_factory=GraphProvenance)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    confidence: float = Field(default=0.0, ge=0, le=1)
    project_id: UUID | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ResearchGraphEdge(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    target_id: UUID
    relationship: RelationshipType
    provenance: GraphProvenance = Field(default_factory=GraphProvenance)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    confidence: float | None = Field(default=None, ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class NodeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    properties: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    provenance: GraphProvenance | None = None
    epistemic_state: ClaimStatus | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    project_id: UUID | None = None


class EdgeCreate(BaseModel):
    source_id: UUID
    target_id: UUID
    relationship: RelationshipType
    provenance: GraphProvenance = Field(default_factory=GraphProvenance)
    epistemic_state: ClaimStatus = ClaimStatus.UNKNOWN
    confidence: float | None = Field(default=None, ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    node_type: NodeType | None = None
    project_id: UUID | None = None
    epistemic_state: ClaimStatus | None = None
    limit: int = Field(default=50, ge=1, le=500)


class GraphPathRequest(BaseModel):
    source_id: UUID
    target_id: UUID
    relationship: RelationshipType | None = None
    max_depth: int = Field(default=20, ge=1, le=100)


class KnowledgeGapRequest(BaseModel):
    question_id: UUID
    required_types: list[NodeType] = Field(default_factory=list)
    required_names: list[str] = Field(default_factory=list)


class KnowledgeGap(BaseModel):
    question_id: UUID
    known: list[ResearchGraphNode] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    unknown: list[ResearchGraphNode] = Field(default_factory=list)
    unvalidated: list[ResearchGraphNode] = Field(default_factory=list)
