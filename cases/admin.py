from django.contrib import admin
from .models import Case, OfficerNote, NotificationSubscription, AnonymousReport

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('ob_number', 'title', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('ob_number', 'title')

@admin.register(OfficerNote)
class OfficerNoteAdmin(admin.ModelAdmin):
    list_display = ('case', 'created_at')
    list_filter = ('created_at',)

@admin.register(NotificationSubscription)
class NotificationSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'case')

@admin.register(AnonymousReport)
class AnonymousReportAdmin(admin.ModelAdmin):
    list_display = ('created_at',)
