from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

LanguageId = Literal[
    "python",
    "r",
    "julia",
    "javascript",
    "typescript",
    "sql",
    "c",
    "cpp",
    "fortran",
    "rust",
    "go",
    "haskell",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ExecuteRequest(StrictModel):
    methodId: str = Field(min_length=1, max_length=96, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    language: LanguageId
    inputs: dict[str, float] = Field(default_factory=dict)
    timeoutSeconds: int = Field(default=8, ge=1, le=20)
    includeSource: bool = False

    @field_validator("inputs")
    @classmethod
    def limit_inputs(cls, value: dict[str, float]) -> dict[str, float]:
        if len(value) > 64:
            raise ValueError("Too many input fields.")
        return value


class CompareRequest(StrictModel):
    methodId: str = Field(min_length=1, max_length=96, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    languages: list[LanguageId] = Field(min_length=1, max_length=8)
    inputs: dict[str, float] = Field(default_factory=dict)
    timeoutSeconds: int = Field(default=8, ge=1, le=20)
    includeSource: bool = False
    absoluteTolerance: float = Field(default=1e-10, gt=0, le=1)
    relativeTolerance: float = Field(default=1e-9, gt=0, le=1)

    @field_validator("languages")
    @classmethod
    def unique_languages(cls, value: list[LanguageId]) -> list[LanguageId]:
        deduplicated = list(dict.fromkeys(value))
        if not deduplicated:
            raise ValueError("At least one language is required.")
        return deduplicated


class ValidateRequest(StrictModel):
    methodId: str = Field(min_length=1, max_length=96, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    inputs: dict[str, float] = Field(default_factory=dict)


class JobRequest(StrictModel):
    operation: Literal["execute", "compare"]
    execute: ExecuteRequest | None = None
    compare: CompareRequest | None = None

    @field_validator("compare")
    @classmethod
    def require_matching_payload(cls, value: CompareRequest | None, info: Any) -> CompareRequest | None:
        operation = info.data.get("operation")
        if operation == "compare" and value is None:
            raise ValueError("A compare payload is required for compare jobs.")
        return value

    def selected_payload(self) -> dict[str, Any]:
        if self.operation == "execute":
            if self.execute is None:
                raise ValueError("An execute payload is required for execute jobs.")
            return self.execute.model_dump()
        if self.compare is None:
            raise ValueError("A compare payload is required for compare jobs.")
        return self.compare.model_dump()
