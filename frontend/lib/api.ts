// API client for backend communication

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AnalyzeResponse {
  curl_command: string;
  request_details: {
    method: string;
    url: string;
    index: number;
    total_api_requests: number;
  };
  request_info: {
    method: string;
    url: string;
    path: string;
    host: string;
    scheme: string;
    headers: Record<string, string>;
    query_params: Record<string, string>;
    path_params: string[];
    body: {
      type: string;
      content: unknown;
      raw: string;
    };
  };
  auth_info: {
    type: string;
    location: string;
    redacted_value: string;
    original_value: string;
  };
  parameters: {
    query_params: Record<string, string>;
    path_params: string[];
    headers: Record<string, string>;
  };
}

export interface ApiError {
  detail: string;
}

export async function analyzeHarFile(
  file: File,
  description: string
): Promise<AnalyzeResponse> {
  // 1️⃣ Create form data
  const formData = new FormData();
  formData.append("har_file", file);
  formData.append("description", description);

  // 2️⃣ Make API request
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  // 3️⃣ Handle response
  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || "Failed to analyze HAR file");
  }

  return response.json();
}

export interface TestRequestResponse {
  status_code: number;
  status_text: string;
  headers: Record<string, string>;
  body: unknown;
  body_type: string;
  execution_time: number;
  size_bytes: number;
}

export interface GenerateCodeResponse {
  code: string;
  language: string;
}

export interface ExportDocsResponse {
  content: string;
  format: string;
  filename: string;
}

export async function testRequest(requestInfo: unknown): Promise<TestRequestResponse> {
  const response = await fetch(`${API_BASE_URL}/api/test-request`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestInfo),
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || "Failed to test request");
  }

  return response.json();
}

export async function generateCode(requestInfo: unknown, language: string): Promise<GenerateCodeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/generate-code`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ request_info: requestInfo, language }),
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || "Failed to generate code");
  }

  return response.json();
}

export async function exportDocs(requestInfo: unknown, authInfo: unknown, format: string): Promise<ExportDocsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/export-docs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ 
      request_info: requestInfo, 
      auth_info: authInfo, 
      format_type: format 
    }),
  });

  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || "Failed to export documentation");
  }

  return response.json();
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
