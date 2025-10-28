# File Upload Feature

## Overview

The Yantra platform now supports per-submission file uploads. Users can upload files along with their code, and these files will be mounted read-only into the execution container at `/data/`.

## Features

- **Per-submission uploads**: Each code submission can have different files
- **Multiple file support**: Up to 10 files per submission
- **Size limits**: 25MB total per submission
- **File type validation**: Whitelist of allowed extensions
- **Security**: Files mounted read-only, immediate cleanup after execution
- **Automatic cleanup**: Files deleted immediately after code execution completes

## Usage

### API Endpoint

**POST** `/api/submit`

Content-Type: `multipart/form-data`

**Parameters:**
- `code` (required): Source code to execute
- `language` (required): Programming language identifier (e.g., "python")
- `files` (optional): One or more files to upload

### Example with cURL

```bash
# Upload with a single file
curl -X POST http://localhost:8000/api/submit \
  -F "code=with open('/data/input.txt') as f: print(f.read())" \
  -F "language=python" \
  -F "files=@input.txt"

# Upload with multiple files
curl -X POST http://localhost:8000/api/submit \
  -F "code=import json; data = json.load(open('/data/config.json')); print(data)" \
  -F "language=python" \
  -F "files=@config.json" \
  -F "files=@data.csv"
```

### Accessing Files in Code

Files are available in the `/data/` directory inside the container:

**Python:**
```python
with open('/data/input.txt', 'r') as f:
    content = f.read()
    print(content)
```

**JavaScript (Node.js):**
```javascript
const fs = require('fs');
const data = fs.readFileSync('/data/data.json', 'utf8');
console.log(data);
```

**Go:**
```go
package main
import (
    "fmt"
    "os"
)
func main() {
    data, _ := os.ReadFile("/data/input.txt")
    fmt.Println(string(data))
}
```

## Configuration

### Limits (defined in `api/config.py`)

- **MAX_UPLOAD_SIZE**: 25MB (26,214,400 bytes)
- **MAX_FILES_PER_SUBMISSION**: 10 files
- **EXECUTOR_JOBS_DIR**: `/tmp/executor_jobs`
- **CONTAINER_MOUNT_PATH**: `/data`

### Allowed Extensions

The following file extensions are whitelisted:

- Text: `.txt`, `.md`, `.log`
- Data: `.json`, `.csv`, `.tsv`, `.xml`, `.yaml`, `.yml`, `.dat`
- Config: `.ini`, `.conf`, `.properties`
- Web: `.html`, `.css`, `.js`
- Database: `.sql`

## Security Features

### 1. Filename Sanitization
- Path components stripped (no `../` attacks)
- Special characters replaced with underscores
- Only alphanumeric, dots, hyphens, and underscores allowed

### 2. File Type Validation
- Extension whitelist enforcement
- Rejects executable files and dangerous extensions

### 3. Size Validation
- Individual file size checked
- Cumulative total size enforced (25MB limit)
- Empty files rejected

### 4. Container Isolation
- Files mounted **read-only** (`:ro` flag)
- No network access in containers
- gVisor runtime for additional isolation
- Read-only filesystem except `/data`

### 5. Immediate Cleanup
- Files deleted right after execution
- Cleanup on success, timeout, or error
- No persistent storage of uploaded files

## Database Schema

### New Columns in `submissions` Table

```sql
uploaded_files TEXT;          -- JSON array of file metadata
files_directory VARCHAR(500); -- Path to job's file directory
```

### File Metadata Format

```json
[
  {
    "filename": "input.txt",
    "size": 1024,
    "mime_type": "text/plain"
  },
  {
    "filename": "data.csv",
    "size": 2048,
    "mime_type": "text/csv"
  }
]
```

## Migration

Run the migration script to add the new columns:

```bash
# Connect to the database
docker exec -i yantra-db-1 psql -U admin -d yantra_db < add_file_upload_columns.sql

# Or manually:
docker exec -it yantra-db-1 psql -U admin -d yantra_db
```

```sql
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS uploaded_files TEXT;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS files_directory VARCHAR(500);
```

## Architecture

### File Flow

```
1. User uploads files via API → POST /api/submit
2. API validates files (size, type, count)
3. API saves files to /tmp/executor_jobs/<job_id>/
4. API stores metadata in database
5. Job queued to Redis
6. Worker receives job
7. Worker mounts directory to /data (read-only)
8. Code executes with access to /data/
9. Worker captures output
10. Worker deletes /tmp/executor_jobs/<job_id>/ immediately
```

### Directory Structure

```
/tmp/executor_jobs/
├── <job_id_1>/
│   ├── file1.txt
│   └── file2.json
├── <job_id_2>/
│   └── data.csv
└── ...
```

Each job gets its own isolated directory that is deleted after execution.

## Error Handling

### Validation Errors (400)

- **Too many files**: More than 10 files uploaded
- **File too large**: Total size exceeds 25MB
- **Invalid extension**: File extension not in whitelist
- **Empty file**: File has zero bytes

### Example Error Response

```json
{
  "detail": "File extension not allowed for 'script.exe'. Allowed: .txt, .json, .csv, ..."
}
```

## API Response

### Submission Response

```json
{
  "message": "Job submitted",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Results Response (with files)

```json
{
  "status": "COMPLETED",
  "stdout": "File content here...",
  "stderr": null,
  "completed_at": "2025-10-29T01:23:45.123456",
  "uploaded_files": [
    {
      "filename": "input.txt",
      "size": 1024,
      "mime_type": "text/plain"
    }
  ]
}
```

## Testing

### Test File Upload

1. Create a test file:
```bash
echo "Hello from file!" > test.txt
```

2. Submit with file:
```bash
curl -X POST http://localhost:8000/api/submit \
  -F "code=print(open('/data/test.txt').read())" \
  -F "language=python" \
  -F "files=@test.txt"
```

3. Get results:
```bash
curl http://localhost:8000/api/submit/results/<job_id>
```

### Test Edge Cases

```bash
# Test size limit (should fail)
dd if=/dev/zero of=large.bin bs=1M count=30
curl -X POST http://localhost:8000/api/submit \
  -F "code=print('test')" \
  -F "language=python" \
  -F "files=@large.bin"

# Test invalid extension (should fail)
echo "test" > script.exe
curl -X POST http://localhost:8000/api/submit \
  -F "code=print('test')" \
  -F "language=python" \
  -F "files=@script.exe"

# Test multiple files
curl -X POST http://localhost:8000/api/submit \
  -F "code=import os; print(os.listdir('/data'))" \
  -F "language=python" \
  -F "files=@file1.txt" \
  -F "files=@file2.json" \
  -F "files=@file3.csv"
```

## Troubleshooting

### Files not accessible in container

**Check:**
1. Volume mount in `docker-compose.yml` is active
2. `/tmp/executor_jobs/` directory exists
3. File was saved to correct directory
4. Path in code is `/data/filename`, not `/tmp/executor_jobs/...`

### Permission errors

The `/tmp/executor_jobs/` directory is owned by root (created by Docker). This is normal and expected. The API and worker services have the necessary permissions through Docker volume mounts.

### Files persist after execution

Files should be deleted immediately. If they persist:
1. Check worker logs for cleanup errors
2. Ensure `shutil.rmtree()` is executing
3. Check for exceptions during execution

## Future Enhancements

Possible future improvements:

1. **Streaming uploads** for large files
2. **Binary file support** (images, PDFs)
3. **Archive support** (zip, tar)
4. **File retention** for debugging (configurable)
5. **Per-compiler file limits** (different limits for different languages)
6. **Virus scanning** integration
7. **File preview** in results API
8. **Compression** before storage

## Related Files

### API
- `api/config.py` - Configuration constants
- `api/models/database.py` - Database model
- `api/models/schemas.py` - Pydantic schemas
- `api/controllers/submission_controller.py` - File handling logic
- `api/routers/submissions.py` - Multipart endpoint

### Worker
- `worker/worker.py` - Volume mount and cleanup
- `worker/models.py` - Database model

### Infrastructure
- `docker-compose.yml` - Volume mounts
- `add_file_upload_columns.sql` - Migration script

## Support

For issues or questions:
- Check Swagger docs: http://localhost:8000/docs
- Review worker logs: `docker logs yantra-worker-1`
- Review API logs: `docker logs yantra-api-1`
