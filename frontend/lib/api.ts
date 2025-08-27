import { APIError, UploadResponse } from "@/types";

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

  async uploadFile(file: File): Promise<UploadResponse> {
     const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/api/v1/upload`, {
      method: 'POST',
      body: formData,
    });

    return this.handleResponse<UploadResponse>(response);
  }

  async healthCheck() {
      const response = await fetch(`${this.baseUrl}/`, {
      method: 'GET',
    });

    return this.handleResponse<healthCheck>(response)
  }

}

export const apiClient = new APIClient()