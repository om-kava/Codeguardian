from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.projects.models import Project
from apps.reviews.models import CodeReview, Finding
from apps.analyzer.engine import ReviewEngine

class Command(BaseCommand):
    help = 'Seed database with demo user, projects, and code review history'

    def handle(self, *args, **options):
        self.stdout.write("Seeding CodeGuardian AI demo data...")

        # 1. Create Demo User
        user, created = User.objects.get_or_create(username='demo', defaults={
            'email': 'demo@codeguardian.ai',
            'first_name': 'Alex',
            'last_name': 'Developer'
        })
        if created:
            user.set_password('demo12345')
            user.save()
            self.stdout.write("Created demo user: username='demo', password='demo12345'")

        # 2. Create Demo Project
        project, _ = Project.objects.get_or_create(
            name="E-Commerce Payment Gateway",
            owner=user,
            defaults={
                "description": "Core payment processing microservice with Stripe and PayPal integrations",
                "repository_url": "https://github.com/demo/payment-service",
                "language": "Python"
            }
        )

        project2, _ = Project.objects.get_or_create(
            name="User Authentication Microservice",
            owner=user,
            defaults={
                "description": "JWT-based SSO identity provider and session manager",
                "repository_url": "https://github.com/demo/auth-service",
                "language": "Python"
            }
        )

        # 3. Seed Code Review Version 1 (Code with vulnerabilities and quality issues)
        code_v1 = """import os
import sys

API_SECRET_KEY = "sk-live-998877665544332211" # Hardcoded key

def process_transaction(user_id, amount, card_details=[]):
    print("Processing transaction for user:", user_id)
    
    # Dangerous eval
    auth_check = eval("amount > 0")
    
    if amount > 10000:
        print("High value transaction!")
        
    try:
        os.system("echo " + user_id)
    except:
        pass
        
    return True
"""
        
        engine = ReviewEngine()
        
        if not CodeReview.objects.filter(project=project, version=1).exists():
            self.stdout.write("Running analysis for demo review v1...")
            res1 = engine.run_review(code_v1, filename="payment_processor.py")
            
            review1 = CodeReview.objects.create(
                project=project,
                user=user,
                filename="payment_processor.py",
                version=1,
                raw_code=code_v1,
                quality_score=res1['quality_score'],
                letter_grade=res1['letter_grade'],
                summary=res1['summary'],
                suggested_code=res1['suggested_code'],
                metrics_json=res1['metrics'],
            )

            for f in res1['findings']:
                Finding.objects.create(
                    review=review1,
                    analyzer=f.get('analyzer', 'AST'),
                    category=f.get('category', 'STYLE'),
                    severity=f.get('severity', 'INFO'),
                    line_number=f.get('line_number'),
                    code_snippet=f.get('code_snippet', ''),
                    title=f.get('title', ''),
                    message=f.get('message', ''),
                    recommendation=f.get('recommendation', ''),
                    rule_id=f.get('rule_id', '')
                )

        # 4. Seed Code Review Version 2 (Refactored code)
        code_v2 = """import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Retrieve key from environment variable
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "")

def process_transaction(user_id: str, amount: float, card_details: Dict = None) -> bool:
    \"\"\"
    Processes credit card transaction securely and records audit logs.
    \"\"\"
    if card_details is None:
        card_details = {}

    logger.info("Processing transaction for user: %s", user_id)
    
    if amount <= 0:
        logger.warning("Invalid transaction amount: %s", amount)
        return False
        
    if amount > 10000:
        logger.info("High value transaction flagged for review")
        
    return True
"""
        if not CodeReview.objects.filter(project=project, version=2).exists():
            self.stdout.write("Running analysis for demo review v2...")
            res2 = engine.run_review(code_v2, filename="payment_processor.py")
            
            review2 = CodeReview.objects.create(
                project=project,
                user=user,
                filename="payment_processor.py",
                version=2,
                raw_code=code_v2,
                quality_score=res2['quality_score'],
                letter_grade=res2['letter_grade'],
                summary=res2['summary'],
                suggested_code=res2['suggested_code'],
                metrics_json=res2['metrics'],
            )

            for f in res2['findings']:
                Finding.objects.create(
                    review=review2,
                    analyzer=f.get('analyzer', 'AST'),
                    category=f.get('category', 'STYLE'),
                    severity=f.get('severity', 'INFO'),
                    line_number=f.get('line_number'),
                    code_snippet=f.get('code_snippet', ''),
                    title=f.get('title', ''),
                    message=f.get('message', ''),
                    recommendation=f.get('recommendation', ''),
                    rule_id=f.get('rule_id', '')
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded CodeGuardian AI demo data!"))
