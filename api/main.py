import uvicorn
import uuid
import json
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import psycopg2
import redis

# --- Config (In a real app, use env vars) ---
DB_CONN = "host=db dbname=yantra_db user=admin password=admin"
REDIS_CONN = redis.Redis(host='queue', port=6379, db=0)
REDIS_QUEUE_NAME = "job_queue"

app = FastAPI()

class Submission(BaseModel):
    code: str
    language: str # For POC, we'll just trust this

@app.post("/submit")
async def submit_code(submission: Submission):
    job_id = str(uuid.uuid4())

    # 1. Create job entry in Postgres
    conn = psycopg2.connect(DB_CONN)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO submissions (job_id, code, language, status) VALUES (%s, %s, %s, %s)",
        (job_id, submission.code, submission.language, 'PENDING')
    )
    conn.commit()
    cursor.close()
    conn.close()

    # 2. Create job payload for the queue
    job_payload = {
        "job_id": job_id,
        "code": submission.code,
        "language": submission.language
    }

    # 3. Push job to Redis queue
    REDIS_CONN.lpush(REDIS_QUEUE_NAME, json.dumps(job_payload))

    return {"message": "Job submitted", "job_id": job_id}

@app.get("/results/{job_id}")
async def get_results(job_id: str):
    conn = psycopg2.connect(DB_CONN)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status, output_stdout, output_stderr, completed_at FROM submissions WHERE job_id = %s",
        (job_id,)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        return {"status": "NOT_FOUND"}

    return {
        "status": result[0],
        "stdout": result[1],
        "stderr": result[2],
        "completed_at": result[3]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
