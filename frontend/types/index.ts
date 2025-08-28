
export interface APIError {
  detail: string;
}

export interface UploadResponse {
  filename: string;
  status: boolean;
  message: string;
  file_id: string;
}

export interface DataSummary {
  filename: string;
  rows_count: number;
  columns_count: number;
  columns: string[];
  data_types: Record<string, string>;
  missing_values: Record<string, number>;
  sample_rows: Record<string, unknown>[];
  duplicate_rows: number;
  memory_usage: string;
}

export interface ProcessResponse {
  file_id: string;
  message: string;
  script: string;
  data_summary: DataSummary;
}

export interface ResultResponse {
  file_id: string;
  message: string;
  data: Record<string, unknown>[];
  columns: string[];
  rows_count: number;
}

export interface ProcessingStep {
  id: string;
  title: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  description?: string;
}

export interface StatusProcess {
  file_id: string;
  uploaded: boolean;
  processed_by_llm: boolean;
  script_executed: boolean;
  ready: boolean;
}