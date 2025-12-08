from django.db import models
from django.contrib.auth.models import User

class Case(models.Model):
    STATUS_CHOICES = [
        ('investigation', 'Investigation'),
        ('dci', 'DCI'),
        ('court', 'Court'),
        ('judgement', 'Judgement'),
    ]

    ob_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='investigation')
    court_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Optional citizen identifier used to associate cases with a registering user
    id_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.ob_number} - {self.title}"


class CitizenProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='citizen_profile')
    id_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.user.username} ({self.id_number})"

class OfficerNote(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.case.ob_number} at {self.created_at}"

class NotificationSubscription(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='subscriptions')
    email = models.EmailField()

    def __str__(self):
        return f"{self.email} subscribed to {self.case.ob_number}"

class AnonymousReport(models.Model):
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report at {self.created_at}"
