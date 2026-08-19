from rest_framework import serializers
from .models import Review, ReviewIssue

class ReviewIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewIssue
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    issues = ReviewIssueSerializer(many=True, read_only=True)
    version = serializers.IntegerField(read_only=True)
    filename = serializers.CharField(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'project', 'code_submission', 'overall_score',
            'security_score', 'quality_score', 'maintainability_score',
            'complexity_score', 'performance_score', 'best_practices_score',
            'summary', 'created_at', 'issues', 'version', 'filename'
        ]
        read_only_fields = fields
