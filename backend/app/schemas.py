from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ComputeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._-]+$")
    version: str | None = Field(default=None, max_length=32)
    inputs: dict[str, Any] = Field(default_factory=dict)
    units: dict[str, str] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    project_id: str | None = Field(default=None, max_length=128)
    requested_outputs: list[str] = Field(default_factory=lambda: ["summary", "values"], max_length=16)
    random_seed: int | None = None
    execution_target: Literal["automatic", "python-core"] = "automatic"

    @field_validator("requested_outputs")
    @classmethod
    def unique_outputs(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(str(v)[:64] for v in values))


class MethodSummary(BaseModel):
    id: str
    version: str
    title: str
    domain: str
    description: str
    packages: list[str]
    execution_modes: list[str]
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    assumptions: list[str]
    references: list[dict[str, str]] = Field(default_factory=list)
    example_inputs: dict[str, Any] = Field(default_factory=dict)
    example_parameters: dict[str, Any] = Field(default_factory=dict)
    recommended_execution: str = "synchronous"
    estimated_cost: str = "light"


class ProvenanceRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    schema_id: str = Field(default="sc-lab-compute-provenance/1.0", serialization_alias="schema")
    run_id: str
    method: str
    method_version: str
    service_version: str
    executed_at: str
    duration_ms: float
    python_version: str
    platform: str
    packages: dict[str, str]
    input_sha256: str
    result_sha256: str
    random_seed: int | None = None
    worker_type: str = "python-core-cpu"
    authentication_mode: str
    client_id: str


class ComputeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    schema_id: str = Field(default="sc-lab-compute-result/1.0", serialization_alias="schema")
    ok: bool = True
    method: str
    method_version: str
    outputs: dict[str, Any]
    summary: str
    warnings: list[str] = Field(default_factory=list)
    validation: dict[str, Any] = Field(default_factory=dict)
    provenance: ProvenanceRecord
