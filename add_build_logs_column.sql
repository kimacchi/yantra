-- Migration script to add build_logs column to compilers table
-- This script adds a new column to store full Docker build output

-- Add build_logs column to compilers table
ALTER TABLE compilers ADD COLUMN IF NOT EXISTS build_logs TEXT;

-- Add comment to document the column purpose
COMMENT ON COLUMN compilers.build_logs IS 'Full Docker build output (stdout and stderr combined)';

-- Optional: Create an index if you plan to search through logs (usually not needed)
-- CREATE INDEX IF NOT EXISTS idx_compilers_build_status ON compilers(build_status);

-- Verify the change
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'compilers'
  AND column_name = 'build_logs';
