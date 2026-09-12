from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Review, ReviewIssue
from .serializers import ReviewSerializer, ReviewIssueSerializer
from apps.projects.models import Project, CodeSubmission
from apps.reviews.github import GitHubFetcher
from apps.analyzer.engine import ReviewEngine, run_analysis
from apps.ai_engine.service import run_ai_review
from apps.analyzer.scoring import QualityScorer

class ProjectReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Review.objects.filter(project__id=project_id, project__owner=self.request.user)

class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Review.objects.filter(project__owner=self.request.user)
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project__id=project_id)
        return queryset

class ReviewDetailView(generics.RetrieveAPIView):
    serializer_class = ReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(project__owner=self.request.user)

class FetchGitHubView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        repo_url = request.data.get('repo_url')
        file_path = request.data.get('file_path', '')
        if not repo_url:
            return Response({"error": "repo_url is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        fetcher = GitHubFetcher()
        result = fetcher.fetch_code_or_tree(repo_url, file_path)
        return Response(result)

class AnalyzeInstantView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        filename = request.data.get('filename', 'main.py')
        
        if not code:
            return Response({"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        engine = ReviewEngine()
        
        # Create a dummy submission object
        class DummySubmission:
            def __init__(self, source_code, file_name):
                self.source_code = source_code
                self.file_name = file_name
        
        dummy_sub = DummySubmission(code, filename)
        static_findings, metrics = engine.run_review(dummy_sub)
        
        # Run AI analysis
        ai_result = run_ai_review(code, static_findings, filename=filename)
        
        # Quality Scoring
        scorer = QualityScorer()
        all_findings = static_findings + ai_result.get('findings', [])
        score_res = scorer.calculate_score(all_findings, metrics)
        
        score = score_res.get('overall_score', score_res.get('quality_score', 100))
        if score >= 90:
            grade = 'A'
        elif score >= 80:
            grade = 'B'
        elif score >= 70:
            grade = 'C'
        elif score >= 60:
            grade = 'D'
        else:
            grade = 'F'
            
        return Response({
            "quality_score": score,
            "letter_grade": grade,
            "summary": ai_result.get('summary', 'Instant analysis completed.'),
            "suggested_code": ai_result.get('suggested_code', code),
            "findings": all_findings
        })

class SubmitReviewView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get('project_id')
        filename = request.data.get('filename', 'main.py')
        code = request.data.get('code')
        
        if not project_id or not code:
            return Response({"error": "project_id and code are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            project = Project.objects.get(id=project_id, owner=request.user)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
            
        submission = CodeSubmission.objects.create(
            project=project,
            source_code=code,
            file_name=filename,
            submission_type='PASTE'
        )
        
        try:
            review = run_analysis(submission)
            return Response({
                "id": review.id,
                "message": "Review submitted successfully"
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AuditRepositoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({"error": "project_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            project = Project.objects.get(id=project_id, owner=request.user)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
            
        if not project.repository_url:
            return Response({"error": "Project has no repository URL configured."}, status=status.HTTP_400_BAD_REQUEST)
            
        fetcher = GitHubFetcher()
        repo_data = fetcher.fetch_all_repo_files_code(project.repository_url, max_files=5)
        
        if 'error' in repo_data:
            return Response({"error": repo_data['error']}, status=status.HTTP_400_BAD_REQUEST)
            
        files = repo_data.get('files', [])
        if not files:
            return Response({"error": "No valid code files found to audit."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Combine files and run analysis
        # For simplicity, we can concatenate the contents or analyze the primary file,
        # or aggregate findings from all files. Let's aggregate findings.
        engine = ReviewEngine()
        all_static_findings = []
        total_loc = 0
        
        class FileSubmission:
            def __init__(self, source_code):
                self.source_code = source_code

        for f in files:
            sub = FileSubmission(f['code'])
            static_findings, metrics = engine.run_review(sub)
            # Tag the findings with their file path so we know where they came from
            for finding in static_findings:
                finding['title'] = f"[{f['path']}] {finding.get('title', 'Issue')}"
            all_static_findings.extend(static_findings)
            total_loc += len(f['code'].splitlines())
            
        # Combine all files into a single prompt for a high-level summary
        combined_code = "\n\n".join([f"### File: {f['path']}\n{f['code']}" for f in files])
        
        # AI analysis across the files
        ai_result = run_ai_review(combined_code, all_static_findings, filename="Repository_Audit")
        
        # Quality Scoring
        scorer = QualityScorer()
        all_findings = all_static_findings + ai_result.get('findings', [])
        score_res = scorer.calculate_score(all_findings, {'lines_of_code': total_loc})
        
        # Create a submission representing the repository
        submission = CodeSubmission.objects.create(
            project=project,
            source_code=combined_code,
            file_name="Repository Audit",
            submission_type='PASTE'
        )
        
        review = Review.objects.create(
            project=project,
            code_submission=submission,
            overall_score=score_res.get('overall_score', score_res.get('quality_score', 100)),
            security_score=score_res.get('security_score', 100),
            quality_score=score_res.get('quality_score', 100),
            maintainability_score=score_res.get('maintainability_score', 100),
            complexity_score=score_res.get('complexity_score', 100),
            performance_score=score_res.get('performance_score', 100),
            best_practices_score=score_res.get('best_practices_score', 100),
            summary=ai_result.get('summary', 'Full Repository Audit Completed.'),
            suggested_code=ai_result.get('suggested_code', combined_code)
        )
        
        for finding in all_findings:
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
            
        return Response({"id": review.id, "message": "Repository audited successfully"}, status=status.HTTP_201_CREATED)

class CompareReviewsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        r1_id = request.query_params.get('review1')
        r2_id = request.query_params.get('review2')
        
        if not r1_id or not r2_id:
            return Response({"error": "review1 and review2 query parameters are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            r1 = Review.objects.get(id=r1_id, project__owner=request.user)
            r2 = Review.objects.get(id=r2_id, project__owner=request.user)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)
            
        score_delta = r2.overall_score - r1.overall_score
        
        r1_issues = list(r1.issues.all())
        r2_issues = list(r2.issues.all())
        
        resolved = []
        new_issues = []
        
        for issue1 in r1_issues:
            match = False
            for issue2 in r2_issues:
                if (issue1.rule_id and issue1.rule_id == issue2.rule_id) or \
                   (issue1.title == issue2.title and issue1.category == issue2.category):
                    match = True
                    break
            if not match:
                resolved.append(issue1)
                
        for issue2 in r2_issues:
            match = False
            for issue1 in r1_issues:
                if (issue1.rule_id and issue1.rule_id == issue2.rule_id) or \
                   (issue1.title == issue2.title and issue1.category == issue2.category):
                    match = True
                    break
            if not match:
                new_issues.append(issue2)
                
        return Response({
            "score_delta": float(score_delta),
            "resolved_count": len(resolved),
            "new_count": len(new_issues),
            "resolved_findings": ReviewIssueSerializer(resolved, many=True).data,
            "new_findings": ReviewIssueSerializer(new_issues, many=True).data,
            "review1": {
                "quality_score": r1.overall_score,
                "version": r1.version,
                "filename": r1.filename
            },
            "review2": {
                "quality_score": r2.overall_score,
                "version": r2.version,
                "filename": r2.filename
            }
        })
