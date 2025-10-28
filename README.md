# Yantra

**Yantra** is a secure, open-source code execution platform that allows you to run untrusted code in isolated Docker containers. It provides a complete system for managing runtime environments (compilers) and executing user-submitted code safely.

Perfect for online coding judges, programming playgrounds, competitive programming platforms, or any application that needs to execute arbitrary code securely.

## Features

- **Dynamic Compiler Management** - Create, update, and delete runtime environments via API or web UI
- **Custom Dockerfiles** - Define any language/runtime using standard Dockerfiles
- **Secure Execution** - Multi-layered sandboxing with gVisor, network isolation, resource limits, and read-only filesystems
- **Web UI** - Modern React application for managing compilers with Monaco Editor
- **RESTful API** - Complete CRUD operations for compilers and code submissions
- **Async Processing** - Redis-based job queue with background worker
- **Auto-Build System** - Automatically builds Docker images from your Dockerfiles
- **Real-time Status** - Monitor build status and execution results

## Architecture

Yantra uses a microservices architecture with 5 main components:

```
┌──────────────┐
│ React Client │  (Port 3000)
│  Web UI      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  FastAPI API │  (Port 8000)
│   + SQLAlchemy
└──────┬───────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
  ┌────────┐      ┌──────────┐
  │ Redis  │      │PostgreSQL│
  │ Queue  │      │  +Models │
  └────┬───┘      └─────┬────┘
       │                │
       ▼                ▼
  ┌──────────────────────┐
  │  Worker Service      │
  │  - Builds images     │
  │  - Runs code         │
  │  - Cleans up         │
  └──────────────────────┘
       │
       ▼
  ┌─────────────────┐
  │ Docker + gVisor │
  │ Isolated Exec   │
  └─────────────────┘
```

### Components

1. **React Client** - Web UI for managing compilers (create/edit/delete/view)
2. **FastAPI API** - REST API with SQLAlchemy ORM for database operations
3. **PostgreSQL** - Stores compilers, submissions, and results
4. **Redis** - Message queues for code execution jobs and image builds
5. **Worker** - Processes jobs, builds Docker images, executes code

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm (for web UI)
- gVisor runtime (optional, for enhanced security)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/yantra.git
cd yantra
```

2. **Start backend services:**
```bash
docker-compose up --build
```

This starts:
- PostgreSQL on port `5432`
- Redis on port `6379`
- API server on port `8000`
- Worker service (background)

3. **Start the web UI (optional):**
```bash
cd client
npm install
npm run dev
```

Web UI will be available at `http://localhost:3000`

4. **Wait for initial build:**

The system seeds a Python 3.11 compiler on first startup. Watch the logs:
```bash
docker-compose logs -f worker
```

Wait for: `Successfully built compiler: python-3.11`

## Usage

### Option 1: Web UI

Open `http://localhost:3000` in your browser.

- **View Compilers** - See all runtime environments with real-time status
- **Create Compiler** - Click "New Compiler" and fill in the form with your Dockerfile
- **Edit Compiler** - Click "Edit" on any compiler card
- **Delete Compiler** - Click "Delete" (with confirmation dialog)
- **Rebuild** - Manually trigger image rebuild

The UI auto-refreshes every 5 seconds to show build progress.

### Option 2: REST API

#### List All Compilers

```bash
curl http://localhost:8000/compilers
```

#### Get Single Compiler

```bash
curl http://localhost:8000/compilers/python-3.11
```

#### Create a New Compiler

```bash
curl -X POST http://localhost:8000/compilers \
  -H "Content-Type: application/json" \
  -d '{
    "id": "node-20",
    "name": "Node.js 20",
    "dockerfile_content": "FROM node:20-slim\nWORKDIR /sandbox\nRUN adduser --disabled-password --gecos \"\" --uid 1000 sandbox\nUSER sandbox\nCMD [\"node\", \"-\"]",
    "run_command": ["node", "-"],
    "version": "20.0.0",
    "memory_limit": "256m",
    "cpu_limit": "0.5",
    "timeout_seconds": 5
  }'
```

The worker will automatically start building the Docker image.

#### Update a Compiler

```bash
curl -X PUT http://localhost:8000/compilers/node-20 \
  -H "Content-Type: application/json" \
  -d '{
    "memory_limit": "512m",
    "timeout_seconds": 10
  }'
```

If you update `dockerfile_content` or `run_command`, it triggers a rebuild.

#### Delete a Compiler

```bash
curl -X DELETE http://localhost:8000/compilers/node-20
```

This queues the Docker image for cleanup.

#### Trigger Manual Rebuild

```bash
curl -X POST http://localhost:8000/compilers/python-3.11/build
```

#### Submit Code for Execution

```bash
curl -X POST http://localhost:8000/submit \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, Yantra!\")",
    "language": "python-3.11"
  }'
```

Response:
```json
{
  "message": "Job submitted",
  "job_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Get Execution Results

```bash
curl http://localhost:8000/results/123e4567-e89b-12d3-a456-426614174000
```

Response:
```json
{
  "status": "COMPLETED",
  "stdout": "Hello, Yantra!\n",
  "stderr": null,
  "completed_at": "2024-01-15T10:30:00"
}
```

## API Reference

### Compiler Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/compilers` | List all compilers (supports `?enabled_only=true`) |
| `POST` | `/compilers` | Create a new compiler |
| `GET` | `/compilers/{id}` | Get compiler details |
| `PUT` | `/compilers/{id}` | Update compiler configuration |
| `DELETE` | `/compilers/{id}` | Delete compiler and cleanup image |
| `POST` | `/compilers/{id}/build` | Manually trigger rebuild |

### Submission Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/submit` | Submit code for execution |
| `GET` | `/results/{job_id}` | Get execution results |

### Data Models

#### Compiler

```typescript
{
  id: string;                    // Unique identifier (e.g., "python-3.11")
  name: string;                  // Display name
  dockerfile_content: string;    // Complete Dockerfile
  run_command: string[];         // Command to execute code (e.g., ["python", "-"])
  image_tag: string;             // Docker image name (auto-generated)
  version: string | null;        // Optional version tag
  memory_limit: string;          // Memory limit (e.g., "512m")
  cpu_limit: string;             // CPU limit (e.g., "1")
  timeout_seconds: number;       // Execution timeout
  enabled: boolean;              // Whether compiler accepts submissions
  build_status: string;          // "pending" | "building" | "ready" | "failed"
  build_error: string | null;    // Error message if build failed
  created_at: string;            // Timestamp
  updated_at: string;            // Timestamp
  built_at: string | null;       // Build completion timestamp
}
```

#### Submission

```typescript
{
  code: string;                  // Source code to execute
  language: string;              // Compiler ID (must be enabled and ready)
}
```

#### Result

```typescript
{
  status: string;                // "PENDING" | "RUNNING" | "COMPLETED" | "ERROR" | "TIMEOUT"
  stdout: string | null;         // Standard output
  stderr: string | null;         // Standard error
  completed_at: string | null;   // Completion timestamp
}
```

## Creating Compilers

### Dockerfile Requirements

Your Dockerfile should:
1. Use the `-i` flag for reading code from stdin
2. Include a non-root user for security (optional but recommended)
3. Set a working directory
4. Specify the command to execute code

### Example: Python with NumPy

```dockerfile
FROM python:3.11-slim
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
RUN pip install --no-cache-dir numpy pandas
USER sandbox
CMD ["python", "-"]
```

**Run command:** `["python", "-"]`

### Example: Node.js with TypeScript

```dockerfile
FROM node:20-alpine
WORKDIR /sandbox
RUN adduser -D -u 1000 sandbox && chown sandbox:sandbox /sandbox
RUN npm install -g typescript ts-node
USER sandbox
CMD ["ts-node"]
```

**Run command:** `["ts-node"]`

### Example: Go

```dockerfile
FROM golang:1.21-alpine
WORKDIR /sandbox
RUN adduser -D -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["go", "run", "-"]
```

**Run command:** `["go", "run", "-"]`

### Example: Rust

```dockerfile
FROM rust:1.75-slim
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
# Note: Rust requires file-based compilation, may need adjustments
```

## Database Schema

### `compilers` Table

```sql
CREATE TABLE compilers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dockerfile_content TEXT NOT NULL,
    run_command TEXT NOT NULL,              -- JSON array
    image_tag VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    memory_limit VARCHAR(20) DEFAULT '512m',
    cpu_limit VARCHAR(20) DEFAULT '1',
    timeout_seconds INTEGER DEFAULT 10,
    enabled BOOLEAN DEFAULT TRUE,
    build_status VARCHAR(50) DEFAULT 'pending',
    build_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    built_at TIMESTAMP WITH TIME ZONE
);
```

### `submissions` Table

```sql
CREATE TABLE submissions (
    job_id UUID PRIMARY KEY,
    code TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    output_stdout TEXT,
    output_stderr TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (language) REFERENCES compilers(id)
);
```

## Security Features

Yantra implements defense-in-depth security:

### Container Security
- **gVisor Runtime** - Application kernel providing additional isolation
- **Network Isolation** - `--network=none` prevents network access
- **Read-Only Filesystem** - `--read-only` prevents file modifications
- **Resource Limits** - Configurable memory and CPU caps per compiler
- **Execution Timeout** - Prevents infinite loops and resource exhaustion
- **Non-Root User** - Code runs as unprivileged user inside container

### Application Security
- **STDIN-Based Execution** - Code passed via stdin eliminates filesystem races
- **SQLAlchemy ORM** - Protects against SQL injection
- **Validation** - Compiler status and availability checks before execution
- **Automatic Cleanup** - Containers removed after execution

## Project Structure

```
yantra/
├── api/
│   ├── main.py              # FastAPI application
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # Database session management
│   ├── requirements.txt
│   └── Dockerfile
├── worker/
│   ├── worker.py            # Job processor and image builder
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # Database session management
│   ├── requirements.txt
│   └── Dockerfile
├── client/
│   ├── src/
│   │   ├── api/             # Axios API client
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── types/           # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml
├── init.sql
├── MIGRATION.md
└── README.md
```

## Troubleshooting

### "Relation 'compilers' does not exist"

Your database was initialized before the schema changes. Reset it:

```bash
docker-compose down -v
docker-compose up --build
```

See `MIGRATION.md` for details.

### Build Status Stuck on "building"

Check worker logs for build errors:

```bash
docker-compose logs worker
```

If failed, check the `build_error` field:

```bash
curl http://localhost:8000/compilers/{compiler-id}
```

Manually trigger rebuild:

```bash
curl -X POST http://localhost:8000/compilers/{compiler-id}/build
```

### Code Execution Returns "not ready"

The compiler image hasn't finished building. Check status:

```bash
curl http://localhost:8000/compilers
```

Wait for `build_status: "ready"` before submitting code.

## Technology Stack

- FastAPI - Modern async web framework
- SQLAlchemy - ORM for database operations
- PostgreSQL - Relational database
- Redis - Message broker and job queue
- Docker - Container platform
- gVisor - Application kernel for sandboxing
- React - For frontend

## Contributing

Contributions are welcome! Please feel free to submit pull requests, open issues, or suggest new features.

## License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## Acknowledgments

Built with amazing open-source tools:
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Docker](https://www.docker.com/)
- [gVisor](https://gvisor.dev/)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [React](https://react.dev/)
- [Monaco Editor](https://microsoft.github.io/monaco-editor/)
- [Tailwind CSS](https://tailwindcss.com/)
