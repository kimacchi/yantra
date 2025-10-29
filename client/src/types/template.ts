export interface DockerfileTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  dockerfile_template: string;
  default_run_command: string[] | null;
  tags: string[] | null;
  icon: string | null;
  author: string;
  is_official: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTemplateRequest {
  id: string;
  name: string;
  description: string;
  category: string;
  dockerfile_template: string;
  default_run_command?: string[];
  tags?: string[];
  icon?: string;
  author?: string;
  is_official?: boolean;
}
