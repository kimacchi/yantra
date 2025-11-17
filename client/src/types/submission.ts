export interface SubmissionRequest {
  code: string;
  language: string;
}

export interface SubmissionResponse {
  job_id: string;
  message: string;
}

export interface ExecutionResult {
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'TIMEOUT' | 'ERROR' | 'NOT_FOUND';
  stdout: string | null;
  stderr: string | null;
  completed_at: string | null;
}
