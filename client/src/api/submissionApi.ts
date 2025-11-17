import axios from 'axios';
import { SubmissionRequest, SubmissionResponse, ExecutionResult } from '../types/submission';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const submissionApi = {
  // Submit code for execution
  submitCode: async (data: SubmissionRequest): Promise<SubmissionResponse> => {
    const formData = new FormData();
    formData.append('code', data.code);
    formData.append('language', data.language);

    const response = await api.post<SubmissionResponse>('/submit', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Get execution results
  getResults: async (jobId: string): Promise<ExecutionResult> => {
    const response = await api.get<ExecutionResult>(`/submit/results/${jobId}`);
    return response.data;
  },
};
