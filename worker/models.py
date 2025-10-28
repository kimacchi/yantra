"""SQLAlchemy models for Yantra."""
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class Compiler(Base):
    """Compiler/Runtime configuration model."""
    __tablename__ = "compilers"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    dockerfile_content = Column(Text, nullable=False)
    run_command = Column(Text, nullable=False)  # JSON string
    image_tag = Column(String(255), nullable=False)
    version = Column(String(50))
    memory_limit = Column(String(20), default='512m')
    cpu_limit = Column(String(20), default='1')
    timeout_seconds = Column(Integer, default=10)
    enabled = Column(Boolean, default=True)
    build_status = Column(String(50), default='pending')
    build_error = Column(Text)
    build_logs = Column(Text)  # Full Docker build output
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    built_at = Column(TIMESTAMP(timezone=True))


class Submission(Base):
    """Code submission model."""
    __tablename__ = "submissions"

    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(Text, nullable=False)
    language = Column(String(50), ForeignKey('compilers.id'), nullable=False)
    status = Column(String(50), nullable=False, default='PENDING')
    output_stdout = Column(Text)
    output_stderr = Column(Text)
    uploaded_files = Column(Text)  # JSON array of file metadata
    files_directory = Column(String(500))  # Path to job's file directory
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    completed_at = Column(TIMESTAMP(timezone=True))
