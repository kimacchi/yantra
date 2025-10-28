"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Submission Schemas
class SubmissionRequest(BaseModel):
    """Schema for code submission request."""

    code: str = Field(..., description="Source code to execute")
    language: str = Field(..., description="Programming language identifier")


class SubmissionResponse(BaseModel):
    """Schema for submission status response."""

    status: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    completed_at: Optional[datetime] = None


# Compiler Schemas
class CreateCompilerRequest(BaseModel):
    """Schema for creating a new compiler."""

    id: str = Field(..., description="Unique identifier (e.g., 'python-3.11')")
    name: str = Field(..., description="Display name")
    dockerfile_content: str = Field(..., description="Complete Dockerfile content")
    run_command: List[str] = Field(
        ..., description="Command to execute code (e.g., ['python', '-'])"
    )
    version: Optional[str] = None
    memory_limit: str = "512m"
    cpu_limit: str = "1"
    timeout_seconds: int = 10


class UpdateCompilerRequest(BaseModel):
    """Schema for updating an existing compiler."""

    name: Optional[str] = None
    dockerfile_content: Optional[str] = None
    run_command: Optional[List[str]] = None
    version: Optional[str] = None
    memory_limit: Optional[str] = None
    cpu_limit: Optional[str] = None
    timeout_seconds: Optional[int] = None
    enabled: Optional[bool] = None


class CompilerResponse(BaseModel):
    """Schema for compiler response."""

    id: str
    name: str
    dockerfile_content: str
    run_command: List[str]
    image_tag: str
    version: Optional[str]
    memory_limit: str
    cpu_limit: str
    timeout_seconds: int
    enabled: bool
    build_status: str
    build_error: Optional[str]
    created_at: str
    updated_at: str
    built_at: Optional[str]

    class Config:
        from_attributes = True
