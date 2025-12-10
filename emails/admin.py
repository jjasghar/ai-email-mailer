from django.contrib import admin
from .models import SeedEmail, EmailTemplate, Recipient, Campaign, SentEmail


@admin.register(SeedEmail)
class SeedEmailAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    search_fields = ['title', 'description']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'created_at']
    list_filter = ['is_default']


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'created_at']
    search_fields = ['email', 'name']


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'seed_email', 'status', 'created_at', 'sent_at']
    list_filter = ['status', 'created_at']
    filter_horizontal = ['recipients']


@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'recipient', 'sent_at']
    list_filter = ['campaign', 'sent_at']
    readonly_fields = ['sent_at']
