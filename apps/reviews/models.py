from django.db import models
from apps.projects.models import Project, CodeSubmission

class Review(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews')
    code_submission = models.ForeignKey(CodeSubmission, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    overall_score = models.IntegerField(default=100)
    security_score = models.IntegerField(default=100)
    quality_score = models.IntegerField(default=100)
    maintainability_score = models.IntegerField(default=100)
    complexity_score = models.IntegerField(default=100)
    performance_score = models.IntegerField(default=100)
    best_practices_score = models.IntegerField(default=100)
    summary = models.TextField(blank=True, default='')
    suggested_code = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.id} for {self.project.name} (Score: {self.overall_score})"

    @property
    def total_issues(self):
        return self.issues.count()

    @property
    def total_findings(self):
        return self.issues.count()

    @property
    def filename(self):
        return self.code_submission.file_name if self.code_submission else 'main.py'

    @property
    def letter_grade(self):
        score = self.overall_score
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    @property
    def raw_code(self):
        return self.code_submission.source_code if self.code_submission else ''

    @property
    def version(self):
        sibling_reviews = list(self.project.reviews.all().order_by('created_at'))
        try:
            return sibling_reviews.index(self) + 1
        except ValueError:
            return 1

class ReviewIssue(models.Model):
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
        ('INFO', 'Info'),
    ]

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='issues')
    category = models.CharField(max_length=50)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    recommendation = models.TextField(blank=True, default='')
    suggested_fix = models.TextField(blank=True, default='')
    line_number = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=50)  # e.g., 'Bandit', 'Gemini AI'
    rule_id = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['line_number', 'severity']

    def __str__(self):
        return f"[{self.severity}] {self.title} (Line {self.line_number or 'N/A'})"
