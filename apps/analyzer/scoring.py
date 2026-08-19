class QualityScorer:
    WEIGHTS = {
        'CRITICAL': 15.0,
        'HIGH': 10.0,
        'MEDIUM': 5.0,
        'LOW': 2.0,
        'INFO': 1.0,
    }

    def calculate_score(self, findings: list, metrics: dict):
        total_deduction = 0.0
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        category_counts = {'SECURITY': 0, 'COMPLEXITY': 0, 'STYLE': 0, 'BUG_RISK': 0, 'DOCUMENTATION': 0}

        for finding in findings:
            sev = finding.get('severity', 'INFO').upper()
            cat = finding.get('category', 'STYLE').upper()

            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            category_counts[cat] = category_counts.get(cat, 0) + 1

            total_deduction += self.WEIGHTS.get(sev, 1.0)

        # Maintainability index penalty if low
        mi = metrics.get('maintainability_index', 100.0)
        if mi < 60:
            total_deduction += (60.0 - mi) * 0.3

        quality_score = max(0.0, min(100.0, round(100.0 - total_deduction, 1)))

        if quality_score >= 90.0:
            letter_grade = 'A'
        elif quality_score >= 80.0:
            letter_grade = 'B'
        elif quality_score >= 70.0:
            letter_grade = 'C'
        elif quality_score >= 60.0:
            letter_grade = 'D'
        else:
            letter_grade = 'F'

        return {
            'quality_score': quality_score,
            'letter_grade': letter_grade,
            'severity_counts': severity_counts,
            'category_counts': category_counts,
        }
