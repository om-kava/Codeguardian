from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.projects.models import Project, CodeSubmission
from apps.analyzer.engine import run_analysis

class Command(BaseCommand):
    help = 'Seed database with demo user, projects, and code review history'

    def handle(self, *args, **options):
        self.stdout.write("Seeding CodeGuardian AI demo data into MySQL database...")

        # 1. Create Demo User
        user, created = User.objects.get_or_create(username='demo', defaults={
            'email': 'demo@codeguardian.ai',
            'first_name': 'Alex',
            'last_name': 'Developer'
        })
        if created:
            user.set_password('demo12345')
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user: username='demo', password='demo12345'"))
        else:
            self.stdout.write("Demo user 'demo' already exists.")

        # 2. Create Demo Projects
        project, _ = Project.objects.get_or_create(
            name="E-Commerce Payment Gateway",
            owner=user,
            defaults={
                "description": "Core payment processing microservice with Stripe and PayPal integrations",
                "repository_url": "https://github.com/demo/payment-service",
            }
        )

        project2, _ = Project.objects.get_or_create(
            name="User Authentication Microservice",
            owner=user,
            defaults={
                "description": "JWT-based SSO identity provider and session manager",
                "repository_url": "https://github.com/demo/auth-service",
            }
        )

        # 3. Seed Code Review Version 1
        code_v1 = """import os
import sys

API_SECRET_KEY = "sk-live-998877665544332211" # Hardcoded secret key

def process_transaction(user_id, amount, card_details=[]):
    print("Processing transaction for user:", user_id)
    
    # Dangerous eval usage
    auth_check = eval("amount > 0")
    
    if amount > 10000:
        print("High value transaction!")
        
    try:
        os.system("echo " + user_id)
    except:
        pass
        
    return True
"""
        
        if not project.submissions.filter(file_name="payment_processor.py").exists():
            self.stdout.write("Running analysis for demo review v1...")
            submission1 = CodeSubmission.objects.create(
                project=project,
                source_code=code_v1,
                file_name="payment_processor.py",
                submission_type='PASTE'
            )
            try:
                review1 = run_analysis(submission1)
                self.stdout.write(self.style.SUCCESS(f"Generated review v1 with score {review1.overall_score}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Note: Review v1 analysis completed with fallback: {e}"))

        # 4. Seed Code Review Version 2 (Refactored secure code)
        code_v2 = """import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Retrieve key safely from environment variable
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
        if project.submissions.count() < 2:
            self.stdout.write("Running analysis for demo review v2...")
            submission2 = CodeSubmission.objects.create(
                project=project,
                source_code=code_v2,
                file_name="payment_processor.py",
                submission_type='PASTE'
            )
            try:
                review2 = run_analysis(submission2)
                self.stdout.write(self.style.SUCCESS(f"Generated review v2 with score {review2.overall_score}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Note: Review v2 analysis completed with fallback: {e}"))

        self.stdout.write(self.style.SUCCESS("Successfully seeded CodeGuardian AI demo data into MySQL!"))
