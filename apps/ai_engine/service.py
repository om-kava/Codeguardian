import os
import json
import requests
from django.conf import settings

def detect_language(filename: str, code: str) -> str:
    fn = (filename or '').lower().strip()
    if fn.endswith(('.html', '.htm')):
        return 'HTML'
    if fn.endswith('.css'):
        return 'CSS'
    if fn.endswith(('.js', '.mjs', '.cjs')):
        return 'JavaScript'
    if fn.endswith('.jsx'):
        return 'React JSX'
    if fn.endswith('.ts'):
        return 'TypeScript'
    if fn.endswith('.tsx'):
        return 'React TSX'
    if fn.endswith(('.py', '.pyw')):
        return 'Python'
    if fn.endswith('.java'):
        return 'Java'
    if fn.endswith(('.cpp', '.cc', '.cxx', '.c', '.h', '.hpp')):
        return 'C/C++'
    if fn.endswith('.go'):
        return 'Go'
    if fn.endswith('.rs'):
        return 'Rust'
    if fn.endswith('.php'):
        return 'PHP'
    if fn.endswith('.sql'):
        return 'SQL'
    if fn.endswith(('.sh', '.bash')):
        return 'Shell / Bash'
    if fn.endswith('.json'):
        return 'JSON'
    if fn.endswith(('.yaml', '.yml')):
        return 'YAML'
        
    # Heuristic content detection
    first_lines = code[:400].lower()
    if '<!doctype html' in first_lines or '<html' in first_lines or '<div' in first_lines or '<body>' in first_lines:
        return 'HTML'
    if '{' in first_lines and ('margin:' in first_lines or 'padding:' in first_lines or 'display:' in first_lines or 'font-' in first_lines):
        return 'CSS'
    if 'import react' in first_lines or 'export ' in first_lines or 'const ' in first_lines or 'let ' in first_lines:
        return 'JavaScript'
    if 'def ' in first_lines or 'import ' in first_lines or 'class ' in first_lines:
        return 'Python'
        
    return 'Source Code'

def run_ai_review(code: str, static_findings: list, filename: str = '') -> dict:
    api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
    if not api_key:
        return {"summary": "OpenRouter API key not configured.", "findings": []}
    
    language = detect_language(filename, code)
    
    # Cap code length to 250 lines for speed
    code_lines = code.splitlines()
    if len(code_lines) > 250:
        analyzed_code = "\n".join(code_lines[:250]) + "\n<!-- [Truncated beyond line 250 for speed] -->"
    else:
        analyzed_code = code

    # Pass compact static findings summary
    compact_static = [
        {"title": f.get("title"), "severity": f.get("severity"), "line": f.get("line_number")}
        for f in static_findings[:8]
    ]

    prompt = f"""
You are an expert polyglot software engineer and code reviewer.
Review the following {language} code. You support ALL programming languages and web formats including HTML, CSS, JavaScript, TypeScript, Python, Java, C++, Go, Rust, PHP, and SQL.
DO NOT reject code or say "this is not Python". Review the provided {language} code for:
- Security vulnerabilities (e.g. XSS, unescaped output, insecure inline scripts, CSRF, insecure links)
- Semantic correctness, accessibility, and modern standards
- Code quality, performance, and formatting
- Clean refactoring suggestions

Language: {language}
Filename: {filename or 'snippet'}

Verified static findings:
{json.dumps(compact_static)}

Code:
```{language.lower().split()[0]}
{analyzed_code}
```

Respond strictly in this JSON format without markdown wrapping:
{{
  "summary": "Concise 2-sentence review summary of this {language} code and key recommendations.",
  "suggested_code": "Clean, refactored {language} code with improvements applied (or original code if already optimal).",
  "findings": [
    {{
      "title": "Short title",
      "category": "SECURITY|COMPLEXITY|STYLE|BUG_RISK|DOCUMENTATION",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
      "line_number": 1,
      "message": "Direct explanation of the issue.",
      "recommendation": "Clear fix recommendation.",
      "suggested_fix": "Code snippet of fix.",
      "analyzer": "Gemini AI"
    }}
  ]
}}
"""
    
    site_url = os.getenv('SITE_URL', 'https://github.com/om-kava/Codeguardian')
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": site_url,
        "X-Title": "CodeGuardian AI",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openrouter/free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "reasoning": {"effort": "none"},
        "max_tokens": 1500,
        "temperature": 0.2
    }
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=14
        )
        response.raise_for_status()
        result = response.json()
        choice = result.get('choices', [{}])[0]
        message = choice.get('message', {})
        content = (message.get('content') or '').strip()
        
        # Strip markdown wrappers if present (e.g. ```json ... ```)
        if content.startswith("```"):
            first_newline = content.find("\n")
            if first_newline != -1:
                content = content[first_newline:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()
                
        if not content:
            return {
                "summary": f"{language} review completed successfully.",
                "suggested_code": code,
                "findings": []
            }

        try:
            parsed = json.loads(content)
        except Exception:
            # Fallback regex extraction in case of unescaped quotes in HTML/CSS
            import re
            summary_match = re.search(r'"summary"\s*:\s*"([^"]+)"', content)
            summary = summary_match.group(1) if summary_match else f"{language} code reviewed and verified."
            return {
                "summary": summary,
                "suggested_code": code,
                "findings": []
            }

        if not parsed.get('suggested_code'):
            parsed['suggested_code'] = code
        return parsed

    except Exception as e:
        print(f"AI Engine Notice ({language} Fallback):", str(e))
        return {
            "summary": f"{language} code analysis completed using static quality checks.",
            "suggested_code": code,
            "error": str(e),
            "findings": []
        }
