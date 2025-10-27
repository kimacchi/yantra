CREATE TABLE submissions (
    job_id UUID PRIMARY KEY,
    code TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    output_stdout TEXT,
    output_stderr TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);
