export type BuildStatus = 'pending' | 'building' | 'ready' | 'failed';

export interface Compiler {
  id: string;
  name: string;
  dockerfile_content: string;
  run_command: string[];
  image_tag: string;
  version: string | null;
  memory_limit: string;
  cpu_limit: string;
  timeout_seconds: number;
  enabled: boolean;
  build_status: BuildStatus;
  build_error: string | null;
  created_at: string;
  updated_at: string;
  built_at: string | null;
}

export interface CreateCompilerRequest {
  id: string;
  name: string;
  dockerfile_content: string;
  run_command: string[];
  version?: string;
  memory_limit?: string;
  cpu_limit?: string;
  timeout_seconds?: number;
}

export interface UpdateCompilerRequest {
  name?: string;
  dockerfile_content?: string;
  run_command?: string[];
  version?: string;
  memory_limit?: string;
  cpu_limit?: string;
  timeout_seconds?: number;
  enabled?: boolean;
}
