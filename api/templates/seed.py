"""Template seeding logic for initializing default Dockerfile templates."""
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.database import DockerfileTemplate
from .definitions import LANGUAGE_TEMPLATES


def seed_templates(db: Session) -> Dict[str, Any]:
    """
    Seed default Dockerfile templates into the database.

    This function is idempotent - it will:
    - Skip templates that already exist (by ID)
    - Insert new templates
    - Optionally update existing templates if they've changed

    Args:
        db: SQLAlchemy database session

    Returns:
        Dictionary with seeding results (added, skipped, errors)
    """
    results = {
        "added": [],
        "skipped": [],
        "updated": [],
        "errors": [],
    }

    for template_data in LANGUAGE_TEMPLATES:
        try:
            template_id = template_data["id"]

            # Check if template already exists
            existing_template = (
                db.query(DockerfileTemplate)
                .filter(DockerfileTemplate.id == template_id)
                .first()
            )

            if existing_template:
                # Template exists - optionally update it
                # For now, we'll skip to avoid overwriting user modifications
                results["skipped"].append(template_id)
                continue

            # Create new template
            template = DockerfileTemplate(
                id=template_data["id"],
                name=template_data["name"],
                description=template_data["description"],
                category=template_data["category"],
                dockerfile_template=template_data["dockerfile_template"],
                default_run_command=(
                    json.dumps(template_data["default_run_command"])
                    if template_data.get("default_run_command")
                    else None
                ),
                tags=(
                    json.dumps(template_data["tags"])
                    if template_data.get("tags")
                    else None
                ),
                icon=template_data.get("icon"),
                author=template_data.get("author", "yantra"),
                is_official=template_data.get("is_official", True),
            )

            db.add(template)
            results["added"].append(template_id)

        except IntegrityError as e:
            # This shouldn't happen due to our check above, but handle it anyway
            db.rollback()
            results["errors"].append({
                "template_id": template_id,
                "error": f"Integrity error: {str(e)}"
            })
        except Exception as e:
            db.rollback()
            results["errors"].append({
                "template_id": template_id,
                "error": str(e)
            })

    # Commit all changes at once
    try:
        if results["added"]:
            db.commit()
    except Exception as e:
        db.rollback()
        results["errors"].append({
            "template_id": "commit",
            "error": f"Failed to commit changes: {str(e)}"
        })

    return results


def update_existing_templates(db: Session) -> Dict[str, Any]:
    """
    Update existing templates with new definitions.

    Use this function when you want to sync template changes
    to the database, overwriting existing templates.

    Args:
        db: SQLAlchemy database session

    Returns:
        Dictionary with update results
    """
    results = {
        "updated": [],
        "added": [],
        "errors": [],
    }

    for template_data in LANGUAGE_TEMPLATES:
        try:
            template_id = template_data["id"]

            # Find existing template
            existing_template = (
                db.query(DockerfileTemplate)
                .filter(DockerfileTemplate.id == template_id)
                .first()
            )

            if existing_template:
                # Update existing template
                existing_template.name = template_data["name"]
                existing_template.description = template_data["description"]
                existing_template.category = template_data["category"]
                existing_template.dockerfile_template = template_data["dockerfile_template"]
                existing_template.default_run_command = (
                    json.dumps(template_data["default_run_command"])
                    if template_data.get("default_run_command")
                    else None
                )
                existing_template.tags = (
                    json.dumps(template_data["tags"])
                    if template_data.get("tags")
                    else None
                )
                existing_template.icon = template_data.get("icon")
                existing_template.author = template_data.get("author", "yantra")
                existing_template.is_official = template_data.get("is_official", True)

                results["updated"].append(template_id)
            else:
                # Create new template
                template = DockerfileTemplate(
                    id=template_data["id"],
                    name=template_data["name"],
                    description=template_data["description"],
                    category=template_data["category"],
                    dockerfile_template=template_data["dockerfile_template"],
                    default_run_command=(
                        json.dumps(template_data["default_run_command"])
                        if template_data.get("default_run_command")
                        else None
                    ),
                    tags=(
                        json.dumps(template_data["tags"])
                        if template_data.get("tags")
                        else None
                    ),
                    icon=template_data.get("icon"),
                    author=template_data.get("author", "yantra"),
                    is_official=template_data.get("is_official", True),
                )

                db.add(template)
                results["added"].append(template_id)

        except Exception as e:
            db.rollback()
            results["errors"].append({
                "template_id": template_id,
                "error": str(e)
            })

    # Commit all changes
    try:
        if results["updated"] or results["added"]:
            db.commit()
    except Exception as e:
        db.rollback()
        results["errors"].append({
            "template_id": "commit",
            "error": f"Failed to commit changes: {str(e)}"
        })

    return results
