"""API routes for Dockerfile template endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.schemas import CreateTemplateRequest, TemplateResponse
from controllers.template_controller import TemplateController

router = APIRouter(
    prefix="/templates",
    tags=["Templates"],
    responses={
        404: {"description": "Template not found"},
        400: {"description": "Bad request - validation error or duplicate ID"},
    },
)


@router.post(
    "",
    response_model=TemplateResponse,
    status_code=201,
    summary="Create a new Dockerfile template",
    description="""
    Create a new Dockerfile template that users can fetch and build upon.

    Templates are starting points for creating custom compiler images.
    They contain Dockerfile content that users can customize for their needs.
    """,
    response_description="The created template",
)
async def create_template(
    template_req: CreateTemplateRequest, db: Session = Depends(get_db)
):
    """Create a new Dockerfile template."""
    return TemplateController.create_template(template_req, db)


@router.get(
    "",
    response_model=List[TemplateResponse],
    summary="List all Dockerfile templates",
    description="""
    Retrieve a list of all available Dockerfile templates.

    Use query parameters to filter:
    - `category`: Filter by category (language, framework, tool, os)
    - `official_only`: Show only official templates
    """,
    response_description="List of Dockerfile templates",
)
async def list_templates(
    category: Optional[str] = None,
    official_only: bool = False,
    db: Session = Depends(get_db),
):
    """List all templates with optional filtering."""
    return TemplateController.list_templates(category, official_only, db)


@router.get(
    "/{template_id}",
    response_model=TemplateResponse,
    summary="Get template details",
    description="""
    Retrieve detailed information about a specific Dockerfile template.

    Returns the complete template including the Dockerfile content,
    suggested run commands, tags, and metadata.
    """,
    response_description="Template details",
)
async def get_template(template_id: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific template."""
    return TemplateController.get_template(template_id, db)


@router.delete(
    "/{template_id}",
    summary="Delete a template",
    description="""
    Delete a Dockerfile template.

    **Warning:** This action cannot be undone.
    """,
    response_description="Deletion confirmation message",
)
async def delete_template(template_id: str, db: Session = Depends(get_db)):
    """Delete a Dockerfile template."""
    return TemplateController.delete_template(template_id, db)
