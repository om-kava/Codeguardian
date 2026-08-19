import ast

class ASTAnalyzer:
    def analyze(self, code: str):
        findings = []
        metrics = {
            'functions': 0,
            'classes': 0,
            'docstrings_missing': 0,
            'globals_used': 0,
            'max_depth': 0,
            'lines_of_code': len(code.splitlines())
        }

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            findings.append({
                'analyzer': 'AST',
                'category': 'BUG_RISK',
                'severity': 'CRITICAL',
                'line_number': e.lineno or 1,
                'code_snippet': e.text.strip() if e.text else '',
                'title': 'Syntax Error',
                'message': f"Syntax error encountered: {e.msg}",
                'recommendation': 'Fix the syntax error so python can parse and execute the code properly.',
                'rule_id': 'AST001'
            })
            return findings, metrics

        # Inspect nodes
        for node in ast.walk(tree):
            # Function definitions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics['functions'] += 1
                docstring = ast.get_docstring(node)
                if not docstring:
                    metrics['docstrings_missing'] += 1
                    findings.append({
                        'analyzer': 'AST',
                        'category': 'DOCUMENTATION',
                        'severity': 'LOW',
                        'line_number': node.lineno,
                        'code_snippet': f"def {node.name}(...)",
                        'title': f"Missing Docstring in Function '{node.name}'",
                        'message': f"Function '{node.name}' does not contain a docstring explaining its behavior.",
                        'recommendation': f"Add a docstring to '{node.name}' describing parameters, return values, and exceptions.",
                        'rule_id': 'AST002'
                    })

            # Class definitions
            elif isinstance(node, ast.ClassDef):
                metrics['classes'] += 1
                docstring = ast.get_docstring(node)
                if not docstring:
                    metrics['docstrings_missing'] += 1
                    findings.append({
                        'analyzer': 'AST',
                        'category': 'DOCUMENTATION',
                        'severity': 'LOW',
                        'line_number': node.lineno,
                        'code_snippet': f"class {node.name}:",
                        'title': f"Missing Docstring in Class '{node.name}'",
                        'message': f"Class '{node.name}' lacks a class-level docstring.",
                        'recommendation': f"Add a docstring to class '{node.name}'.",
                        'rule_id': 'AST003'
                    })

            # Global statements
            elif isinstance(node, ast.Global):
                metrics['globals_used'] += len(node.names)
                findings.append({
                    'analyzer': 'AST',
                    'category': 'STYLE',
                    'severity': 'MEDIUM',
                    'line_number': node.lineno,
                    'code_snippet': f"global {', '.join(node.names)}",
                    'title': "Global Statement Usage",
                    'message': f"Use of 'global' keyword for variables ({', '.join(node.names)}) makes code harder to test and maintain.",
                    'recommendation': 'Avoid global variables. Pass state explicitly via function arguments or class instances.',
                    'rule_id': 'AST004'
                })

            # Bare Exception handlers
            elif isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    findings.append({
                        'analyzer': 'AST',
                        'category': 'BUG_RISK',
                        'severity': 'HIGH',
                        'line_number': node.lineno,
                        'code_snippet': 'except:',
                        'title': 'Bare Except Clause',
                        'message': 'Bare `except:` catches system-exiting exceptions like KeyboardInterrupt and SystemExit.',
                        'recommendation': 'Catch specific exceptions (e.g. `except Exception:` or `except ValueError:`).',
                        'rule_id': 'AST005'
                    })

        return findings, metrics
