"""LLM service for identifying the best matching API request."""

import os
from typing import Any

from openai import OpenAI
from pydantic import BaseModel


class RequestSelection(BaseModel):
    """Structured output for request selection."""
    
    index: int
    reasoning: str


def identify_best_request(
    summaries: list[dict[str, Any]], 
    user_query: str
) -> int:
    """Use LLM to identify which request best matches the user's intent."""
    if not summaries:
        raise ValueError("No API requests found in HAR file")
    
    # 1️⃣ Build prompt with request summaries ----
    prompt = _build_prompt(summaries, user_query)
    
    # 2️⃣ Call OpenAI with structured output ----
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {
                "role": "system",
                "content": _get_system_prompt(),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_format={"type": "json_object"},
    )
    
    # 3️⃣ Extract and return index ----
    import json
    result_text = response.choices[0].message.content
    result = json.loads(result_text)
    return result["index"]


def _get_system_prompt() -> str:
    """Return the system prompt for request identification."""
    return """You are an API request analyzer. Given a list of HTTP requests from a HAR file and a user's description, identify which request best matches their intent.

Rules:
- Only consider requests that return JSON or XML data, not HTML pages
- Focus on the URL path and response content to understand what data the API returns
- Return the 0-based index of the best matching request
- Provide brief reasoning for your choice

Respond with a JSON object in this format:
{"index": 0, "reasoning": "brief explanation"}"""


def _build_prompt(
    summaries: list[dict[str, Any]], 
    user_query: str
) -> str:
    """Build the user prompt with request summaries."""
    lines = ["Requests:\n"]
    
    for i, summary in enumerate(summaries):
        method = summary.get("method", "")
        url = summary.get("url", "")
        content_type = summary.get("content_type", "")
        preview = summary.get("response_preview", "")
        
        # Format each request summary
        lines.append(f"[{i}] {method} {url}")
        lines.append(f"    Content-Type: {content_type}")
        
        if preview:
            lines.append(f"    Response preview: {preview}")
        
        lines.append("")
    
    lines.append(f'User wants: "{user_query}"')
    lines.append("")
    lines.append("Which request index best matches?")
    
    return "\n".join(lines)

