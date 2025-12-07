from django.core.management.base import BaseCommand
from cases.models import Case, OfficerNote
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        # Create Cases
        case1 = Case.objects.create(
            ob_number='OB/2025/001',
            title='Theft at Central Market',
            description='Reported theft of a mobile phone at the main entrance.',
            status='investigation',
            created_at=timezone.now() - timedelta(days=5)
        )
        
        case2 = Case.objects.create(
            ob_number='OB/2025/002',
            title='Assault Case - Westlands',
            description='Physical altercation between two individuals.',
            status='court',
            court_date=timezone.now() + timedelta(days=10),
            created_at=timezone.now() - timedelta(days=10)
        )

        case3 = Case.objects.create(
            ob_number='OB/2025/003',
            title='Traffic Incident',
            description='Minor collision involving two vehicles.',
            status='judgement',
            court_date=timezone.now() - timedelta(days=2),
            created_at=timezone.now() - timedelta(days=20)
        )

        # Create Notes
        OfficerNote.objects.create(
            case=case1,
            note='Suspect identified via CCTV footage.'
        )
        OfficerNote.objects.create(
            case=case2,
            note='Witness statements recorded.'
        )
        OfficerNote.objects.create(
            case=case2,
            note='Medical report received.'
        )
        OfficerNote.objects.create(
            case=case3,
            note='Both parties agreed to settle out of court.'
        )

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data'))
