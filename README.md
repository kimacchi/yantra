# Yantra

A secure, isolated code execution system that allows users to submit code for compilation and execution in sandboxed environments. Yantra provides an API that accepts code submissions and runs them in isolated Docker containers with security restrictions to prevent malicious code execution.

## 🎯 Overview

Yantra is an open-source code execution platform designed for safe code evaluation. It's perfect for online judges, coding playgrounds, or any application that needs to run untrusted code.

## ✨ Current Features (POC)

The current version is a proof of concept that demonstrates the core architecture:

- **Secure Code Execution**: Code runs in isolated Docker containers with multiple security layers
- **RESTful API**: Submit code and retrieve results via simple HTTP endpoints
- **Queue-Based Processing**: Asynchronous job processing using Redis
- **Persistent Storage**: All submissions and results are stored in PostgreSQL
- **Security Measures**:
  - gVisor runtime for additional sandboxing
  - No network access
  - Memory and CPU limits
  - Read-only filesystem
  - Timeout protection (10 seconds)

## 🚀 Upcoming Features

The full version will include:

- **Custom Runtime Environments**: Define your own compiler/runtime environments using Dockerfiles
- **Multi-Language Support**: Seamlessly support Python, JavaScript, C++, and any other language
- **Web UI**: Configure languages, compilers, and runtime settings through a modern web interface
- **Dynamic Compiler Registration**: Add new language support without code changes
- **Advanced Security Controls**: Fine-tune security policies per language/environment
- **Resource Management**: Configurable limits on memory, CPU, execution time, and disk space

## 🏗️ Architecture

Yantra follows a microservices architecture:

```
┌─────────────────┐
│   FastAPI API   │◄───── Submit code, check results
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
    ┌────────┐      ┌──────────┐
    │ Redis  │      │PostgreSQL│
    │ Queue  │      │  Database │
    └────┬───┘      └─────┬────┘
         │                │
         │                │
         ▼                │
    ┌──────────┐         │
    │  Worker  │─────────┘
    └─────┬────┘
          │
          ▼
    ┌─────────────────┐
    │  Docker (gVisor) │
    │  Isolated Exec   │
    └──────────────────┘
```

### Components

- **API Service**: FastAPI application that handles code submissions and result retrieval
- **Worker Service**: Processes jobs from the queue and executes code in Docker containers
- **PostgreSQL**: Stores job metadata, code, and results
- **Redis**: Message queue for asynchronous job processing

## 🔒 Security Features

Yantra implements multiple layers of security:

1. **gVisor Runtime**: Adds an additional layer of kernel protection
2. **Network Isolation**: Containers have no network access
3. **Resource Limits**: Memory (512MB) and CPU (1 core) restrictions
4. **Read-Only Filesystem**: Prevents file system modifications
5. **Execution Timeout**: 10-second limit to prevent infinite loops
6. **STDIN-Based Execution**: Code is passed via stdin, eliminating file system race conditions

## 📋 Prerequisites

- Docker and Docker Compose
- gVisor runtime (for production deployments)
- Linux operating system (currently tested on Linux)

## 🛠️ Installation & Usage

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/yantra.git
cd yantra
```

2. Start all services:
```bash
docker-compose up
```

This will start:
- PostgreSQL database on port `5432`
- Redis queue on port `6379`
- API server on port `8000`
- Worker service (consumes jobs from the queue)

### Usage

#### Submit Code

Send a POST request to submit code for execution:

```bash
curl -X POST http://localhost:8000/submit \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")",
    "language": "python"
  }'
```

Response:
```json
{
  "message": "Job submitted",
  "job_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### Get Results

Retrieve the execution results using the job ID:

```bash
curl http://localhost:8000/results/123e4567-e89b-12d3-a456-426614174000
```

Response:
```json
{
  "status": "COMPLETED",
  "stdout": "Hello, World!\n",
  "stderr": null,
  "completed_at": "2024-01-15T10:30:00"
}
```

### Status Codes

- `PENDING`: Job is in queue, waiting to be processed
- `RUNNING`: Job is currently executing
- `COMPLETED`: Job completed successfully
- `ERROR`: Execution encountered an error
- `TIMEOUT`: Execution exceeded the time limit
- `NOT_FOUND`: Job ID not found in database

## 📝 API Endpoints

### POST `/submit`

Submit code for execution.

**Request Body:**
```json
{
  "code": "string",
  "language": "string"
}
```

**Response:**
```json
{
  "message": "Job submitted",
  "job_id": "uuid"
}
```

### GET `/results/{job_id}`

Retrieve execution results.

**Response:**
```json
{
  "status": "string",
  "stdout": "string",
  "stderr": "string",
  "completed_at": "timestamp"
}
```

## 🗂️ Project Structure

```
yantra/
├── api/
│   ├── main.py          # FastAPI application
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # API container image
├── worker/
│   ├── worker.py        # Worker service
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Worker container image
├── docker-compose.yml   # Service orchestration
├── init.sql             # Database schema
└── README.md            # This file
```

## 🧪 Current Implementation

The POC currently hardcodes Python 3.11 execution using stdin-based approach:

```python
docker run --runtime=runsc --rm --network=none \
  --memory=512m --cpus=1 --read-only \
  python:3.11-slim python -
```

This approach:
- ✅ Eliminates file system operations
- ✅ Simplifies cleanup (containers auto-remove)
- ✅ Reduces attack surface
- ❌ Currently limited to Python only

## 🔮 Roadmap

### Phase 2: Multi-Language Support
- Dynamic language detection and execution
- Support for JavaScript (Node.js), C++, and more
- Build steps for compiled languages

### Phase 3: Custom Runtimes
- Dockerfile-based custom compiler definitions
- Plugin system for adding new languages
- Configuration-driven runtime selection

### Phase 4: Web UI
- Dashboard for monitoring submissions
- Language and compiler management interface
- Real-time execution logs
- User management and authentication

### Phase 5: Enterprise Features
- Kubernetes deployment support
- Horizontal scaling
- Advanced resource quotas
- Audit logging

## 🤝 Contributing

Contributions are welcome! This is an open-source project. Feel free to open issues, submit pull requests, or start discussions about new features.

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [gVisor](https://gvisor.dev/) - Application kernel for security
- [Docker](https://www.docker.com/) - Container platform
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Redis](https://redis.io/) - Message broker

