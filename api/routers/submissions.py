"""API routes for code submission endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.schemas import SubmissionRequest
from controllers.submission_controller import SubmissionController

router = APIRouter(
    prefix="/submit",
    tags=["Submissions"],
    responses={
        400: {"description": "Bad request - invalid language or language not ready"},
        404: {"description": "Job not found"},
    },
)


@router.post(
    "",
    summary="Submit code for execution",
    description="""
    Submit code to be executed in an isolated Docker container with optional file uploads.

    The code will be queued for execution and you'll receive a job_id
    to check the execution status and retrieve results.

    **Requirements:**
    - The specified language must exist and be enabled
    - The language's Docker image must be built and ready

    **File Uploads (Optional):**
    - Maximum 10 files per submission
    - Total size limit: 25MB
    - Allowed extensions: .txt, .json, .csv, .xml, .yaml, .yml, .md, .dat, .log, .tsv, .ini, .conf, .properties, .sql, .html, .css, .js
    - Files will be available in the container at `/data/<filename>`

    **Example Usage:**
    ```bash
    curl -X POST http://localhost:8000/api/submit \\
      -F "code=with open('/data/input.txt') as f: print(f.read())" \\
      -F "language=python" \\
      -F "files=@input.txt" \\
      -F "files=@data.csv"
    ```
    """,
    response_description="Job submission confirmation with job_id",
)
async def submit_code(
    code: str = Form(..., description="Source code to execute"),
    language: str = Form(..., description="Programming language identifier"),
    files: Optional[List[UploadFile]] = File(None, description="Optional files to upload"),
    db: Session = Depends(get_db),
):
    """Submit code for execution with optional file uploads."""
    # Create SubmissionRequest from form data
    submission = SubmissionRequest(code=code, language=language)

    return SubmissionController.submit_code(submission, db, files)


@router.get(
    "/results/{job_id}",
    summary="Get execution results",
    description="""
    Retrieve the execution results for a submitted job.

    **Status values:**
    - `PENDING`: Job is queued for execution
    - `RUNNING`: Job is currently executing
    - `COMPLETED`: Execution finished successfully
    - `FAILED`: Execution failed
    - `TIMEOUT`: Execution exceeded time limit
    - `NOT_FOUND`: Job ID doesn't exist
    """,
    response_description="Execution status and output",
)
async def get_results(job_id: str, db: Session = Depends(get_db)):
    """Get the execution status and results for a job."""
    return SubmissionController.get_results(job_id, db)
