import redis
import json
import subprocess
import os
import time
import sys
import tempfile
from sqlalchemy import func

from database import get_db_session
from models import Compiler, Submission

# --- Config ---
REDIS_CONN = redis.Redis(host='queue', port=6379, db=0)
REDIS_QUEUE_NAME = "job_queue"
REDIS_BUILD_QUEUE_NAME = "build_queue"


def get_compiler_config(language):
    """Fetch compiler configuration from database."""
    with get_db_session() as db:
        compiler = db.query(Compiler).filter(
            Compiler.id == language,
            Compiler.enabled == True,
            Compiler.build_status == 'ready'
        ).first()

        if not compiler:
            return None

        return {
            "image_tag": compiler.image_tag,
            "run_command": json.loads(compiler.run_command),
            "memory_limit": compiler.memory_limit,
            "cpu_limit": compiler.cpu_limit,
            "timeout_seconds": compiler.timeout_seconds
        }


def build_compiler(compiler_id):
    """Build Docker image for a compiler from its Dockerfile."""
    print(f"Building compiler: {compiler_id}")

    try:
        # 1. Update status to 'building' and fetch Dockerfile
        with get_db_session() as db:
            compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()
            if not compiler:
                print(f"ERROR: Compiler {compiler_id} not found", file=sys.stderr)
                return

            compiler.build_status = 'building'
            compiler.updated_at = func.now()
            db.commit()

            dockerfile_content = compiler.dockerfile_content
            image_tag = compiler.image_tag

        # 2. Create temporary directory for build context
        with tempfile.TemporaryDirectory() as build_dir:
            dockerfile_path = os.path.join(build_dir, "Dockerfile")

            # Write Dockerfile
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)

            # 3. Build the image
            build_command = [
                "docker", "build",
                "-t", image_tag,
                build_dir
            ]

            process = subprocess.run(
                build_command,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for builds
            )

            # 4. Update database with result
            with get_db_session() as db:
                compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()
                if compiler:
                    if process.returncode == 0:
                        # Build succeeded
                        compiler.build_status = 'ready'
                        compiler.build_error = None
                        compiler.built_at = func.now()
                        compiler.updated_at = func.now()
                        print(f"Successfully built compiler: {compiler_id} -> {image_tag}")
                    else:
                        # Build failed
                        error_msg = process.stderr or process.stdout
                        compiler.build_status = 'failed'
                        compiler.build_error = error_msg
                        compiler.updated_at = func.now()
                        print(f"Failed to build compiler {compiler_id}: {error_msg}", file=sys.stderr)

    except subprocess.TimeoutExpired:
        error_msg = "Build timed out after 10 minutes"
        with get_db_session() as db:
            compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()
            if compiler:
                compiler.build_status = 'failed'
                compiler.build_error = error_msg
                compiler.updated_at = func.now()
        print(f"Build timeout for compiler {compiler_id}", file=sys.stderr)
    except Exception as e:
        error_msg = str(e)
        with get_db_session() as db:
            compiler = db.query(Compiler).filter(Compiler.id == compiler_id).first()
            if compiler:
                compiler.build_status = 'failed'
                compiler.build_error = error_msg
                compiler.updated_at = func.now()
        print(f"Build error for compiler {compiler_id}: {e}", file=sys.stderr)


def cleanup_compiler(compiler_id, image_tag):
    """Remove Docker image for a deleted compiler."""
    print(f"Cleaning up compiler: {compiler_id} (image: {image_tag})")
    try:
        # Remove the Docker image
        cleanup_command = ["docker", "rmi", "-f", image_tag]
        process = subprocess.run(
            cleanup_command,
            capture_output=True,
            text=True,
            timeout=60
        )

        if process.returncode == 0:
            print(f"Successfully removed image: {image_tag}")
        else:
            # Image might not exist, which is fine
            print(f"Could not remove image {image_tag}: {process.stderr}")

    except Exception as e:
        print(f"Cleanup error for {image_tag}: {e}", file=sys.stderr)


def run_job(job_id, code, language):
    """Execute user code in an isolated Docker container."""
    try:
        # 1. Update DB to 'RUNNING'
        with get_db_session() as db:
            submission = db.query(Submission).filter(Submission.job_id == job_id).first()
            if submission:
                submission.status = 'RUNNING'

        # 2. Get compiler configuration
        compiler_config = get_compiler_config(language)
        if not compiler_config:
            raise Exception(f"Compiler for language '{language}' is not available or not ready")

        # 3. Build the Docker command with dynamic config
        docker_command = [
            "docker", "run",
            "--runtime=runsc",                              # Use gVisor
            "--rm",                                          # Clean up container
            "--network=none",                                # No network access
            f"--memory={compiler_config['memory_limit']}",  # Dynamic memory limit
            f"--cpus={compiler_config['cpu_limit']}",       # Dynamic CPU limit
            "--read-only",                                   # Make filesystem read-only
            "-i",                                            # Pass STDIN to container
            "-w", "/sandbox",                                # Set working directory
            compiler_config['image_tag']                     # Dynamic image
        ] + compiler_config['run_command']                   # Dynamic run command

        # 4. Execute the command
        process = subprocess.run(
            docker_command,
            input=code,
            capture_output=True,
            text=True,
            timeout=compiler_config['timeout_seconds']
        )

        stdout = process.stdout
        stderr = process.stderr

        # 5. Update DB to 'COMPLETED'
        with get_db_session() as db:
            submission = db.query(Submission).filter(Submission.job_id == job_id).first()
            if submission:
                submission.status = 'COMPLETED'
                submission.output_stdout = stdout
                submission.output_stderr = stderr
                submission.completed_at = func.now()

    except subprocess.TimeoutExpired:
        timeout = compiler_config.get('timeout_seconds', 10) if compiler_config else 10
        with get_db_session() as db:
            submission = db.query(Submission).filter(Submission.job_id == job_id).first()
            if submission:
                submission.status = 'TIMEOUT'
                submission.output_stderr = f'Execution timed out after {timeout} seconds.'
                submission.completed_at = func.now()
    except Exception as e:
        print(f"DEBUG: Job {job_id} failed: {e}", file=sys.stderr)
        with get_db_session() as db:
            submission = db.query(Submission).filter(Submission.job_id == job_id).first()
            if submission:
                submission.status = 'ERROR'
                submission.output_stderr = str(e)
                submission.completed_at = func.now()


def process_job_queue():
    """Check for and process a job from the job queue (non-blocking)."""
    job_data = REDIS_CONN.rpop(REDIS_QUEUE_NAME)
    if job_data:
        job = json.loads(job_data)
        job_id = job.get("job_id")
        code = job.get("code")
        language = job.get("language")
        print(f"Processing job: {job_id} (language: {language})")
        run_job(job_id, code, language)
        return True
    return False


def process_build_queue():
    """Check for and process a build/cleanup job from the build queue (non-blocking)."""
    build_data = REDIS_CONN.rpop(REDIS_BUILD_QUEUE_NAME)
    if build_data:
        build_job = json.loads(build_data)
        action = build_job.get("action")

        if action == "build":
            compiler_id = build_job.get("compiler_id")
            build_compiler(compiler_id)
        elif action == "cleanup":
            compiler_id = build_job.get("compiler_id")
            image_tag = build_job.get("image_tag")
            cleanup_compiler(compiler_id, image_tag)

        return True
    return False


def main():
    print("Worker started. Processing jobs and builds...")
    while True:
        # Process both queues in a round-robin fashion
        job_processed = process_job_queue()
        build_processed = process_build_queue()

        # If no work was done, sleep briefly to avoid tight loop
        if not job_processed and not build_processed:
            time.sleep(0.5)


if __name__ == "__main__":
    main()
