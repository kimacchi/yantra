-- Migration script to add file upload columns to submissions table
-- Adds support for per-submission file uploads

-- Add uploaded_files column to store file metadata as JSON
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS uploaded_files TEXT;

-- Add files_directory column to store the path to job's file directory
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS files_directory VARCHAR(500);

-- Add comments to document the columns
COMMENT ON COLUMN submissions.uploaded_files IS 'JSON array of uploaded file metadata: [{"filename": "data.csv", "size": 1024, "mime_type": "text/csv"}]';
COMMENT ON COLUMN submissions.files_directory IS 'Path to job-specific directory containing uploaded files (e.g., /tmp/executor_jobs/<job_id>)';

-- Verify the changes
SELECT column_name, data_type, is_nullable, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'submissions'
  AND column_name IN ('uploaded_files', 'files_directory')
ORDER BY ordinal_position;
