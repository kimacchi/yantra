"""API routes for compiler management endpoints."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.schemas import (
    CreateCompilerRequest,
    UpdateCompilerRequest,
    CompilerResponse,
)
from controllers.compiler_controller import CompilerController

router = APIRouter(
    prefix="/compilers",
    tags=["Compilers"],
    responses={
        404: {"description": "Compiler not found"},
        400: {"description": "Bad request - validation error or duplicate ID"},
    },
)


@router.post(
    "",
    response_model=CompilerResponse,
    status_code=201,
    summary="Create a new compiler",
    description="""
    Create a new compiler/runtime configuration and queue it for Docker image building.

    **What happens:**
    1. A new compiler configuration is saved to the database
    2. A Docker image build job is queued
    3. The builder service will create the Docker image asynchronously
    4. The compiler's `build_status` will update as the build progresses

    **Build statuses:**
    - `pending`: Build queued, not started yet
    - `building`: Build in progress
    - `ready`: Build completed successfully, compiler ready to use
    - `failed`: Build failed (check `build_error` field)
    """,
    response_description="The created compiler configuration",
)
async def create_compiler(compiler_req: CreateCompilerRequest, db: Session = Depends(get_db)):
    """Create a new compiler and queue it for image building."""
    return CompilerController.create_compiler(compiler_req, db)


@router.get(
    "",
    response_model=List[CompilerResponse],
    summary="List all compilers",
    description="""
    Retrieve a list of all compiler configurations.

    Use the `enabled_only` query parameter to filter for only enabled compilers.
    """,
    response_description="List of compiler configurations",
)
async def list_compilers(enabled_only: bool = False, db: Session = Depends(get_db)):
    """List all compilers, optionally filtering for enabled ones only."""
    return CompilerController.list_compilers(enabled_only, db)


@router.get(
    "/{compiler_id}",
    response_model=CompilerResponse,
    summary="Get compiler details",
    description="""
    Retrieve detailed information about a specific compiler.

    Returns the complete configuration including build status, Docker settings,
    and execution parameters.
    """,
    response_description="Compiler configuration details",
)
async def get_compiler(compiler_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific compiler."""
    return CompilerController.get_compiler(compiler_id, db)


@router.put(
    "/{compiler_id}",
    response_model=CompilerResponse,
    summary="Update a compiler",
    description="""
    Update an existing compiler configuration.

    **Important:**
    - Updating `dockerfile_content` or `run_command` will trigger a rebuild
    - The compiler's `build_status` will reset to `pending` during rebuild
    - Other fields can be updated without triggering a rebuild

    Only provide the fields you want to update - all fields are optional.
    """,
    response_description="Updated compiler configuration",
)
async def update_compiler(
    compiler_id: str, update: UpdateCompilerRequest, db: Session = Depends(get_db)
):
    """Update a compiler and trigger rebuild if necessary."""
    return CompilerController.update_compiler(compiler_id, update, db)


@router.delete(
    "/{compiler_id}",
    summary="Delete a compiler",
    description="""
    Delete a compiler configuration and queue cleanup of its Docker image.

    **Warning:** This action cannot be undone.

    The Docker image will be removed asynchronously by the builder service.
    """,
    response_description="Deletion confirmation message",
)
async def delete_compiler(compiler_id: str, db: Session = Depends(get_db)):
    """Delete a compiler and queue cleanup of its Docker image."""
    return CompilerController.delete_compiler(compiler_id, db)


@router.post(
    "/{compiler_id}/build",
    summary="Trigger manual rebuild",
    description="""
    Manually trigger a rebuild of the compiler's Docker image.

    This is useful when:
    - A previous build failed and you want to retry
    - You want to rebuild with updated base images
    - You need to force a clean rebuild

    The build will be queued and processed asynchronously.
    """,
    response_description="Build trigger confirmation",
)
async def trigger_build(compiler_id: str, db: Session = Depends(get_db)):
    """Manually trigger a rebuild of the compiler's Docker image."""
    return CompilerController.trigger_build(compiler_id, db)


@router.get(
    "/{compiler_id}/logs",
    summary="Get build logs",
    description="""
    Retrieve the full Docker build output logs for a compiler.

    Returns the complete stdout and stderr from the most recent build attempt.
    Useful for debugging build failures and understanding the build process.
    """,
    response_description="Build logs",
)
async def get_build_logs(compiler_id: str, db: Session = Depends(get_db)):
    """Get the full build logs for a compiler."""
    return CompilerController.get_build_logs(compiler_id, db)
