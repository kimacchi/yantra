-- Compilers/Runtimes table
CREATE TABLE compilers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dockerfile_content TEXT NOT NULL,
    run_command TEXT NOT NULL, -- JSON array: ["python", "-"]
    image_tag VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    memory_limit VARCHAR(20) DEFAULT '512m',
    cpu_limit VARCHAR(20) DEFAULT '1',
    timeout_seconds INTEGER DEFAULT 10,
    enabled BOOLEAN DEFAULT TRUE,
    build_status VARCHAR(50) DEFAULT 'pending', -- pending, building, ready, failed
    build_error TEXT,
    build_logs TEXT, -- Full Docker build output (stdout and stderr combined)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    built_at TIMESTAMP WITH TIME ZONE
);

-- Submissions table
CREATE TABLE submissions (
    job_id UUID PRIMARY KEY,
    code TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    output_stdout TEXT,
    output_stderr TEXT,
    uploaded_files TEXT, -- JSON array of uploaded file metadata
    files_directory VARCHAR(500), -- Path to job-specific directory containing uploaded files
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (language) REFERENCES compilers(id)
);

-- Dockerfile Templates table
CREATE TABLE dockerfile_templates (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL, -- language, framework, tool, os
    dockerfile_template TEXT NOT NULL,
    default_run_command TEXT, -- JSON array suggestion: ["python", "-"]
    tags TEXT, -- JSON array for search/filtering: ["python", "data-science"]
    icon VARCHAR(50), -- emoji or icon identifier
    author VARCHAR(100) DEFAULT 'yantra',
    is_official BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for category-based filtering
CREATE INDEX idx_templates_category ON dockerfile_templates(category);

-- Create index for official templates
CREATE INDEX idx_templates_official ON dockerfile_templates(is_official);

-- Seed data: Python 3.11 compiler
INSERT INTO compilers (id, name, dockerfile_content, run_command, image_tag, build_status, enabled)
VALUES (
    'python-3.11',
    'Python 3.11',
    'FROM python:3.11-slim
WORKDIR /sandbox
RUN useradd -m -u 1000 sandbox && chown sandbox:sandbox /sandbox
USER sandbox
CMD ["python", "-"]',
    '["python", "-"]',
    'yantra-python-3.11:latest',
    'pending',
    TRUE
);
