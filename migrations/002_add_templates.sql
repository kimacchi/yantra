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
