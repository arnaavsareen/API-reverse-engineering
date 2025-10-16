"""Generate code in multiple languages from request details."""

from typing import Any


def generate_code(request_details: dict[str, Any], language: str) -> str:
    """Generate code for the specified language."""
    
    if language == "python":
        return _generate_python_code(request_details)
    elif language == "javascript":
        return _generate_javascript_code(request_details)
    elif language == "go":
        return _generate_go_code(request_details)
    else:
        raise ValueError(f"Unsupported language: {language}")


def _generate_python_code(request_details: dict[str, Any]) -> str:
    """Generate Python code using requests library."""
    
    # 1️⃣ Extract request info ----
    method = request_details.get("method", "GET").lower()
    url = request_details.get("url", "")
    headers = request_details.get("headers", {})
    query_params = request_details.get("query_params", {})
    body_info = request_details.get("body", {})
    
    # Debug: Print what we're working with
    print(f"DEBUG: Generating Python code for {method} {url}")
    print(f"DEBUG: Headers: {list(headers.keys())}")
    print(f"DEBUG: Query params: {query_params}")
    print(f"DEBUG: Body type: {body_info.get('type', 'none')}")
    
    if not url:
        return "# Error: No URL provided in request details"
    
    # 2️⃣ Build imports ----
    lines = ["import requests", ""]
    
    # 3️⃣ Build URL with query params ----
    if query_params:
        lines.append("# Query parameters")
        lines.append(f"params = {_format_dict(query_params)}")
        lines.append("")
    
    # 4️⃣ Build headers ----
    if headers:
        lines.append("# Headers")
        lines.append(f"headers = {_format_dict(headers)}")
        lines.append("")
    
    # 5️⃣ Build request body ----
    body_lines = _build_python_body(body_info)
    if body_lines:
        lines.extend(body_lines)
        lines.append("")
    
    # 6️⃣ Build request call ----
    lines.append("# Make request")
    request_parts = [f"'{url}'"]
    
    if query_params:
        request_parts.append("params=params")
    if headers:
        request_parts.append("headers=headers")
    if body_info.get("type") != "none":
        if body_info.get("type") == "json":
            request_parts.append("json=data")
        else:
            request_parts.append("data=data")
    
    request_call = f"response = requests.{method}({', '.join(request_parts)})"
    lines.append(request_call)
    lines.append("")
    
    # 7️⃣ Add response handling ----
    lines.extend([
        "# Handle response",
        "print(f'Status: {response.status_code}')",
        "print(f'Response: {response.text}')",
    ])
    
    return "\n".join(lines)


def _generate_javascript_code(request_details: dict[str, Any]) -> str:
    """Generate JavaScript code using fetch API."""
    
    # 1️⃣ Extract request info ----
    method = request_details.get("method", "GET").upper()
    url = request_details.get("url", "")
    headers = request_details.get("headers", {})
    query_params = request_details.get("query_params", {})
    body_info = request_details.get("body", {})
    
    if not url:
        return "// Error: No URL provided in request details"
    
    # 2️⃣ Build URL with query params ----
    lines = []
    if query_params:
        lines.append("// Query parameters")
        lines.append(f"const params = {_format_dict(query_params)};")
        lines.append("const url = new URL('" + url + "');")
        lines.append("Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));")
        lines.append("")
    else:
        lines.append(f"const url = '{url}';")
        lines.append("")
    
    # 3️⃣ Build headers ----
    if headers:
        lines.append("// Headers")
        lines.append(f"const headers = {_format_dict(headers)};")
        lines.append("")
    
    # 4️⃣ Build request body ----
    body_lines = _build_javascript_body(body_info)
    if body_lines:
        lines.extend(body_lines)
        lines.append("")
    
    # 5️⃣ Build fetch call ----
    lines.append("// Make request")
    fetch_parts = ["url"]
    
    options = []
    if method != "GET":
        options.append(f"method: '{method}'")
    if headers:
        options.append("headers: headers")
    if body_info.get("type") != "none":
        options.append("body: body")
    
    if options:
        fetch_parts.append(f"{{{', '.join(options)}}}")
    
    fetch_call = f"fetch({', '.join(fetch_parts)})"
    lines.extend([
        fetch_call,
        "  .then(response => response.json())",
        "  .then(data => console.log(data))",
        "  .catch(error => console.error('Error:', error));",
    ])
    
    return "\n".join(lines)


def _generate_go_code(request_details: dict[str, Any]) -> str:
    """Generate Go code using net/http package."""
    
    # 1️⃣ Extract request info ----
    method = request_details.get("method", "GET").upper()
    url = request_details.get("url", "")
    headers = request_details.get("headers", {})
    query_params = request_details.get("query_params", {})
    body_info = request_details.get("body", {})
    
    if not url:
        return "// Error: No URL provided in request details"
    
    # 2️⃣ Build imports ----
    lines = [
        "package main",
        "",
        "import (",
        '    "fmt"',
        '    "io"',
        '    "net/http"',
        '    "net/url"',
        '    "strings"',
        ")",
        "",
    ]
    
    # 3️⃣ Build main function ----
    lines.append("func main() {")
    lines.append("    // Create HTTP client")
    lines.append("    client := &http.Client{}")
    lines.append("")
    
    # 4️⃣ Build URL with query params ----
    if query_params:
        lines.append("    // Query parameters")
        lines.append(f"    baseURL := \"{url}\"")
        lines.append("    u, _ := url.Parse(baseURL)")
        lines.append("    q := u.Query()")
        for key, value in query_params.items():
            lines.append(f"    q.Set(\"{key}\", \"{value}\")")
        lines.append("    u.RawQuery = q.Encode()")
        lines.append("")
    else:
        lines.append(f"    requestURL := \"{url}\"")
        lines.append("")
    
    # 5️⃣ Build request body ----
    body_lines = _build_go_body(body_info)
    if body_lines:
        lines.extend(body_lines)
        lines.append("")
    
    # 6️⃣ Build request ----
    lines.append("    // Create request")
    if body_info.get("type") != "none":
        lines.append("    req, _ := http.NewRequest(\"" + method + "\", requestURL, body)")
    else:
        lines.append("    req, _ := http.NewRequest(\"" + method + "\", requestURL, nil)")
    
    # 7️⃣ Add headers ----
    if headers:
        lines.append("    // Headers")
        for key, value in headers.items():
            lines.append(f"    req.Header.Set(\"{key}\", \"{value}\")")
        lines.append("")
    
    # 8️⃣ Execute request ----
    lines.extend([
        "    // Execute request",
        "    resp, err := client.Do(req)",
        "    if err != nil {",
        "        panic(err)",
        "    }",
        "    defer resp.Body.Close()",
        "",
        "    // Read response",
        "    body, _ := io.ReadAll(resp.Body)",
        "    fmt.Printf(\"Status: %s\\n\", resp.Status)",
        "    fmt.Printf(\"Response: %s\\n\", string(body))",
        "}",
    ])
    
    return "\n".join(lines)


def _build_python_body(body_info: dict[str, Any]) -> list[str]:
    """Build Python request body code."""
    body_type = body_info.get("type", "none")
    
    if body_type == "none":
        return []
    elif body_type == "json":
        content = body_info.get("content", {})
        return [
            "# Request body",
            f"data = {_format_dict(content)}",
        ]
    elif body_type == "form":
        content = body_info.get("content", {})
        return [
            "# Request body (form data)",
            f"data = {_format_dict(content)}",
        ]
    else:  # text
        raw = body_info.get("raw", "")
        return [
            "# Request body",
            f"data = \"\"\"{raw}\"\"\"",
        ]


def _build_javascript_body(body_info: dict[str, Any]) -> list[str]:
    """Build JavaScript request body code."""
    body_type = body_info.get("type", "none")
    
    if body_type == "none":
        return []
    elif body_type == "json":
        content = body_info.get("content", {})
        return [
            "// Request body",
            f"const body = JSON.stringify({_format_dict(content)});",
        ]
    elif body_type == "form":
        content = body_info.get("content", {})
        return [
            "// Request body (form data)",
            f"const body = new URLSearchParams({_format_dict(content)});",
        ]
    else:  # text
        raw = body_info.get("raw", "")
        return [
            "// Request body",
            f"const body = `{raw}`;",
        ]


def _build_go_body(body_info: dict[str, Any]) -> list[str]:
    """Build Go request body code."""
    body_type = body_info.get("type", "none")
    
    if body_type == "none":
        return []
    elif body_type == "json":
        content = body_info.get("content", {})
        return [
            "    // Request body",
            f"    body := strings.NewReader(`{_format_dict(content)}`)",
        ]
    elif body_type == "form":
        content = body_info.get("content", {})
        return [
            "    // Request body (form data)",
            f"    body := strings.NewReader(`{_format_dict(content)}`)",
        ]
    else:  # text
        raw = body_info.get("raw", "")
        return [
            "    // Request body",
            f"    body := strings.NewReader(`{raw}`)",
        ]


def _format_dict(data: dict[str, Any]) -> str:
    """Format dictionary for code generation."""
    if not data:
        return "{}"
    
    # Simple formatting - in production, use proper JSON formatting
    import json
    return json.dumps(data, indent=2)
