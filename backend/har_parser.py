"""Parse and filter HAR files to extract API requests."""

import json
import re
from typing import Any
from urllib.parse import urlparse, parse_qs


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


def extract_request_details(entry: dict[str, Any]) -> dict[str, Any]:
    """Extract detailed request information including headers, params, and body."""
    request = entry.get("request", {})
    
    # 1️⃣ Extract basic request info ----
    method = request.get("method", "")
    url = request.get("url", "")
    headers = request.get("headers", [])
    query_string = request.get("queryString", [])
    post_data = request.get("postData", {})
    
    # 2️⃣ Parse URL components ----
    parsed_url = urlparse(url)
    path_params = _extract_path_parameters(parsed_url.path)
    query_params = {param.get("name", ""): param.get("value", "") for param in query_string}
    
    # 3️⃣ Parse headers ----
    header_dict = {}
    for header in headers:
        name = header.get("name", "")
        value = header.get("value", "")
        
        # Skip HTTP/2 pseudo-headers and problematic headers
        if (name.startswith(":") or 
            name.lower() in ["host", ":authority", ":method", ":path", ":scheme", ":status"]):
            continue
            
        header_dict[name] = value
    
    # 4️⃣ Parse request body ----
    body_info = _parse_request_body(post_data)
    
    return {
        "method": method,
        "url": url,
        "path": parsed_url.path,
        "host": parsed_url.netloc,
        "scheme": parsed_url.scheme,
        "headers": header_dict,
        "query_params": query_params,
        "path_params": path_params,
        "body": body_info,
    }


def detect_authentication(request_details: dict[str, Any]) -> dict[str, Any]:
    """Detect authentication methods and redact sensitive values."""
    headers = request_details.get("headers", {})
    auth_info = {
        "type": "none",
        "location": "none",
        "redacted_value": "",
        "original_value": "",
    }
    
    # 1️⃣ Check Authorization header ----
    auth_header = headers.get("Authorization", "").lower()
    if auth_header.startswith("bearer "):
        token = headers.get("Authorization", "").replace("Bearer ", "")
        auth_info.update({
            "type": "bearer_token",
            "location": "header",
            "redacted_value": redact_sensitive_values(token),
            "original_value": token,
        })
    elif auth_header.startswith("basic "):
        auth_info.update({
            "type": "basic_auth",
            "location": "header",
            "redacted_value": "Basic ********",
            "original_value": headers.get("Authorization", ""),
        })
    
    # 2️⃣ Check API key headers ----
    api_key_headers = ["x-api-key", "api-key", "x-auth-token", "authorization"]
    for header_name in api_key_headers:
        if header_name in headers:
            value = headers[header_name]
            if value and not auth_info["type"] != "none":
                auth_info.update({
                    "type": "api_key",
                    "location": "header",
                    "redacted_value": redact_sensitive_values(value),
                    "original_value": value,
                })
                break
    
    # 3️⃣ Check query parameters for API keys ----
    query_params = request_details.get("query_params", {})
    api_key_params = ["api_key", "apikey", "key", "token", "access_token"]
    for param_name in api_key_params:
        if param_name in query_params:
            value = query_params[param_name]
            if value and auth_info["type"] == "none":
                auth_info.update({
                    "type": "api_key",
                    "location": "query",
                    "redacted_value": redact_sensitive_values(value),
                    "original_value": value,
                })
                break
    
    return auth_info


def redact_sensitive_values(value: str) -> str:
    """Redact sensitive values while preserving structure."""
    if not value or len(value) < 8:
        return "****"
    
    # 1️⃣ Keep first 4 and last 4 characters ----
    if len(value) <= 12:
        return value[:2] + "*" * (len(value) - 4) + value[-2:]
    
    return value[:4] + "*" * (len(value) - 8) + value[-4:]


def _extract_path_parameters(path: str) -> list[str]:
    """Extract potential path parameters from URL path."""
    # Look for patterns like /users/{id} or /users/:id
    param_patterns = [
        r'\{([^}]+)\}',  # {id}
        r':([^/]+)',     # :id
    ]
    
    params = []
    for pattern in param_patterns:
        matches = re.findall(pattern, path)
        params.extend(matches)
    
    return list(set(params))  # Remove duplicates


def _parse_request_body(post_data: dict[str, Any]) -> dict[str, Any]:
    """Parse request body and return structured information."""
    if not post_data:
        return {"type": "none", "content": ""}
    
    text = post_data.get("text", "")
    mime_type = post_data.get("mimeType", "")
    
    # 1️⃣ Try to parse JSON ----
    if "application/json" in mime_type and text:
        try:
            json_data = json.loads(text)
            return {
                "type": "json",
                "content": json_data,
                "raw": text,
            }
        except json.JSONDecodeError:
            pass
    
    # 2️⃣ Try to parse form data ----
    if "application/x-www-form-urlencoded" in mime_type and text:
        try:
            form_data = parse_qs(text)
            return {
                "type": "form",
                "content": form_data,
                "raw": text,
            }
        except Exception:
            pass
    
    # 3️⃣ Return raw text ----
    return {
        "type": "text",
        "content": text,
        "raw": text,
    }

