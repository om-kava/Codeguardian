import ast
import re
import tempfile
import os
import subprocess
import json

class BanditAnalyzer:
    def analyze(self, code: str):
        findings = []

        # Try running Bandit CLI if available
        bandit_findings = self._run_bandit_cli(code)
        if bandit_findings is not None:
            return bandit_findings

        # Fallback security AST inspection if CLI run fails or unavailable
        return self._fallback_security_scan(code)

    def _run_bandit_cli(self, code: str):
        try:
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name

            try:
                result = subprocess.run(
                    ['bandit', '-f', 'json', temp_path],
                    capture_output=True, text=True, timeout=10
                )
                if result.stdout:
                    data = json.loads(result.stdout)
                    findings = []
                    for issue in data.get('results', []):
                        severity_map = {'HIGH': 'HIGH', 'MEDIUM': 'MEDIUM', 'LOW': 'LOW'}
                        findings.append({
                            'analyzer': 'BANDIT',
                            'category': 'SECURITY',
                            'severity': severity_map.get(issue.get('issue_severity'), 'MEDIUM'),
                            'line_number': issue.get('line_number'),
                            'code_snippet': issue.get('code', '').strip(),
                            'title': issue.get('issue_text', 'Security Issue'),
                            'message': f"[{issue.get('test_id')}] {issue.get('issue_text')}",
                            'recommendation': f"Refer to Bandit test {issue.get('test_id')} for remediation.",
                            'rule_id': issue.get('test_id', 'B000')
                        })
                    return findings
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception:
            return None

    def _fallback_security_scan(self, code: str):
        findings = []
        lines = code.splitlines()

        # Regex patterns for common security issues
        secret_patterns = [
            (r'(?i)(api[_-]?key|secret[_-]?key|password|passwd|auth[_-]?token)\s*=\s*[\'"][^\'"]{5,}[\'"]', 
             'Hardcoded Secret / Credentials', 'HIGH', 'B105'),
            (r'eval\s*\(', 'Use of dangerous function eval()', 'CRITICAL', 'B307'),
            (r'exec\s*\(', 'Use of dangerous function exec()', 'CRITICAL', 'B102'),
            (r'shell\s*=\s*True', 'Subprocess call with shell=True', 'HIGH', 'B602'),
            (r'pickle\.loads?\s*\(', 'Unsafe deserialization using pickle', 'HIGH', 'B301'),
            (r'md5\s*\(|sha1\s*\(', 'Use of weak cryptographic hash function', 'MEDIUM', 'B303'),
            (r'verify\s*=\s*False', 'Unverified HTTPS connection (verify=False)', 'HIGH', 'B501'),
        ]

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Ignore comments
            if stripped.startswith('#'):
                continue

            for pattern, title, severity, rule_id in secret_patterns:
                if re.search(pattern, line):
                    findings.append({
                        'analyzer': 'BANDIT',
                        'category': 'SECURITY',
                        'severity': severity,
                        'line_number': i,
                        'code_snippet': stripped,
                        'title': title,
                        'message': f"Security risk identified on line {i}: '{title}'.",
                        'recommendation': 'Refactor to store secrets in environment variables or use safe alternative functions.',
                        'rule_id': rule_id
                    })

        return findings
