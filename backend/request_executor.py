"""Execute HTTP requests for testing API endpoints."""

import time
from typing import Any

import httpx


def execute_request(request_details: dict[str, Any]) -> dict[str, Any]:
    """Execute HTTP request and return response details."""
    
    # 1️⃣ Extract request parameters ----
    method = request_details.get("method", "GET").upper()
    url = request_details.get("url", "")
    headers = request_details.get("headers", {})
    query_params = request_details.get("query_params", {})
    body_info = request_details.get("body", {})
    
    if not url:
        raise ValueError("URL is required for request execution")
    
    # Debug: Print headers to see what's being sent
    print(f"DEBUG: Headers being sent: {list(headers.keys())}")
    for key in headers.keys():
        if key.startswith(":") or key.lower() in [":authority", ":method", ":path", ":scheme", ":status"]:
            print(f"DEBUG: Found problematic header: {key}")
    
    # 2️⃣ Prepare request data ----
    request_data = _prepare_request_data(body_info)
    request_headers = _prepare_headers(headers)
    
    # 3️⃣ Execute request with timing ----
    start_time = time.time()
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.request(
                method=method,
                url=url,
                headers=request_headers,
                params=query_params,
                **request_data
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # 4️⃣ Parse response ----
            return _parse_response(response, execution_time)
            
    except httpx.TimeoutException:
        raise ValueError("Request timed out after 30 seconds")
    except httpx.ConnectError:
        raise ValueError("Failed to connect to the server")
    except httpx.HTTPError as e:
        error_msg = str(e)
        if "Illegal header name" in error_msg:
            raise ValueError("Invalid headers detected. Please try again or check the request details.")
        raise ValueError(f"HTTP error occurred: {error_msg}")
    except Exception as e:
        error_msg = str(e)
        if "Illegal header name" in error_msg:
            raise ValueError("Invalid headers detected. Please try again or check the request details.")
        raise ValueError(f"Request failed: {error_msg}")


def _prepare_request_data(body_info: dict[str, Any]) -> dict[str, Any]:
    """Prepare request data based on body type."""
    body_type = body_info.get("type", "none")
    
    if body_type == "none":
        return {}
    elif body_type == "json":
        return {"json": body_info.get("content", {})}
    elif body_type == "form":
        return {"data": body_info.get("content", {})}
    else:  # text or other
        return {"content": body_info.get("raw", "").encode("utf-8")}


def _prepare_headers(headers: dict[str, str]) -> dict[str, str]:
    """Prepare headers for the request."""
    # Remove problematic headers
    filtered_headers = {}
    
    for key, value in headers.items():
        key_lower = key.lower()
        
        # Skip HTTP/2 pseudo-headers and other problematic headers
        if key_lower in [
            "host",           # Set automatically by httpx
            ":authority",     # HTTP/2 pseudo-header
            ":method",        # HTTP/2 pseudo-header  
            ":path",          # HTTP/2 pseudo-header
            ":scheme",        # HTTP/2 pseudo-header
            ":status",        # HTTP/2 pseudo-header
        ]:
            continue
            
        # Skip headers that start with colon (HTTP/2 pseudo-headers)
        if key.startswith(":"):
            continue
            
        filtered_headers[key] = value
    
    return filtered_headers


def _parse_response(response: httpx.Response, execution_time: float) -> dict[str, Any]:
    """Parse HTTP response into structured format."""
    
    # 1️⃣ Parse response body ----
    try:
        if response.headers.get("content-type", "").startswith("application/json"):
            response_body = response.json()
            body_type = "json"
        else:
            response_body = response.text
            body_type = "text"
    except Exception:
        response_body = response.text
        body_type = "text"
    
    # 2️⃣ Format headers ----
    response_headers = dict(response.headers)
    
    return {
        "status_code": response.status_code,
        "status_text": response.reason_phrase,
        "headers": response_headers,
        "body": response_body,
        "body_type": body_type,
        "execution_time": round(execution_time, 3),
        "size_bytes": len(response.content),
    }
