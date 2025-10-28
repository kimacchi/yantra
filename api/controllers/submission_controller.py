"""Controller for handling code submission business logic."""
import uuid
import json
from typing import Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.database import Compiler, Submission
from models.schemas import SubmissionRequest
from config import get_redis_connection, REDIS_QUEUE_NAME


class SubmissionController:
    """Handles business logic for code submissions."""

    @staticmethod
    def submit_code(submission: SubmissionRequest, db: Session) -> Dict[str, Any]:
        """
        Submit code for execution.

        Args:
            submission: The submission request
            db: Database session

        Returns:
            Dictionary with job_id and message

        Raises:
            HTTPException: If language not found, disabled, or not ready
        """
        job_id = str(uuid.uuid4())

        # Validate language exists and is ready
        compiler = db.query(Compiler).filter(Compiler.id == submission.language).first()

        if not compiler:
            raise HTTPException(
                status_code=400, detail=f"Language '{submission.language}' not found"
            )

        if not compiler.enabled:
            raise HTTPException(
                status_code=400, detail=f"Language '{submission.language}' is disabled"
            )

        if compiler.build_status != "ready":
            raise HTTPException(
                status_code=400,
                detail=f"Language '{submission.language}' is not ready (status: {compiler.build_status})",
            )

        # Create job entry in database
        new_submission = Submission(
            job_id=job_id, code=submission.code, language=submission.language, status="PENDING"
        )
        db.add(new_submission)
        db.commit()

        # Create job payload for the queue
        job_payload = {"job_id": job_id, "code": submission.code, "language": submission.language}

        # Push job to Redis queue
        redis_conn = get_redis_connection()
        redis_conn.lpush(REDIS_QUEUE_NAME, json.dumps(job_payload))

        return {"message": "Job submitted", "job_id": job_id}

    @staticmethod
    def get_results(job_id: str, db: Session) -> Dict[str, Any]:
        """
        Retrieve submission results.

        Args:
            job_id: The job identifier
            db: Database session

        Returns:
            Dictionary with status and output information
        """
        submission = db.query(Submission).filter(Submission.job_id == job_id).first()

        if not submission:
            return {"status": "NOT_FOUND"}

        return {
            "status": submission.status,
            "stdout": submission.output_stdout,
            "stderr": submission.output_stderr,
            "completed_at": submission.completed_at,
        }
