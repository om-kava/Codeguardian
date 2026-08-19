import os
import json
import requests
from django.conf import settings

def run_ai_review(code: str, static_findings: list) -> dict:
    api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
    if not api_key:
        return {"summary": "OpenRouter API key not configured.", "findings": []}
    
    prompt = f"""
    You are an expert software engineer reviewer. Review this code and provide a structured JSON response.
    Do not report basic linting issues that static tools already found. Focus on high-level architecture, design, and complex bugs.

    Here are the static findings already detected:
    {json.dumps(static_findings, indent=2)}
    
    Code to review:
    ```
    {code}
    ```

    Respond EXACTLY in this JSON format without markdown wrapping:
    {{
        "summary": "High level summary of your review.",
        "suggested_code": "The entire original code file but refactored to resolve all high-severity findings and architectural bugs. DO NOT return just a snippet, return the full corrected file.",
        "findings": [
            {{
                "title": "Short title",
                "category": "SECURITY|COMPLEXITY|STYLE|BUG_RISK|DOCUMENTATION",
                "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
                "line_number": 10,
                "message": "Detailed explanation",
                "recommendation": "How to fix it",
                "suggested_fix": "Code snippet of fix if applicable",
                "analyzer": "Gemini AI"
            }}
        ]
    }}
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "CodeGuardian AI",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openrouter/free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        
        # Strip markdown wrappers if present (e.g. ```json ... ```)
        if content.startswith("```"):
            first_newline = content.find("\n")
            if first_newline != -1:
                content = content[first_newline:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()
                
        return json.loads(content)
    except Exception as e:
        print("AI Engine Error:", str(e))
        return {
            "summary": "AI Analysis failed to generate a valid response.",
            "error": str(e),
            "findings": []
        }
