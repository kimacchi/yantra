import uvicorn
import uuid
import json
from typing import Optional, List
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import redis

from database import get_db
from models import Compiler, Submission

# --- Config (In a real app, use env vars) ---
REDIS_CONN = redis.Redis(host='queue', port=6379, db=0)
REDIS_QUEUE_NAME = "job_queue"
REDIS_BUILD_QUEUE_NAME = "build_queue"

app = FastAPI()

# --- Pydantic Models ---
class SubmissionRequest(BaseModel):
    code: str
    language: str

class CreateCompilerRequest(BaseModel):
    id: str = Field(..., description="Unique identifier (e.g., 'python-3.11')")
    name: str = Field(..., description="Display name")
    dockerfile_content: str = Field(..., description="Complete Dockerfile content")
    run_command: List[str] = Field(..., description="Command to execute code (e.g., ['python', '-'])")
    version: Optional[str] = None
    memory_limit: str = "512m"
    cpu_limit: str = "1"
    timeout_seconds: int = 10

class UpdateCompilerRequest(BaseModel):
    name: Optional[str] = None
    dockerfile_content: Optional[str] = None
    run_command: Optional[List[str]] = None
    version: Optional[str] = None
    memory_limit: Optional[str] = None
    cpu_limit: Optional[str] = None
    timeout_seconds: Optional[int] = None
    enabled: Optional[bool] = None

class CompilerResponse(BaseModel):
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


@app.post("/submit")
async def submit_code(submission: SubmissionRequest, db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())

    # 1. Validate language exists and is ready
    compiler = db.query(Compiler).filter(Compiler.id == submission.language).first()

    if not compiler:
        raise HTTPException(status_code=400, detail=f"Language '{submission.language}' not found")

    if not compiler.enabled:
        raise HTTPException(status_code=400, detail=f"Language '{submission.language}' is disabled")

    if compiler.build_status != 'ready':
        raise HTTPException(
            status_code=400,
            detail=f"Language '{submission.language}' is not ready (status: {compiler.build_status})"
        )

    # 2. Create job entry in database
    new_submission = Submission(
        job_id=job_id,
        code=submission.code,
        language=submission.language,
        status='PENDING'
    )
    db.add(new_submission)
    db.commit()

    # 3. Create job payload for the queue
    job_payload = {
        "job_id": job_id,
        "code": submission.code,
        "language": submission.language
    }

    # 4. Push job to Redis queue
    REDIS_CONN.lpush(REDIS_QUEUE_NAME, json.dumps(job_payload))

    return {"message": "Job submitted", "job_id": job_id}


@app.get("/results/{job_id}")
async def get_results(job_id: str, db: Session = Depends(get_db)):
    submission = db.query(Submission).filter(Submission.job_id == job_id).first()

    if not submission:
        return {"status": "NOT_FOUND"}

    return {
        "status": submission.status,
        "stdout": submission.output_stdout,
        "stderr": submission.output_stderr,
        "completed_at": submission.completed_at
    }


# --- Compiler Management Endpoints ---

@app.post("/compilers", response_model=CompilerResponse, status_code=201)
async def create_compiler(compiler_req: CreateCompilerRequest, db: Session = Depends(get_db)):
    """Create a new compiler and queue it for image building."""

    # Check if compiler ID already exists
    existing = db.query(Compiler).filter(Compiler.id == compiler_req.id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Compiler with id '{compiler_req.id}' already exists")

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
        build_status='pending',
        enabled=True
    )
    db.add(new_compiler)
    db.commit()
    db.refresh(new_compiler)

    # Queue build job
    build_payload = {"compiler_id": compiler_req.id, "action": "build"}
    REDIS_CONN.lpush(REDIS_BUILD_QUEUE_NAME, json.dumps(build_payload))

    # Convert to response model
    response_data = {
        **new_compiler.__dict__,
        "run_command": json.loads(new_compiler.run_command),
        "created_at": str(new_compiler.created_at),
        "updated_at": str(new_compiler.updated_at),
        "built_at": str(new_compiler.built_at) if new_compiler.built_at else None
    }
    return CompilerResponse(**response_data)


@app.get("/compilers", response_model=List[CompilerResponse])
async def list_compilers(enabled_only: bool = False, db: Session = Depends(get_db)):
    """List all compilers."""
    query = db.query(Compiler)

    if enabled_only:
        query = query.filter(Compiler.enabled == True)

    compilers = query.order_by(Compiler.created_at.desc()).all()

    # Convert to response models
    results = []
    for compiler in compilers:
        response_data = {
            **compiler.__dict__,
            "run_command": json.loads(compiler.run_command),
            "created_at": str(compiler.created_at),
            "updated_at": str(compiler.updated_at),
            "built_at": str(compiler.built_at) if compiler.built_at else None
        }
        results.append(CompilerResponse(**response_data))

    return results


@app.get("/compilers/{compiler_id}", response_model=CompilerResponse)
async def get_compiler(compiler_id: str, db: Session = Depends(get_db)):
    """Get a specific compiler by ID."""
    compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()

    if not compiler:
        raise HTTPException(status_code=404, detail=f"Compiler '{compiler_id}' not found")

    response_data = {
        **compiler.__dict__,
        "run_command": json.loads(compiler.run_command),
        "created_at": str(compiler.created_at),
        "updated_at": str(compiler.updated_at),
        "built_at": str(compiler.built_at) if compiler.built_at else None
    }
    return CompilerResponse(**response_data)


@app.put("/compilers/{compiler_id}", response_model=CompilerResponse)
async def update_compiler(
    compiler_id: str,
    update: UpdateCompilerRequest,
    db: Session = Depends(get_db)
):
    """Update a compiler and trigger rebuild if Dockerfile or run_command changed."""
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
    from sqlalchemy import func
    compiler.updated_at = func.now()

    # If rebuild needed, reset build status
    if rebuild_needed:
        compiler.build_status = 'pending'
        compiler.build_error = None
        compiler.built_at = None

    db.commit()
    db.refresh(compiler)

    # Queue rebuild if needed
    if rebuild_needed:
        build_payload = {"compiler_id": compiler_id, "action": "build"}
        REDIS_CONN.lpush(REDIS_BUILD_QUEUE_NAME, json.dumps(build_payload))

    response_data = {
        **compiler.__dict__,
        "run_command": json.loads(compiler.run_command),
        "created_at": str(compiler.created_at),
        "updated_at": str(compiler.updated_at),
        "built_at": str(compiler.built_at) if compiler.built_at else None
    }
    return CompilerResponse(**response_data)


@app.delete("/compilers/{compiler_id}")
async def delete_compiler(compiler_id: str, db: Session = Depends(get_db)):
    """Delete a compiler and queue cleanup of its Docker image."""
    compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()

    if not compiler:
        raise HTTPException(status_code=404, detail=f"Compiler '{compiler_id}' not found")

    image_tag = compiler.image_tag

    # Delete from database
    db.delete(compiler)
    db.commit()

    # Queue cleanup job
    cleanup_payload = {"compiler_id": compiler_id, "image_tag": image_tag, "action": "cleanup"}
    REDIS_CONN.lpush(REDIS_BUILD_QUEUE_NAME, json.dumps(cleanup_payload))

    return {"message": f"Compiler '{compiler_id}' deleted and cleanup queued"}


@app.post("/compilers/{compiler_id}/build")
async def trigger_build(compiler_id: str, db: Session = Depends(get_db)):
    """Manually trigger a rebuild of the compiler's Docker image."""
    compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()

    if not compiler:
        raise HTTPException(status_code=404, detail=f"Compiler '{compiler_id}' not found")

    # Update build status to pending
    from sqlalchemy import func
    compiler.build_status = 'pending'
    compiler.build_error = None
    compiler.updated_at = func.now()
    db.commit()

    # Queue build job
    build_payload = {"compiler_id": compiler_id, "action": "build"}
    REDIS_CONN.lpush(REDIS_BUILD_QUEUE_NAME, json.dumps(build_payload))

    return {"message": f"Build queued for compiler '{compiler_id}'"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
