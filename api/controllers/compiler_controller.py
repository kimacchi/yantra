"""Controller for handling compiler management business logic."""
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from models.database import Compiler
from models.schemas import (
    CreateCompilerRequest,
    UpdateCompilerRequest,
    CompilerResponse,
)
from config import get_redis_connection, REDIS_BUILD_QUEUE_NAME


class CompilerController:
    """Handles business logic for compiler management."""

    @staticmethod
    def create_compiler(compiler_req: CreateCompilerRequest, db: Session) -> CompilerResponse:
        """
        Create a new compiler and queue it for image building.

        Args:
            compiler_req: The compiler creation request
            db: Database session

        Returns:
            CompilerResponse with the created compiler details

        Raises:
            HTTPException: If compiler ID already exists
        """
        # Check if compiler ID already exists
        existing = db.query(Compiler).filter(Compiler.id == compiler_req.id).first()
        if existing:
            raise HTTPException(
                status_code=400, detail=f"Compiler with id '{compiler_req.id}' already exists"
            )

        # Generate image tag
        image_tag = f"yantra-{compiler_req.id}:latest"

        # Create compiler
        new_compiler = Compiler(
            id=compiler_req.id,
            name=compiler_req.name,
            dockerfile_content=compiler_req.dockerfile_content,
            run_command=json.dumps(compiler_req.run_command),
            image_tag=image_tag,
            version=compiler_req.version,
            memory_limit=compiler_req.memory_limit,
            cpu_limit=compiler_req.cpu_limit,
            timeout_seconds=compiler_req.timeout_seconds,
            build_status="pending",
            enabled=True,
        )
        db.add(new_compiler)
        db.commit()
        db.refresh(new_compiler)

        # Queue build job
        build_payload = {"compiler_id": compiler_req.id, "action": "build"}
        redis_conn = get_redis_connection()
        redis_conn.lpush(REDIS_BUILD_QUEUE_NAME, json.dumps(build_payload))

        return CompilerController._to_response(new_compiler)

    @staticmethod
    def list_compilers(enabled_only: bool, db: Session) -> List[CompilerResponse]:
        """
        List all compilers.

        Args:
            enabled_only: If True, only return enabled compilers
            db: Database session

        Returns:
            List of CompilerResponse objects
        """
        query = db.query(Compiler)

        if enabled_only:
            query = query.filter(Compiler.enabled == True)

        compilers = query.order_by(Compiler.created_at.desc()).all()

        return [CompilerController._to_response(compiler) for compiler in compilers]

    @staticmethod
    def get_compiler(compiler_id: str, db: Session) -> CompilerResponse:
        """
        Get a specific compiler by ID.

        Args:
            compiler_id: The compiler identifier
            db: Database session

        Returns:
            CompilerResponse object

        Raises:
            HTTPException: If compiler not found
        """
        compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()

        if not compiler:
            raise HTTPException(status_code=404, detail=f"Compiler '{compiler_id}' not found")

        return CompilerController._to_response(compiler)

    @staticmethod
    def update_compiler(
        compiler_id: str, update: UpdateCompilerRequest, db: Session
    ) -> CompilerResponse:
        """
        Update a compiler and trigger rebuild if necessary.

        Args:
            compiler_id: The compiler identifier
            update: The update request
            db: Database session

        Returns:
            CompilerResponse with updated details

        Raises:
            HTTPException: If compiler not found or no fields to update
        """
        compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()

        if not compiler:
            raise HTTPException(status_code=404, detail=f"Compiler '{compiler_id}' not found")

        # Track if rebuild is needed
        rebuild_needed = False

        # Update fields
        if update.name is not None:
            compiler.name = update.name
        if update.dockerfile_content is not None:
            compiler.dockerfile_content = update.dockerfile_content
            rebuild_needed = True
        if update.run_command is not None:
            compiler.run_command = json.dumps(update.run_command)
            rebuild_needed = True
        if update.version is not None:
            compiler.version = update.version
        if update.memory_limit is not None:
            compiler.memory_limit = update.memory_limit
        if update.cpu_limit is not None:
            compiler.cpu_limit = update.cpu_limit
        if update.timeout_seconds is not None:
            compiler.timeout_seconds = update.timeout_seconds
        if update.enabled is not None:
            compiler.enabled = update.enabled

        # Check if any update was provided
        if all(getattr(update, field) is None for field in update.model_fields):
            raise HTTPException(status_code=400, detail="No fields to update")

        # Update timestamp
        compiler.updated_at = func.now()

        # If rebuild needed, reset build status
        if rebuild_needed:
            compiler.build_status = "pending"
            compiler.build_error = None
            compiler.built_at = None

        db.commit()
        db.refresh(compiler)

        # Queue rebuild if needed
        if rebuild_needed:
            build_payload = {"compiler_id": compiler_id, "action": "build"}
            redis_conn = get_redis_connection()
            redis_conn.lpush(REDIS_BUILD_QUEUE_NAME, json.dumps(build_payload))

        return CompilerController._to_response(compiler)

    @staticmethod
    def delete_compiler(compiler_id: str, db: Session) -> Dict[str, str]:
        """
        Delete a compiler and queue cleanup of its Docker image.

        Args:
            compiler_id: The compiler identifier
            db: Database session

        Returns:
            Dictionary with success message

        Raises:
            HTTPException: If compiler not found
        """
        compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()

        if not compiler:
            raise HTTPException(status_code=404, detail=f"Compiler '{compiler_id}' not found")

        image_tag = compiler.image_tag

        # Delete from database
        db.delete(compiler)
        db.commit()

        # Queue cleanup job
        cleanup_payload = {
            "compiler_id": compiler_id,
            "image_tag": image_tag,
            "action": "cleanup",
        }
        redis_conn = get_redis_connection()
        redis_conn.lpush(REDIS_BUILD_QUEUE_NAME, json.dumps(cleanup_payload))

        return {"message": f"Compiler '{compiler_id}' deleted and cleanup queued"}

    @staticmethod
    def trigger_build(compiler_id: str, db: Session) -> Dict[str, str]:
        """
        Manually trigger a rebuild of the compiler's Docker image.

        Args:
            compiler_id: The compiler identifier
            db: Database session

        Returns:
            Dictionary with success message

        Raises:
            HTTPException: If compiler not found
        """
        compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()

        if not compiler:
            raise HTTPException(status_code=404, detail=f"Compiler '{compiler_id}' not found")

        # Update build status to pending
        compiler.build_status = "pending"
        compiler.build_error = None
        compiler.updated_at = func.now()
        db.commit()

        # Queue build job
        build_payload = {"compiler_id": compiler_id, "action": "build"}
        redis_conn = get_redis_connection()
        redis_conn.lpush(REDIS_BUILD_QUEUE_NAME, json.dumps(build_payload))

        return {"message": f"Build queued for compiler '{compiler_id}'"}

    @staticmethod
    def get_build_logs(compiler_id: str, db: Session) -> Dict[str, Any]:
        """
        Get the full build logs for a compiler.

        Args:
            compiler_id: The compiler identifier
            db: Database session

        Returns:
            Dictionary with build logs and metadata

        Raises:
            HTTPException: If compiler not found
        """
        compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()

        if not compiler:
            raise HTTPException(status_code=404, detail=f"Compiler '{compiler_id}' not found")

        return {
            "compiler_id": compiler.id,
            "compiler_name": compiler.name,
            "build_status": compiler.build_status,
            "build_logs": compiler.build_logs or "No build logs available",
            "build_error": compiler.build_error,
            "built_at": str(compiler.built_at) if compiler.built_at else None,
            "updated_at": str(compiler.updated_at),
        }

    @staticmethod
    def _to_response(compiler: Compiler) -> CompilerResponse:
        """
        Convert database model to response schema.

        Args:
            compiler: The compiler database model

        Returns:
            CompilerResponse object
        """
        response_data = {
            **compiler.__dict__,
            "run_command": json.loads(compiler.run_command),
            "created_at": str(compiler.created_at),
            "updated_at": str(compiler.updated_at),
            "built_at": str(compiler.built_at) if compiler.built_at else None,
        }
        return CompilerResponse(**response_data)
