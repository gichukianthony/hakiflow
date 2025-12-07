from django.db import models

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

    def __str__(self):
        return f"{self.ob_number} - {self.title}"

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
