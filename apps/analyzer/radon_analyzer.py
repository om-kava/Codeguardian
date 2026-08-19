import ast

class RadonAnalyzer:
    def analyze(self, code: str):
        findings = []
        metrics = {
            'cyclomatic_complexity_avg': 1.0,
            'maintainability_index': 100.0,
            'loc': len(code.splitlines()),
            'comments': 0,
        }

        # Count comment lines
        for line in code.splitlines():
            if line.strip().startswith('#'):
                metrics['comments'] += 1

        try:
            # Try importing radon libraries if installed
            from radon.complexity import cc_visit, cc_rank
            from radon.metrics import mi_visit

            try:
                blocks = cc_visit(code)
                total_cc = 0
                if blocks:
                    for block in blocks:
                        cc = block.complexity
                        total_cc += cc
                        rank = cc_rank(cc)
    
                        if cc > 10:
                            severity = 'CRITICAL' if cc > 20 else 'HIGH' if cc > 14 else 'MEDIUM'
                            findings.append({
                                'analyzer': 'RADON',
                                'category': 'COMPLEXITY',
                                'severity': severity,
                                'line_number': block.lineno,
                                'code_snippet': f"{block.letter} {block.name}",
                                'title': f"High Cyclomatic Complexity in {block.name} (CC = {cc})",
                                'message': f"Function/Class '{block.name}' has cyclomatic complexity of {cc} (Rank {rank}).",
                                'recommendation': 'Decompose this function into smaller, single-responsibility helper functions.',
                                'rule_id': 'RAD001'
                            })
    
                    metrics['cyclomatic_complexity_avg'] = round(total_cc / len(blocks), 2)
            except Exception:
                # If radon fails to parse (e.g. syntax error in non-python files), skip complexity findings
                pass
            
            try:
                mi = mi_visit(code, multi=True)
                metrics['maintainability_index'] = round(mi, 2)
                if mi < 50:
                    findings.append({
                        'analyzer': 'RADON',
                        'category': 'COMPLEXITY',
                        'severity': 'HIGH',
                        'line_number': 1,
                        'code_snippet': f"MI = {mi:.1f}",
                        'title': "Low Maintainability Index",
                        'message': f"Maintainability Index for this module is {mi:.1f} (under 50 is hard to maintain).",
                        'recommendation': 'Refactor complex functions, reduce module size, and improve code structure.',
                        'rule_id': 'RAD002'
                    })
            except Exception:
                pass

            return findings, metrics

        except ImportError:
            # Fallback AST-based cyclomatic complexity calculation
            return self._fallback_complexity(code, metrics)

    def _fallback_complexity(self, code: str, metrics: dict):
        findings = []
        try:
            tree = ast.parse(code)
        except Exception:
            return findings, metrics

        total_cc = 0
        func_count = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_count += 1
                cc = 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.And, ast.Or, ast.ExceptHandler, ast.With, ast.Assert)):
                        cc += 1
                
                total_cc += cc
                if cc > 10:
                    severity = 'CRITICAL' if cc > 20 else 'HIGH' if cc > 14 else 'MEDIUM'
                    findings.append({
                        'analyzer': 'RADON',
                        'category': 'COMPLEXITY',
                        'severity': severity,
                        'line_number': node.lineno,
                        'code_snippet': f"def {node.name}(...)",
                        'title': f"High Cyclomatic Complexity in '{node.name}' (CC = {cc})",
                        'message': f"Function '{node.name}' has decision branch complexity score of {cc}.",
                        'recommendation': 'Break down this function into smaller sub-routines.',
                        'rule_id': 'RAD001'
                    })

        if func_count > 0:
            metrics['cyclomatic_complexity_avg'] = round(total_cc / func_count, 2)
            # Estimate MI: 100 - (CC * 5)
            metrics['maintainability_index'] = max(0.0, round(100.0 - (metrics['cyclomatic_complexity_avg'] * 4.0), 2))

        return findings, metrics
