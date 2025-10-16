"""Generate curl commands from HAR entries."""

import json
from typing import Any


def generate_curl_command(entry: dict[str, Any]) -> str:
    """Convert a HAR entry into a curl command."""
    request = entry.get("request", {})
    
    # 1️⃣ Get basic request info ----
    method = request.get("method", "GET")
    url = request.get("url", "")
    headers = request.get("headers", [])
    
    # 2️⃣ Build curl command ----
    parts = [f"curl '{url}'"]
    
    # Add method if not GET
    if method != "GET":
        parts.append(f"-X {method}")
    
    # 3️⃣ Add headers ----
    for header in headers:
        name = header.get("name", "")
        value = header.get("value", "")
        
        # Skip pseudo-headers (HTTP/2)
        if name.startswith(":"):
            continue
        
        # Escape single quotes in header values
        value = value.replace("'", "'\"'\"'")
        parts.append(f"-H '{name}: {value}'")
    
    # 4️⃣ Add request body if present ----
    post_data = request.get("postData", {})
    if post_data:
        text = post_data.get("text", "")
        if text:
            # Escape single quotes in body
            text = text.replace("'", "'\"'\"'")
            parts.append(f"--data-raw '{text}'")
    
    # 5️⃣ Format with line continuations ----
    return " \\\n  ".join(parts)

