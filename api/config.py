"""Application configuration."""
import redis
from typing import Optional

# Redis Configuration
REDIS_HOST = "queue"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_QUEUE_NAME = "job_queue"
REDIS_BUILD_QUEUE_NAME = "build_queue"

# Database Configuration
DATABASE_URL = "postgresql://admin:admin@db/yantra_db"

# API Configuration
API_TITLE = "Yantra Code Execution API"
API_DESCRIPTION = """
Yantra is a secure code execution platform that supports multiple programming languages.

## Features

* **Submit Code**: Execute code in isolated Docker containers
* **Compiler Management**: Create and manage custom language runtimes
* **Real-time Status**: Check execution status and retrieve results
* **Dynamic Image Building**: Automatically build Docker images for new compilers

## Endpoints

### Submissions
* Submit code for execution
* Retrieve execution results

### Compilers
* Create, read, update, and delete compiler configurations
* Trigger manual builds
* List available compilers
"""
API_VERSION = "1.0.0"
API_CONTACT = {
    "name": "Yantra API Support",
    "url": "https://github.com/yourusername/yantra",
}
API_LICENSE = {
    "name": "MIT",
}

# Redis connection (singleton)
_redis_conn: Optional[redis.Redis] = None


def get_redis_connection() -> redis.Redis:
    """Get or create Redis connection."""
    global _redis_conn
    if _redis_conn is None:
        _redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    return _redis_conn
