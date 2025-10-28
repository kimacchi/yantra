"""Controller for handling code submission business logic."""
import uuid
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile

from models.database import Compiler, Submission
from models.schemas import SubmissionRequest, FileMetadata
from config import (
    get_redis_connection,
    REDIS_QUEUE_NAME,
    MAX_UPLOAD_SIZE,
    MAX_FILES_PER_SUBMISSION,
    ALLOWED_EXTENSIONS,
    EXECUTOR_JOBS_DIR,
)


class SubmissionController:
    """Handles business logic for code submissions."""

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent directory traversal and other attacks.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Get just the basename (no path components)
        filename = os.path.basename(filename)

        # Remove any remaining dangerous characters
        # Keep only alphanumeric, dots, hyphens, and underscores
        safe_chars = []
        for char in filename:
            if char.isalnum() or char in ".-_":
                safe_chars.append(char)
            else:
                safe_chars.append("_")

        sanitized = "".join(safe_chars)

        # Ensure filename is not empty after sanitization
        if not sanitized or sanitized == ".":
            sanitized = f"file_{uuid.uuid4().hex[:8]}"

        return sanitized

    @staticmethod
    def _validate_file_extension(filename: str) -> bool:
        """
        Validate file extension against whitelist.

        Args:
            filename: Filename to validate

        Returns:
            True if extension is allowed, False otherwise
        """
        ext = Path(filename).suffix.lower()
        return ext in ALLOWED_EXTENSIONS

    @staticmethod
    def _save_uploaded_files(
        files: List[UploadFile], job_id: str
    ) -> tuple[str, List[FileMetadata]]:
        """
        Save uploaded files to job directory.

        Args:
            files: List of uploaded files
            job_id: Job identifier

        Returns:
            Tuple of (directory_path, list of file metadata)

        Raises:
            HTTPException: If file validation fails
        """
        # Validate file count
        if len(files) > MAX_FILES_PER_SUBMISSION:
            raise HTTPException(
                status_code=400,
                detail=f"Too many files. Maximum {MAX_FILES_PER_SUBMISSION} files allowed.",
            )

        # Create job directory
        job_dir = os.path.join(EXECUTOR_JOBS_DIR, job_id)
        os.makedirs(job_dir, exist_ok=True)

        file_metadata_list = []
        total_size = 0

        try:
            for upload_file in files:
                # Read file content
                content = upload_file.file.read()
                file_size = len(content)

                # Validate individual file isn't empty
                if file_size == 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File '{upload_file.filename}' is empty.",
                    )

                # Check cumulative size
                total_size += file_size
                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Total file size exceeds {MAX_UPLOAD_SIZE / (1024 * 1024)}MB limit.",
                    )

                # Validate extension
                if not SubmissionController._validate_file_extension(upload_file.filename):
                    raise HTTPException(
                        status_code=400,
                        detail=f"File extension not allowed for '{upload_file.filename}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
                    )

                # Sanitize filename
                safe_filename = SubmissionController._sanitize_filename(upload_file.filename)

                # Save file
                file_path = os.path.join(job_dir, safe_filename)
                with open(file_path, "wb") as f:
                    f.write(content)

                # Store metadata
                file_metadata_list.append(
                    FileMetadata(
                        filename=safe_filename,
                        size=file_size,
                        mime_type=upload_file.content_type,
                    )
                )

            return job_dir, file_metadata_list

        except HTTPException:
            # Clean up directory on validation failure
            if os.path.exists(job_dir):
                shutil.rmtree(job_dir)
            raise
        except Exception as e:
            # Clean up directory on any error
            if os.path.exists(job_dir):
                shutil.rmtree(job_dir)
            raise HTTPException(status_code=500, detail=f"Failed to save files: {str(e)}")

    @staticmethod
    def submit_code(
        submission: SubmissionRequest,
        db: Session,
        files: Optional[List[UploadFile]] = None,
    ) -> Dict[str, Any]:
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

        # Handle file uploads if provided
        files_directory = None
        uploaded_files_metadata = None

        if files and len(files) > 0:
            files_directory, file_metadata_list = SubmissionController._save_uploaded_files(
                files, job_id
            )
            uploaded_files_metadata = json.dumps([fm.dict() for fm in file_metadata_list])

        # Create job entry in database
        new_submission = Submission(
            job_id=job_id,
            code=submission.code,
            language=submission.language,
            status="PENDING",
            uploaded_files=uploaded_files_metadata,
            files_directory=files_directory,
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

        # Parse uploaded files metadata if present
        uploaded_files = None
        if submission.uploaded_files:
            try:
                uploaded_files = json.loads(submission.uploaded_files)
            except json.JSONDecodeError:
                uploaded_files = None

        return {
            "status": submission.status,
            "stdout": submission.output_stdout,
            "stderr": submission.output_stderr,
            "completed_at": submission.completed_at,
            "uploaded_files": uploaded_files,
        }
