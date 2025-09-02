import { APIError, ExecuteResponse, ProcessResponse, ResultResponse, StatusProcess, UploadResponse } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface healthCheck {
  message: string
}

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: APIError = await response.json().catch(() => ({
        detail: 'Internal server Error'
      }));
      throw new Error(error.detail || 'Erro na requisição');
    }
    return response.json();
  }

  async healthCheck() {
      const response = await fetch(`${this.baseUrl}/`, {
      method: 'GET',
    });

    return this.handleResponse<healthCheck>(response)
  }

  async getStatusProcess(fileId: string): Promise<StatusProcess>{
    const response = await fetch(`${this.baseUrl}/api/v1/status/${fileId}`);

    return this.handleResponse<StatusProcess>(response)
  }

  async getScript(fileId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/v1/script/${fileId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch script');
    }
    return await response.blob();
  }

  async uploadFile(file: File): Promise<UploadResponse> {
     const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/v1/upload`, {
      method: 'POST',
      body: formData,
    });
    return this.handleResponse<UploadResponse>(response);
  } 

  async processFile(fileId: string): Promise<ProcessResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/process?file_id=${fileId}`, {
      method: 'POST',      
    });

    return this.handleResponse<ProcessResponse>(response)
  }

  async executeScript(fileId: string): Promise<ExecuteResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/execute?file_id=${fileId}`, {
      method: 'POST',      
    });

    return this.handleResponse<ExecuteResponse>(response)
  }
  

  async download(file_id: string) {
    const response = await fetch(`${this.baseUrl}/api/v1/download/${file_id}`)
    
    if (!response.ok) {
      throw new Error('Failed to fetch result');
    }

    const blob = await response.blob();
    return blob;

  }

  async results(fileId: string): Promise<ResultResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/result/${fileId}`);
    return this.handleResponse<ResultResponse>(response);
  }

}

export const apiClient = new APIClient()