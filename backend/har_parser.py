"""Parse and filter HAR files to extract API requests."""

import json
from typing import Any


def parse_har_file(file_content: bytes) -> dict[str, Any]:
    """Parse HAR file content into a dictionary."""
    return json.loads(file_content.decode("utf-8"))


def filter_api_requests(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter out non-API requests (HTML pages, images, CSS, etc.)."""
    api_requests = []
    
    for entry in entries:
        if not _is_api_request(entry):
            continue
        api_requests.append(entry)
    
    return api_requests


def create_request_summary(entry: dict[str, Any]) -> dict[str, Any]:
    """Create a lightweight summary of a request for LLM analysis."""
    request = entry.get("request", {})
    response = entry.get("response", {})
    
    # 1️⃣ Extract basic request info ----
    method = request.get("method", "")
    url = request.get("url", "")
    
    # 2️⃣ Get content type and response preview ----
    content_type = _get_response_content_type(response)
    response_preview = _get_response_preview(response)
    
    # 3️⃣ Return summary ----
    return {
        "method": method,
        "url": url,
        "content_type": content_type,
        "response_preview": response_preview,
    }


def _is_api_request(entry: dict[str, Any]) -> bool:
    """Check if entry is likely an API request (not HTML/CSS/image/etc)."""
    response = entry.get("response", {})
    content_type = _get_response_content_type(response)
    
    # Filter out common non-API content types
    non_api_types = [
        "text/html",
        "text/css",
        "image/",
        "font/",
        "video/",
        "audio/",
        "application/javascript",
        "text/javascript",
    ]
    
    for non_api_type in non_api_types:
        if non_api_type in content_type.lower():
            return False
    
    return True


def _get_response_content_type(response: dict[str, Any]) -> str:
    """Extract content-type from response headers."""
    headers = response.get("headers", [])
    
    for header in headers:
        name = header.get("name", "").lower()
        if name == "content-type":
            return header.get("value", "")
    
    return ""


def _get_response_preview(response: dict[str, Any]) -> str:
    """Get first 200 characters of response body."""
    content = response.get("content", {})
    text = content.get("text", "")
    
    if not text:
        return ""
    
    # Return first 200 chars
    preview = text[:200]
    if len(text) > 200:
        preview += "..."
    
    return preview

