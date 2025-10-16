"""FastAPI backend for API reverse engineering."""

import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from curl_generator import generate_curl_command
from har_parser import (
    create_request_summary,
    detect_authentication,
    extract_request_details,
    filter_api_requests,
    parse_har_file,
)
from llm_service import identify_best_request
from request_executor import execute_request
from code_generator import generate_code
from doc_generator import generate_documentation

load_dotenv()

app = FastAPI(title="API Reverse Engineering Service")

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeResponse(BaseModel):
    """Response model for analyze endpoint."""
    
    curl_command: str
    request_details: dict[str, Any]
    request_info: dict[str, Any]
    auth_info: dict[str, Any]
    parameters: dict[str, Any]


class TestRequestResponse(BaseModel):
    """Response model for test request endpoint."""
    
    status_code: int
    status_text: str
    headers: dict[str, str]
    body: Any
    body_type: str
    execution_time: float
    size_bytes: int


class GenerateCodeResponse(BaseModel):
    """Response model for code generation endpoint."""
    
    code: str
    language: str


class ExportDocsResponse(BaseModel):
    """Response model for documentation export endpoint."""
    
    content: str
    format: str
    filename: str


class GenerateCodeRequest(BaseModel):
    """Request model for code generation endpoint."""
    
    request_info: dict[str, Any]
    language: str = "python"


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_har_file(
    har_file: UploadFile = File(...),
    description: str = Form(...),
) -> AnalyzeResponse:
    """Analyze HAR file and return curl command for matching request."""
    
    # 1️⃣ Validate inputs ----
    if not har_file.filename or not har_file.filename.endswith(".har"):
        raise HTTPException(status_code=400, detail="File must be a .har file")
    
    if not description or len(description.strip()) == 0:
        raise HTTPException(status_code=400, detail="Description is required")
    
    try:
        # 2️⃣ Parse and filter HAR file ----
        content = await har_file.read()
        har_data = parse_har_file(content)
        
        entries = har_data.get("log", {}).get("entries", [])
        api_requests = filter_api_requests(entries)
        
        if not api_requests:
            raise HTTPException(
                status_code=404,
                detail="No API requests found in HAR file"
            )
        
        # 3️⃣ Create summaries for LLM ----
        summaries = [create_request_summary(req) for req in api_requests]
        
        # 4️⃣ Use LLM to find best match ----
        best_index = identify_best_request(summaries, description)
        
        if best_index < 0 or best_index >= len(api_requests):
            raise HTTPException(
                status_code=500,
                detail="LLM returned invalid request index"
            )
        
        # 5️⃣ Generate curl command ----
        selected_request = api_requests[best_index]
        curl_command = generate_curl_command(selected_request)
        
        # 6️⃣ Extract detailed request info ----
        request_info = extract_request_details(selected_request)
        auth_info = detect_authentication(request_info)
        
        # 7️⃣ Build parameters summary ----
        parameters = {
            "query_params": request_info.get("query_params", {}),
            "path_params": request_info.get("path_params", []),
            "headers": {k: v for k, v in request_info.get("headers", {}).items() 
                       if k.lower() not in ["authorization", "x-api-key", "api-key"]},
        }
        
        # 8️⃣ Return enhanced response ----
        return AnalyzeResponse(
            curl_command=curl_command,
            request_details={
                "method": selected_request.get("request", {}).get("method", ""),
                "url": selected_request.get("request", {}).get("url", ""),
                "index": best_index,
                "total_api_requests": len(api_requests),
            },
            request_info=request_info,
            auth_info=auth_info,
            parameters=parameters,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing HAR file: {str(e)}"
        )


@app.post("/api/test-request", response_model=TestRequestResponse)
async def test_request(request_info: dict[str, Any]) -> TestRequestResponse:
    """Execute the API request and return response details."""
    
    try:
        # 1️⃣ Clean request info ----
        cleaned_request_info = _clean_request_info(request_info)
        
        # 2️⃣ Execute request ----
        response_data = execute_request(cleaned_request_info)
        
        # 3️⃣ Return response ----
        return TestRequestResponse(**response_data)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing request: {str(e)}"
        )


@app.post("/api/generate-code", response_model=GenerateCodeResponse)
async def generate_code_endpoint(request: GenerateCodeRequest) -> GenerateCodeResponse:
    """Generate code in the specified language."""
    
    try:
        # Debug: Print what we received
        print(f"DEBUG: Received request: {request}")
        print(f"DEBUG: request_info: {request.request_info}")
        print(f"DEBUG: URL in request_info: {request.request_info.get('url', 'NOT_FOUND')}")
        print(f"DEBUG: Language: {request.language}")
        
        # 1️⃣ Validate language ----
        supported_languages = ["python", "javascript", "go"]
        if request.language not in supported_languages:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported language. Supported: {', '.join(supported_languages)}"
            )
        
        # 2️⃣ Generate code ----
        code = generate_code(request.request_info, request.language)
        
        # 3️⃣ Return response ----
        return GenerateCodeResponse(code=code, language=request.language)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating code: {str(e)}"
        )


@app.post("/api/export-docs", response_model=ExportDocsResponse)
async def export_docs_endpoint(
    request_info: dict[str, Any],
    auth_info: dict[str, Any],
    format_type: str = "markdown"
) -> ExportDocsResponse:
    """Export API documentation in the specified format."""
    
    try:
        # 1️⃣ Validate format ----
        supported_formats = ["markdown", "openapi"]
        if format_type not in supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Supported: {', '.join(supported_formats)}"
            )
        
        # 2️⃣ Generate documentation ----
        content = generate_documentation(request_info, auth_info, format_type)
        
        # 3️⃣ Determine filename ----
        method = request_info.get("method", "GET").lower()
        path = request_info.get("path", "/").replace("/", "_")
        if path.startswith("_"):
            path = path[1:]
        if not path:
            path = "api"
        
        filename = f"{method}_{path}.{format_type}"
        if format_type == "openapi":
            filename = f"{method}_{path}.json"
        
        # 4️⃣ Return response ----
        return ExportDocsResponse(
            content=content,
            format=format_type,
            filename=filename
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating documentation: {str(e)}"
        )


def _clean_request_info(request_info: dict[str, Any]) -> dict[str, Any]:
    """Clean request info by removing problematic headers."""
    cleaned_info = request_info.copy()
    
    # Clean headers
    if "headers" in cleaned_info:
        headers = cleaned_info["headers"]
        cleaned_headers = {}
        
        for key, value in headers.items():
            key_lower = key.lower()
            
            # Skip HTTP/2 pseudo-headers and problematic headers
            if (key_lower in [
                "host", ":authority", ":method", ":path", ":scheme", ":status"
            ] or key.startswith(":")):
                continue
                
            cleaned_headers[key] = value
        
        cleaned_info["headers"] = cleaned_headers
    
    return cleaned_info


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

