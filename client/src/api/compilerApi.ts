import axios from 'axios';
import { Compiler, CreateCompilerRequest, UpdateCompilerRequest } from '../types/compiler';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const compilerApi = {
  // List all compilers
  listCompilers: async (enabledOnly: boolean = false): Promise<Compiler[]> => {
    const response = await api.get<Compiler[]>('/compilers', {
      params: { enabled_only: enabledOnly },
    });
    return response.data;
  },

  // Get single compiler
  getCompiler: async (id: string): Promise<Compiler> => {
    const response = await api.get<Compiler>(`/compilers/${id}`);
    return response.data;
  },

  // Create new compiler
  createCompiler: async (data: CreateCompilerRequest): Promise<Compiler> => {
    const response = await api.post<Compiler>('/compilers', data);
    return response.data;
  },

  // Update compiler
  updateCompiler: async (id: string, data: UpdateCompilerRequest): Promise<Compiler> => {
    const response = await api.put<Compiler>(`/compilers/${id}`, data);
    return response.data;
  },

  // Delete compiler
  deleteCompiler: async (id: string): Promise<void> => {
    await api.delete(`/compilers/${id}`);
  },

  // Trigger manual rebuild
  rebuildCompiler: async (id: string): Promise<void> => {
    await api.post(`/compilers/${id}/build`);
  },

  // Get build logs
  getBuildLogs: async (id: string): Promise<{
    compiler_id: string;
    compiler_name: string;
    build_status: string;
    build_logs: string;
    build_error: string | null;
    built_at: string | null;
    updated_at: string;
  }> => {
    const response = await api.get(`/compilers/${id}/logs`);
    return response.data;
  },
};
