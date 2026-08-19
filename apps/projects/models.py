from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    repository_url = models.URLField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    @property
    def total_reviews(self):
        return self.reviews.count()

    @property
    def average_score(self):
        total = self.reviews.count()
        if total == 0:
            return 0
        sum_scores = sum(r.overall_score for r in self.reviews.all())
        return round(sum_scores / total, 1)

class CodeSubmission(models.Model):
    SUBMISSION_TYPES = [
        ('PASTE', 'Pasted Code'),
        ('UPLOAD', 'File Upload'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='submissions')
    source_code = models.TextField()
    file_name = models.CharField(max_length=255, default='script.py')
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPES, default='PASTE')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.name} - {self.file_name}"
