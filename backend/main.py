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
    filter_api_requests,
    parse_har_file,
)
from llm_service import identify_best_request

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
        
        # 6️⃣ Return response ----
        return AnalyzeResponse(
            curl_command=curl_command,
            request_details={
                "method": selected_request.get("request", {}).get("method", ""),
                "url": selected_request.get("request", {}).get("url", ""),
                "index": best_index,
                "total_api_requests": len(api_requests),
            },
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing HAR file: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

