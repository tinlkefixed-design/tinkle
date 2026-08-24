from __future__ import annotations
from pydantic import BaseModel, Field

class PersistenceConfig(BaseModel):
    database_url: str = Field(default="sqlite:///./data/tinkle.db")
    redis_url: str = Field(default="redis://localhost:6379/0")
    qdrant_url: str = Field(default="http://localhost:6333")
    qdrant_collection: str = Field(default="tinkle_knowledge")
    durable_memory: bool = True
