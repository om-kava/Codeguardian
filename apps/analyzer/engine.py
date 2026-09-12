from .ast_analyzer import ASTAnalyzer
from .bandit_analyzer import BanditAnalyzer
from .radon_analyzer import RadonAnalyzer
from .ruff_analyzer import RuffAnalyzer
from .polyglot_analyzer import PolyglotAnalyzer
from .scoring import QualityScorer

class ReviewEngine:
    def __init__(self):
        self.ast_analyzer = ASTAnalyzer()
        self.bandit_analyzer = BanditAnalyzer()
        self.radon_analyzer = RadonAnalyzer()
        self.ruff_analyzer = RuffAnalyzer()
        self.polyglot_analyzer = PolyglotAnalyzer()
        self.scorer = QualityScorer()

    def run_review(self, submission):
        code = submission.source_code
        all_findings = []
        combined_metrics = {
            'lines_of_code': len(code.splitlines()),
            'functions': 0,
            'classes': 0,
            'docstrings_missing': 0,
            'globals_used': 0,
            'cyclomatic_complexity_avg': 1.0,
            'maintainability_index': 100.0,
            'comments': 0,
        }

        filename = getattr(submission, 'file_name', getattr(submission, 'filename', 'main.py')) or 'main.py'
        is_python = filename.lower().endswith('.py')

        # 1. Polyglot Static & Security Analysis (All Languages)
        poly_findings, poly_metrics = self.polyglot_analyzer.analyze(code, filename)
        all_findings.extend(poly_findings)
        combined_metrics.update(poly_metrics)

        # 2. Python-specific Deep Static Analyzers
        if is_python:
            # AST Analysis
            ast_findings, ast_metrics = self.ast_analyzer.analyze(code)
            all_findings.extend(ast_findings)
            combined_metrics.update(ast_metrics)
    
            # Bandit Security Analysis
            bandit_findings = self.bandit_analyzer.analyze(code)
            all_findings.extend(bandit_findings)
    
            # Radon Complexity Analysis
            radon_findings, radon_metrics = self.radon_analyzer.analyze(code)
            all_findings.extend(radon_findings)
            combined_metrics.update(radon_metrics)
    
            # Ruff Style Analysis
            ruff_findings = self.ruff_analyzer.analyze(code)
            all_findings.extend(ruff_findings)

        # Normalize findings (remove exact duplicates)
        unique_findings = []
        seen = set()
        for f in all_findings:
            sig = (f.get('line_number'), f.get('title'), f.get('severity'))
            if sig not in seen:
                seen.add(sig)
                unique_findings.append(f)

        return unique_findings, combined_metrics

def run_analysis(submission):
    # This is the main pipeline coordinator
    from apps.reviews.models import Review, ReviewIssue
    from apps.ai_engine.service import run_ai_review

    engine = ReviewEngine()
    static_findings, metrics = engine.run_review(submission)
    
    # 5. Gemini AI Analysis
    filename = getattr(submission, 'file_name', 'main.py') or 'main.py'
    ai_result = run_ai_review(submission.source_code, static_findings, filename=filename)

    # 6. Quality Scoring
    scorer = QualityScorer()
    # Combine findings
    all_final_findings = static_findings + ai_result.get('findings', [])
    score_res = scorer.calculate_score(all_final_findings, metrics)

    # Save to database
    review = Review.objects.create(
        project=submission.project,
        code_submission=submission,
        overall_score=score_res.get('overall_score', score_res.get('quality_score', 100)),
        security_score=score_res.get('security_score', 100),
        quality_score=score_res.get('quality_score', 100),
        maintainability_score=score_res.get('maintainability_score', 100),
        complexity_score=score_res.get('complexity_score', 100),
        performance_score=score_res.get('performance_score', 100),
        best_practices_score=score_res.get('best_practices_score', 100),
        summary=ai_result.get('summary', 'Static analysis completed.'),
        suggested_code=ai_result.get('suggested_code', submission.source_code)
    )

    for finding in all_final_findings:
        ReviewIssue.objects.create(
            review=review,
            category=finding.get('category', 'STYLE'),
            severity=finding.get('severity', 'INFO'),
            title=finding.get('title', 'Issue'),
            description=finding.get('message', ''),
            recommendation=finding.get('recommendation', ''),
            suggested_fix=finding.get('suggested_fix', ''),
            line_number=finding.get('line_number'),
            source=finding.get('analyzer', 'Static'),
            rule_id=finding.get('rule_id', '')
        )

    return review
