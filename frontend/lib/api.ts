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
}

export interface ApiError {
  detail: string;
}

export async function analyzeHarFile(
  file: File,
  description: string
): Promise<AnalyzeResponse> {
  // 1️⃣ Create form data ----
  const formData = new FormData();
  formData.append("har_file", file);
  formData.append("description", description);

  // 2️⃣ Make API request ----
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  // 3️⃣ Handle response ----
  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || "Failed to analyze HAR file");
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
