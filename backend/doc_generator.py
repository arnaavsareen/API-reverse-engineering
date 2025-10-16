"""Generate API documentation in various formats."""

import json
from typing import Any


def generate_documentation(request_details: dict[str, Any], auth_info: dict[str, Any], format_type: str) -> str:
    """Generate documentation in the specified format."""
    
    if format_type == "markdown":
        return _generate_markdown_doc(request_details, auth_info)
    elif format_type == "openapi":
        return _generate_openapi_doc(request_details, auth_info)
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def _generate_markdown_doc(request_details: dict[str, Any], auth_info: dict[str, Any]) -> str:
    """Generate Markdown documentation."""
    
    # 1️⃣ Extract request info ----
    method = request_details.get("method", "GET")
    url = request_details.get("url", "")
    path = request_details.get("path", "")
    headers = request_details.get("headers", {})
    query_params = request_details.get("query_params", {})
    body_info = request_details.get("body", {})
    
    # 2️⃣ Build documentation ----
    lines = [
        f"# API Documentation",
        "",
        f"## {method} {path}",
        "",
        f"**URL:** `{url}`",
        "",
    ]
    
    # 3️⃣ Add description ----
    lines.extend([
        "### Description",
        "",
        "This endpoint was reverse-engineered from a HAR file capture.",
        "",
    ])
    
    # 4️⃣ Add authentication ----
    if auth_info.get("type") != "none":
        lines.extend([
            "### Authentication",
            "",
            f"**Type:** {auth_info.get('type', 'none').replace('_', ' ').title()}",
            f"**Location:** {auth_info.get('location', 'none')}",
            "",
        ])
        
        if auth_info.get("redacted_value"):
            lines.extend([
                "**Example:**",
                f"```",
                f"{auth_info.get('redacted_value')}",
                f"```",
                "",
            ])
    
    # 5️⃣ Add parameters ----
    if query_params:
        lines.extend([
            "### Query Parameters",
            "",
            "| Parameter | Type | Required | Description |",
            "|-----------|------|----------|-------------|",
        ])
        
        for param, value in query_params.items():
            lines.append(f"| `{param}` | string | No | Example: `{value}` |")
        
        lines.append("")
    
    # 6️⃣ Add headers ----
    if headers:
        lines.extend([
            "### Headers",
            "",
            "| Header | Value |",
            "|--------|-------|",
        ])
        
        for header, value in headers.items():
            lines.append(f"| `{header}` | `{value}` |")
        
        lines.append("")
    
    # 7️⃣ Add request body ----
    if body_info.get("type") != "none":
        lines.extend([
            "### Request Body",
            "",
            f"**Content Type:** {body_info.get('type', 'text')}",
            "",
        ])
        
        if body_info.get("type") == "json":
            content = body_info.get("content", {})
            lines.extend([
                "**Example:**",
                "```json",
                json.dumps(content, indent=2),
                "```",
                "",
            ])
        else:
            raw = body_info.get("raw", "")
            lines.extend([
                "**Example:**",
                "```",
                raw,
                "```",
                "",
            ])
    
    # 8️⃣ Add cURL example ----
    lines.extend([
        "### cURL Example",
        "",
        "```bash",
        _generate_curl_example(request_details),
        "```",
        "",
    ])
    
    # 9️⃣ Add response example ----
    lines.extend([
        "### Response",
        "",
        "The API returns a JSON response with the requested data.",
        "",
        "**Example Response:**",
        "```json",
        "{",
        '  "status": "success",',
        '  "data": {',
        '    "message": "Request successful"',
        "  }",
        "}",
        "```",
        "",
    ])
    
    return "\n".join(lines)


def _generate_openapi_doc(request_details: dict[str, Any], auth_info: dict[str, Any]) -> str:
    """Generate OpenAPI 3.0 documentation."""
    
    # 1️⃣ Extract request info ----
    method = request_details.get("method", "GET").lower()
    url = request_details.get("url", "")
    path = request_details.get("path", "")
    headers = request_details.get("headers", {})
    query_params = request_details.get("query_params", {})
    body_info = request_details.get("body", {})
    
    # 2️⃣ Build OpenAPI spec ----
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Reverse Engineered API",
            "description": "API documentation generated from HAR file analysis",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": f"{request_details.get('scheme', 'https')}://{request_details.get('host', '')}",
                "description": "API Server"
            }
        ],
        "paths": {
            path: {
                method: {
                    "summary": f"{method.upper()} {path}",
                    "description": "Endpoint reverse-engineered from HAR file",
                    "parameters": _build_openapi_parameters(query_params),
                    "requestBody": _build_openapi_request_body(body_info),
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "data": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    # 3️⃣ Add security if auth detected ----
    if auth_info.get("type") != "none":
        spec["components"] = {
            "securitySchemes": _build_security_schemes(auth_info)
        }
        spec["paths"][path][method]["security"] = [
            {auth_info.get("type", "none"): []}
        ]
    
    return json.dumps(spec, indent=2)


def _build_openapi_parameters(query_params: dict[str, str]) -> list[dict[str, Any]]:
    """Build OpenAPI parameters from query params."""
    parameters = []
    
    for param, value in query_params.items():
        parameters.append({
            "name": param,
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
            "example": value
        })
    
    return parameters


def _build_openapi_request_body(body_info: dict[str, Any]) -> dict[str, Any]:
    """Build OpenAPI request body from body info."""
    if body_info.get("type") == "none":
        return None
    
    content_type = "application/json"
    if body_info.get("type") == "form":
        content_type = "application/x-www-form-urlencoded"
    elif body_info.get("type") == "text":
        content_type = "text/plain"
    
    return {
        "required": True,
        "content": {
            content_type: {
                "schema": {
                    "type": "object" if body_info.get("type") == "json" else "string"
                },
                "example": body_info.get("content", {})
            }
        }
    }


def _build_security_schemes(auth_info: dict[str, Any]) -> dict[str, Any]:
    """Build OpenAPI security schemes from auth info."""
    auth_type = auth_info.get("type", "none")
    
    if auth_type == "bearer_token":
        return {
            "bearer_token": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    elif auth_type == "basic_auth":
        return {
            "basic_auth": {
                "type": "http",
                "scheme": "basic"
            }
        }
    elif auth_type == "api_key":
        location = auth_info.get("location", "header")
        return {
            "api_key": {
                "type": "apiKey",
                "in": location,
                "name": "X-API-Key"
            }
        }
    else:
        return {}


def _generate_curl_example(request_details: dict[str, Any]) -> str:
    """Generate cURL example for documentation."""
    from curl_generator import generate_curl_command
    
    # Create a mock entry for curl generation
    entry = {
        "request": {
            "method": request_details.get("method", "GET"),
            "url": request_details.get("url", ""),
            "headers": [{"name": k, "value": v} for k, v in request_details.get("headers", {}).items()],
            "queryString": [{"name": k, "value": v} for k, v in request_details.get("query_params", {}).items()],
            "postData": request_details.get("body", {})
        }
    }
    
    return generate_curl_command(entry)
