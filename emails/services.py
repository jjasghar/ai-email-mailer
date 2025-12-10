"""
Email sending service.
"""
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags
from .models import Campaign, SentEmail
from .utils import rewrite_with_ollama, render_email_html, replace_variables
import json


def send_campaign(campaign):
    """
    Send campaign emails. Each recipient gets a unique AI-rewritten version.
    
    Args:
        campaign: Campaign instance
    
    Returns:
        Tuple of (sent_count, failed_count)
    """
    if campaign.status != 'draft':
        raise ValueError("Campaign must be in draft status to send")
    
    campaign.status = 'sending'
    recipients_list = list(campaign.recipients.all())
    campaign.sending_total = len(recipients_list)
    campaign.sending_progress = 0
    campaign.sending_current_email = ''
    campaign.save()
    
    sent_count = 0
    failed_count = 0
    
    # Load variable mappings
    variable_mappings = {}
    if campaign.variable_mappings:
        try:
            variable_mappings = json.loads(campaign.variable_mappings)
        except (json.JSONDecodeError, TypeError):
            pass
    
    for idx, recipient in enumerate(recipients_list, 1):
        try:
            # Skip if already sent
            if SentEmail.objects.filter(campaign=campaign, recipient=recipient).exists():
                continue
            
            # Update progress
            campaign.sending_current_email = recipient.email
            campaign.sending_progress = idx - 1
            campaign.save(update_fields=['sending_current_email', 'sending_progress'])
            
            # Replace variables in seed content before AI rewriting
            seed_content = campaign.seed_email.content_markdown
            if variable_mappings:
                seed_content = replace_variables(seed_content, variable_mappings, recipient)
            
            # Rewrite email with AI for this recipient
            rewritten_markdown = rewrite_with_ollama(
                seed_content,
                recipient_name=recipient.name if recipient.name else None,
                additional_prompt=campaign.ai_prompt if campaign.ai_prompt else None
            )
            
            # Render to HTML
            html_content = render_email_html(rewritten_markdown, campaign.template)
            text_content = strip_tags(html_content)
            
            # Create and send email
            email = EmailMultiAlternatives(
                subject=campaign.subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient.email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            # Save sent email record
            SentEmail.objects.create(
                campaign=campaign,
                recipient=recipient,
                content_markdown=rewritten_markdown,
                content_html=html_content
            )
            
            sent_count += 1
            
            # Update progress after successful send
            campaign.sending_progress = idx
            campaign.save(update_fields=['sending_progress'])
            
        except Exception as e:
            print(f"Error sending email to {recipient.email}: {str(e)}")
            failed_count += 1
            # Still update progress count
            campaign.sending_progress = idx
            campaign.save(update_fields=['sending_progress'])
    
    campaign.status = 'sent'
    campaign.sent_at = timezone.now()
    campaign.sending_current_email = ''
    campaign.save()
    
    return sent_count, failed_count




