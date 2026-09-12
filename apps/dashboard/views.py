from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.projects.models import Project, CodeSubmission
from apps.reviews.models import Review, ReviewIssue

def index_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_page')
    return render(request, 'login.html')

@login_required(login_url='/login/')
def dashboard_view(request):
    projects = Project.objects.filter(owner=request.user)
    recent_reviews = Review.objects.filter(project__owner=request.user).order_by('-created_at')[:5]

    total_projects = projects.count()
    total_reviews = Review.objects.filter(project__owner=request.user).count()
    avg_score = 0
    if total_reviews > 0:
        total_score = sum(r.overall_score for r in Review.objects.filter(project__owner=request.user))
        avg_score = round(total_score / total_reviews, 1)
        
    total_issues = ReviewIssue.objects.filter(review__project__owner=request.user).count()

    context = {
        'total_projects': total_projects,
        'total_reviews': total_reviews,
        'avg_score': avg_score,
        'total_issues': total_issues,
        'recent_reviews': recent_reviews,
        'projects': projects,
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='/login/')
def projects_view(request):
    projects = Project.objects.filter(owner=request.user)
    return render(request, 'projects.html', {'projects': projects})

@login_required(login_url='/login/')
def project_detail_view(request, project_id):
    project = Project.objects.get(id=project_id, owner=request.user)
    reviews = project.reviews.all().order_by('-created_at')
    
    # Chronological list for chart
    chrono_reviews = list(reviews)[::-1]
    chart_labels = [f"R{r.id}" for r in chrono_reviews]
    chart_scores = [r.overall_score for r in chrono_reviews]

    return render(request, 'project_detail.html', {
        'project': project, 
        'reviews': reviews,
        'chart_labels': chart_labels,
        'chart_scores': chart_scores,
    })

@login_required(login_url='/login/')
def review_studio_view(request):
    projects = Project.objects.filter(owner=request.user)
    selected_project_id = request.GET.get('project')
    return render(request, 'review_studio.html', {'projects': projects, 'selected_project_id': selected_project_id})

@login_required(login_url='/login/')
def review_report_view(request, review_id):
    review = Review.objects.get(id=review_id, project__owner=request.user)
    findings = review.issues.all()
    project_reviews = review.project.reviews.exclude(id=review.id).order_by('-created_at')
    return render(request, 'review_report.html', {
        'review': review, 
        'findings': findings,
        'other_reviews': project_reviews
    })

@login_required(login_url='/login/')
def compare_view(request):
    projects = Project.objects.filter(owner=request.user)
    selected_project_id = request.GET.get('project')
    return render(request, 'compare.html', {
        'projects': projects,
        'selected_project_id': selected_project_id
    })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_page')
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_page')
    return render(request, 'register.html')
