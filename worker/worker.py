import redis
import psycopg2
import json
import subprocess
import os
import time
import sys

# --- Config ---
DB_CONN = "host=db dbname=yantra_db user=admin password=admin"
REDIS_CONN = redis.Redis(host='queue', port=6379, db=0)
REDIS_QUEUE_NAME = "job_queue"
# We need a shared volume for the worker to write code
# and for the docker run command to read it.

# --- POC Compiler Map ---
# Maps language string to the Docker image and run command
COMPILERS = {
    "python": {
        "image": "python:3.11-slim",
        "command": ["python", "main.py"]
    },
    "javascript": {
        "image": "node:20-slim",
        "command": ["node", "main.js"]
    },
    "cpp": {
        "image": "gcc:13",
        "command": ["./a.out"] # We'll need a build step
    }
}


def run_job(job_id, code):
    conn = psycopg2.connect(DB_CONN)
    cursor = conn.cursor()
    
    try:
        # 1. Update DB to 'RUNNING'
        cursor.execute(
            "UPDATE submissions SET status = %s WHERE job_id = %s",
            ('RUNNING', job_id)
        )
        conn.commit()

        # 2. Build the Docker command to read from stdin
        docker_command = [
            "docker", "run",
            "--runtime=runsc",    # Use gVisor!
            "--rm",               # Clean up container
            "--network=none",     # No network access
            "--memory=512m",      # Limit memory
            "--cpus=1",           # Limit CPU
            "--read-only",        # Make filesystem read-only
            "-i",                 # <-- Pass STDIN to the container
            "-w", "/sandbox",     # Set working directory
            "python:3.11-slim",   # Hardcoded image for POC
            "python", "-"         # <-- Tell python to read from STDIN
        ]

        # 3. Execute the command
        # We pass the 'code' directly to the process's stdin
        process = subprocess.run(
            docker_command,
            input=code,           # <-- This is the key change!
            capture_output=True,
            text=True,
            timeout=10 # 10-second timeout
        )

        stdout = process.stdout
        stderr = process.stderr

        # 4. Update DB to 'COMPLETED'
        cursor.execute(
            "UPDATE submissions SET status = %s, output_stdout = %s, output_stderr = %s, completed_at = CURRENT_TIMESTAMP WHERE job_id = %s",
            ('COMPLETED', stdout, stderr, job_id)
        )

    except subprocess.TimeoutExpired:
        cursor.execute(
            "UPDATE submissions SET status = %s, output_stderr = %s, completed_at = CURRENT_TIMESTAMP WHERE job_id = %s",
            ('TIMEOUT', 'Execution timed out after 10 seconds.', job_id)
        )
    except Exception as e:
        print(f"DEBUG: Job {job_id} failed: {e}", file=sys.stderr)
        cursor.execute(
            "UPDATE submissions SET status = %s, output_stderr = %s, completed_at = CURRENT_TIMESTAMP WHERE job_id = %s",
            ('ERROR', str(e), job_id)
        )
    finally:
        # 5. Clean up (no more files to delete!)
        conn.commit()
        cursor.close()
        conn.close()

def main():
    print("Worker started. Waiting for jobs...")
    while True:
        # Pop a job from the queue (blocking)
        _, job_data = REDIS_CONN.brpop(REDIS_QUEUE_NAME)
        job = json.loads(job_data)

        job_id = job.get("job_id")
        code = job.get("code")

        print(f"Running job: {job_id}")
        run_job(job_id, code)

if __name__ == "__main__":
    main()
