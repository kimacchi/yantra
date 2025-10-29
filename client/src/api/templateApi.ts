import axios from 'axios';
import { DockerfileTemplate, CreateTemplateRequest } from '../types/template';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const templateApi = {
  // List all templates
  listTemplates: async (category?: string, officialOnly: boolean = false): Promise<DockerfileTemplate[]> => {
    const response = await api.get<DockerfileTemplate[]>('/templates', {
      params: {
        category,
        official_only: officialOnly
      },
    });
    return response.data;
  },

  // Get single template
  getTemplate: async (id: string): Promise<DockerfileTemplate> => {
    const response = await api.get<DockerfileTemplate>(`/templates/${id}`);
    return response.data;
  },

  // Create new template (admin only)
  createTemplate: async (data: CreateTemplateRequest): Promise<DockerfileTemplate> => {
    const response = await api.post<DockerfileTemplate>('/templates', data);
    return response.data;
  },

  // Delete template (admin only)
  deleteTemplate: async (id: string): Promise<void> => {
    await api.delete(`/templates/${id}`);
  },
};
