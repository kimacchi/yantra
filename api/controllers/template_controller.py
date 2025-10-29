"""Controller for handling Dockerfile template business logic."""
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.database import DockerfileTemplate
from models.schemas import CreateTemplateRequest, TemplateResponse


class TemplateController:
    """Handles business logic for Dockerfile template management."""

    @staticmethod
    def create_template(
        template_req: CreateTemplateRequest, db: Session
    ) -> TemplateResponse:
        """
        Create a new Dockerfile template.

        Args:
            template_req: The template creation request
            db: Database session

        Returns:
            TemplateResponse with the created template details

        Raises:
            HTTPException: If template ID already exists
        """
        # Check if template ID already exists
        existing = (
            db.query(DockerfileTemplate)
            .filter(DockerfileTemplate.id == template_req.id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Template with id '{template_req.id}' already exists",
            )

        # Create template
        new_template = DockerfileTemplate(
            id=template_req.id,
            name=template_req.name,
            description=template_req.description,
            category=template_req.category,
            dockerfile_template=template_req.dockerfile_template,
            default_run_command=(
                json.dumps(template_req.default_run_command)
                if template_req.default_run_command
                else None
            ),
            tags=json.dumps(template_req.tags) if template_req.tags else None,
            icon=template_req.icon,
            author=template_req.author,
            is_official=template_req.is_official,
        )

        db.add(new_template)
        db.commit()
        db.refresh(new_template)

        return TemplateController._to_response(new_template)

    @staticmethod
    def list_templates(
        category: Optional[str] = None,
        official_only: bool = False,
        db: Session = None,
    ) -> List[TemplateResponse]:
        """
        List all Dockerfile templates with optional filtering.

        Args:
            category: Optional category filter
            official_only: Whether to show only official templates
            db: Database session

        Returns:
            List of TemplateResponse objects
        """
        query = db.query(DockerfileTemplate)

        if category:
            query = query.filter(DockerfileTemplate.category == category)

        if official_only:
            query = query.filter(DockerfileTemplate.is_official == True)

        templates = query.order_by(DockerfileTemplate.name).all()
        return [TemplateController._to_response(t) for t in templates]

    @staticmethod
    def get_template(template_id: str, db: Session) -> TemplateResponse:
        """
        Get a specific Dockerfile template by ID.

        Args:
            template_id: The template ID
            db: Database session

        Returns:
            TemplateResponse with the template details

        Raises:
            HTTPException: If template not found
        """
        template = (
            db.query(DockerfileTemplate)
            .filter(DockerfileTemplate.id == template_id)
            .first()
        )

        if not template:
            raise HTTPException(
                status_code=404, detail=f"Template '{template_id}' not found"
            )

        return TemplateController._to_response(template)

    @staticmethod
    def delete_template(template_id: str, db: Session) -> dict:
        """
        Delete a Dockerfile template.

        Args:
            template_id: The template ID
            db: Database session

        Returns:
            Deletion confirmation message

        Raises:
            HTTPException: If template not found
        """
        template = (
            db.query(DockerfileTemplate)
            .filter(DockerfileTemplate.id == template_id)
            .first()
        )

        if not template:
            raise HTTPException(
                status_code=404, detail=f"Template '{template_id}' not found"
            )

        db.delete(template)
        db.commit()

        return {"message": f"Template '{template_id}' deleted successfully"}

    @staticmethod
    def _to_response(template: DockerfileTemplate) -> TemplateResponse:
        """
        Convert a DockerfileTemplate model to a TemplateResponse.

        Args:
            template: The DockerfileTemplate model instance

        Returns:
            TemplateResponse object
        """
        return TemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            category=template.category,
            dockerfile_template=template.dockerfile_template,
            default_run_command=(
                json.loads(template.default_run_command)
                if template.default_run_command
                else None
            ),
            tags=json.loads(template.tags) if template.tags else None,
            icon=template.icon,
            author=template.author,
            is_official=template.is_official,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat(),
        )
