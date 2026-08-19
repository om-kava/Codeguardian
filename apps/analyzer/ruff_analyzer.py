import ast
import re

class RuffAnalyzer:
    def analyze(self, code: str):
        findings = []
        lines = code.splitlines()

        # Line length check
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                findings.append({
                    'analyzer': 'RUFF',
                    'category': 'STYLE',
                    'severity': 'LOW',
                    'line_number': i,
                    'code_snippet': line[:50] + '...',
                    'title': f"Line Too Long ({len(line)} > 100 chars)",
                    'message': f"Line {i} exceeds standard maximum length of 100 characters.",
                    'recommendation': 'Wrap line to stay within recommended line length limit.',
                    'rule_id': 'E501'
                })

            # Wildcard import check
            if re.search(r'from\s+[\w\.]+\s+import\s+\*', line):
                findings.append({
                    'analyzer': 'RUFF',
                    'category': 'STYLE',
                    'severity': 'MEDIUM',
                    'line_number': i,
                    'code_snippet': line.strip(),
                    'title': "Wildcard Import Detected",
                    'message': "Wildcard imports (`from module import *`) pollute namespace and reduce readability.",
                    'recommendation': 'Explicitly import required classes/functions.',
                    'rule_id': 'F403'
                })

            # Print statement check in backend code
            if re.search(r'^\s*print\s*\(', line):
                findings.append({
                    'analyzer': 'RUFF',
                    'category': 'STYLE',
                    'severity': 'INFO',
                    'line_number': i,
                    'code_snippet': line.strip(),
                    'title': "Console Print Statement",
                    'message': "Use of print() in production code instead of Python standard logging module.",
                    'recommendation': "Replace print() with Python `logging` logger.",
                    'rule_id': 'T201'
                })

        # AST-based Ruff style checks (mutable default args)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for default in node.args.defaults + node.args.kw_defaults:
                        if default and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            findings.append({
                                'analyzer': 'RUFF',
                                'category': 'BUG_RISK',
                                'severity': 'HIGH',
                                'line_number': node.lineno,
                                'code_snippet': f"def {node.name}(...)",
                                'title': "Mutable Default Argument",
                                'message': f"Function '{node.name}' uses a mutable default argument (list/dict/set).",
                                'recommendation': "Use `None` as default value and initialize mutable object inside function body.",
                                'rule_id': 'B006'
                            })
        except Exception:
            pass

        return findings
