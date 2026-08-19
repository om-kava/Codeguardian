from django.db import models
from apps.reviews.models import Review

class AIAnalysis(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='ai_analyses')
    model_name = models.CharField(max_length=100, default='gemini-1.5-pro')
    prompt_version = models.CharField(max_length=50, default='v1.0')
    response_status = models.CharField(max_length=50) # e.g. 'SUCCESS', 'FAILED'
    raw_response = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"AI Analysis for {self.review} - {self.response_status}"
