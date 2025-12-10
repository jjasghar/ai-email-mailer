from django.db import models
from django.contrib.auth.models import User


class SeedEmail(models.Model):
    """Seed email that serves as the base template for AI rewriting."""
    title = models.CharField(max_length=200)
    content_markdown = models.TextField(help_text="Markdown content of the seed email")
    description = models.TextField(blank=True, help_text="Description of this seed email")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Seed Email'
        verbose_name_plural = 'Seed Emails'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class EmailTemplate(models.Model):
    """HTML email template with header and footer."""
    name = models.CharField(max_length=200)
    header_html = models.TextField(blank=True, help_text="HTML header content")
    footer_html = models.TextField(blank=True, help_text="HTML footer content")
    is_default = models.BooleanField(default=False, help_text="Use as default template")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default template
            EmailTemplate.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Recipient(models.Model):
    """Email recipient."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Recipient'
        verbose_name_plural = 'Recipients'
        ordering = ['email']
    
    def __str__(self):
        return f"{self.name} ({self.email})" if self.name else self.email


class Campaign(models.Model):
    """Email campaign that sends unique AI-rewritten emails to recipients."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
    ]
    
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=300)
    seed_email = models.ForeignKey(SeedEmail, on_delete=models.CASCADE, related_name='campaigns')
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    recipients = models.ManyToManyField(Recipient, related_name='campaigns')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    ai_prompt = models.TextField(blank=True, help_text="Additional prompt for AI rewriting (optional)")
    variable_mappings = models.TextField(blank=True, help_text="JSON mapping of variables to values or recipient fields")
    sending_progress = models.IntegerField(default=0, help_text="Number of emails sent so far")
    sending_total = models.IntegerField(default=0, help_text="Total number of emails to send")
    sending_current_email = models.CharField(max_length=255, blank=True, help_text="Currently processing email")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class SentEmail(models.Model):
    """Record of each unique email sent to a recipient."""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='sent_emails')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='sent_emails')
    content_markdown = models.TextField(help_text="AI-rewritten markdown content")
    content_html = models.TextField(help_text="Final HTML content sent")
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Sent Email'
        verbose_name_plural = 'Sent Emails'
        ordering = ['-sent_at']
        unique_together = ['campaign', 'recipient']
    
    def __str__(self):
        return f"{self.campaign.title} -> {self.recipient.email}"
