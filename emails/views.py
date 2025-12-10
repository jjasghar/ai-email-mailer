from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
import csv
import io
from .models import SeedEmail, EmailTemplate, Recipient, Campaign, SentEmail
from .services import send_campaign
from .utils import render_email_html, get_available_models, detect_variables
import json


def dashboard(request):
    """Dashboard view."""
    campaigns = Campaign.objects.all()[:5]
    seed_emails = SeedEmail.objects.all()[:5]
    recipients_count = Recipient.objects.count()
    
    context = {
        'campaigns': campaigns,
        'seed_emails': seed_emails,
        'recipients_count': recipients_count,
    }
    return render(request, 'emails/dashboard.html', context)


# Seed Email Views
def seed_email_list(request):
    """List all seed emails."""
    seeds = SeedEmail.objects.all()
    return render(request, 'emails/seed_email_list.html', {'seeds': seeds})


def seed_email_create(request):
    """Create a new seed email."""
    if request.method == 'POST':
        seed = SeedEmail.objects.create(
            title=request.POST.get('title'),
            content_markdown=request.POST.get('content_markdown'),
            description=request.POST.get('description', '')
        )
        messages.success(request, 'Seed email created successfully!')
        return redirect('seed_email_detail', pk=seed.pk)
    return render(request, 'emails/seed_email_form.html')


def seed_email_detail(request, pk):
    """View seed email details."""
    seed = get_object_or_404(SeedEmail, pk=pk)
    return render(request, 'emails/seed_email_detail.html', {'seed': seed})


def seed_email_edit(request, pk):
    """Edit a seed email."""
    seed = get_object_or_404(SeedEmail, pk=pk)
    if request.method == 'POST':
        seed.title = request.POST.get('title')
        seed.content_markdown = request.POST.get('content_markdown')
        seed.description = request.POST.get('description', '')
        seed.save()
        messages.success(request, 'Seed email updated successfully!')
        return redirect('seed_email_detail', pk=seed.pk)
    return render(request, 'emails/seed_email_form.html', {'seed': seed})


def seed_email_delete(request, pk):
    """Delete a seed email."""
    seed = get_object_or_404(SeedEmail, pk=pk)
    if request.method == 'POST':
        seed.delete()
        messages.success(request, 'Seed email deleted successfully!')
        return redirect('seed_email_list')
    return render(request, 'emails/seed_email_delete.html', {'seed': seed})


# Template Views
def template_list(request):
    """List all email templates."""
    templates = EmailTemplate.objects.all()
    return render(request, 'emails/template_list.html', {'templates': templates})


def template_create(request):
    """Create a new email template."""
    if request.method == 'POST':
        template = EmailTemplate.objects.create(
            name=request.POST.get('name'),
            header_html=request.POST.get('header_html', ''),
            footer_html=request.POST.get('footer_html', ''),
            is_default=request.POST.get('is_default') == 'on'
        )
        messages.success(request, 'Template created successfully!')
        return redirect('template_detail', pk=template.pk)
    return render(request, 'emails/template_form.html')


def template_detail(request, pk):
    """View template details."""
    template = get_object_or_404(EmailTemplate, pk=pk)
    return render(request, 'emails/template_detail.html', {'template': template})


def template_edit(request, pk):
    """Edit a template."""
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        template.name = request.POST.get('name')
        template.header_html = request.POST.get('header_html', '')
        template.footer_html = request.POST.get('footer_html', '')
        template.is_default = request.POST.get('is_default') == 'on'
        template.save()
        messages.success(request, 'Template updated successfully!')
        return redirect('template_detail', pk=template.pk)
    return render(request, 'emails/template_form.html', {'template': template})


def template_delete(request, pk):
    """Delete a template."""
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        template.delete()
        messages.success(request, 'Template deleted successfully!')
        return redirect('template_list')
    return render(request, 'emails/template_delete.html', {'template': template})


# Recipient Views
def recipient_list(request):
    """List all recipients."""
    recipients = Recipient.objects.all()
    paginator = Paginator(recipients, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'emails/recipient_list.html', {'page_obj': page_obj})


def recipient_add(request):
    """Add recipients manually or via CSV upload."""
    if request.method == 'POST':
        # Handle CSV upload
        if 'csv_file' in request.FILES and request.FILES['csv_file']:
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file.')
                return redirect('recipient_add')
            
            try:
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.reader(io_string)
                
                added = 0
                skipped = 0
                for row in reader:
                    if len(row) >= 1:
                        email = row[0].strip()
                        name = row[1].strip() if len(row) > 1 else ''
                        company = row[2].strip() if len(row) > 2 else ''
                        phone = row[3].strip() if len(row) > 3 else ''
                        
                        if email and '@' in email:
                            defaults = {}
                            if name:
                                defaults['name'] = name
                            if company:
                                defaults['company'] = company
                            if phone:
                                defaults['phone'] = phone
                            
                            recipient, created = Recipient.objects.get_or_create(
                                email=email,
                                defaults=defaults
                            )
                            if created:
                                added += 1
                            else:
                                skipped += 1
                
                messages.success(request, f'Added {added} recipients. {skipped} already existed.')
            except Exception as e:
                messages.error(request, f'Error processing CSV: {str(e)}')
        
        # Handle manual entry
        if 'emails' in request.POST and request.POST.get('emails'):
            emails_text = request.POST.get('emails', '')
            emails_list = [e.strip() for e in emails_text.split('\n') if e.strip() and '@' in e.strip()]
            
            added = 0
            skipped = 0
            for email in emails_list:
                recipient, created = Recipient.objects.get_or_create(email=email)
                if created:
                    added += 1
                else:
                    skipped += 1
            
            messages.success(request, f'Added {added} recipients. {skipped} already existed.')
        
        return redirect('recipient_list')
    
    return render(request, 'emails/recipient_add.html')


def recipient_edit(request, pk):
    """Edit a recipient."""
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        recipient.email = request.POST.get('email')
        recipient.name = request.POST.get('name', '')
        recipient.company = request.POST.get('company', '')
        recipient.phone = request.POST.get('phone', '')
        recipient.save()
        messages.success(request, 'Recipient updated successfully!')
        return redirect('recipient_list')
    return render(request, 'emails/recipient_form.html', {'recipient': recipient})


def recipient_delete(request, pk):
    """Delete a recipient."""
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        recipient.delete()
        messages.success(request, 'Recipient deleted successfully!')
        return redirect('recipient_list')
    return render(request, 'emails/recipient_delete.html', {'recipient': recipient})


# Campaign Views
def campaign_list(request):
    """List all campaigns."""
    campaigns = Campaign.objects.all()
    return render(request, 'emails/campaign_list.html', {'campaigns': campaigns})


def campaign_create(request):
    """Create a new campaign."""
    if request.method == 'POST':
        # Get variable mappings from form
        variable_mappings = {}
        seed_email_id = request.POST.get('seed_email')
        if seed_email_id:
            seed_email = SeedEmail.objects.get(pk=seed_email_id)
            variables = detect_variables(seed_email.content_markdown)
            for var in variables:
                mapping_value = request.POST.get(f'var_{var}', '')
                # If custom value is selected, use the custom input
                if mapping_value == '__custom__':
                    custom_value = request.POST.get(f'var_{var}_custom', '')
                    if custom_value:
                        variable_mappings[var] = custom_value
                elif mapping_value and mapping_value != '__custom__':
                    variable_mappings[var] = mapping_value
        
        campaign = Campaign.objects.create(
            title=request.POST.get('title'),
            subject=request.POST.get('subject'),
            seed_email_id=seed_email_id,
            template_id=request.POST.get('template') or None,
            ai_prompt=request.POST.get('ai_prompt', ''),
            variable_mappings=json.dumps(variable_mappings) if variable_mappings else ''
        )
        
        # Add recipients
        recipient_ids = request.POST.getlist('recipients')
        campaign.recipients.set(recipient_ids)
        
        messages.success(request, 'Campaign created successfully!')
        return redirect('campaign_detail', pk=campaign.pk)
    
    seeds = SeedEmail.objects.all()
    templates = EmailTemplate.objects.all()
    recipients = Recipient.objects.all()
    
    # Detect variables if seed email is selected
    detected_variables = []
    seed_email_id = request.GET.get('seed_email')
    if seed_email_id:
        try:
            seed_email = SeedEmail.objects.get(pk=seed_email_id)
            detected_variables = detect_variables(seed_email.content_markdown)
        except SeedEmail.DoesNotExist:
            pass
    
    return render(request, 'emails/campaign_form.html', {
        'seeds': seeds,
        'templates': templates,
        'recipients': recipients,
        'detected_variables': detected_variables,
        'selected_seed_id': seed_email_id,
    })


def campaign_detail(request, pk):
    """View campaign details."""
    campaign = get_object_or_404(Campaign, pk=pk)
    sent_emails = SentEmail.objects.filter(campaign=campaign)
    
    # Preview the seed email with template
    html_preview = render_email_html(campaign.seed_email.content_markdown, campaign.template)
    
    # Get Ollama info
    ollama_model = getattr(settings, 'OLLAMA_MODEL', 'granite4:1b')
    available_models = get_available_models()
    
    return render(request, 'emails/campaign_detail.html', {
        'campaign': campaign,
        'sent_emails': sent_emails,
        'html_preview': html_preview,
        'ollama_model': ollama_model,
        'available_models': available_models,
    })


def campaign_copy(request, pk):
    """Copy a campaign with option to select different recipients."""
    original_campaign = get_object_or_404(Campaign, pk=pk)
    
    if request.method == 'POST':
        # Get variable mappings from form
        variable_mappings = {}
        seed_email_id = request.POST.get('seed_email')
        if seed_email_id:
            seed_email = SeedEmail.objects.get(pk=seed_email_id)
            variables = detect_variables(seed_email.content_markdown)
            for var in variables:
                mapping_value = request.POST.get(f'var_{var}', '')
                # If custom value is selected, use the custom input
                if mapping_value == '__custom__':
                    custom_value = request.POST.get(f'var_{var}_custom', '')
                    if custom_value:
                        variable_mappings[var] = custom_value
                elif mapping_value and mapping_value != '__custom__':
                    variable_mappings[var] = mapping_value
        
        # Create new campaign with copied settings
        new_campaign = Campaign.objects.create(
            title=request.POST.get('title'),
            subject=request.POST.get('subject'),
            seed_email_id=seed_email_id,
            template_id=request.POST.get('template') or None,
            ai_prompt=request.POST.get('ai_prompt', ''),
            variable_mappings=json.dumps(variable_mappings) if variable_mappings else ''
        )
        
        # Add recipients (can be different from original)
        recipient_ids = request.POST.getlist('recipients')
        new_campaign.recipients.set(recipient_ids)
        
        messages.success(request, 'Campaign copied successfully!')
        return redirect('campaign_detail', pk=new_campaign.pk)
    
    # Pre-fill form with original campaign data
    seeds = SeedEmail.objects.all()
    templates = EmailTemplate.objects.all()
    recipients = Recipient.objects.all()
    
    # Load variable mappings from original campaign
    variable_mappings = {}
    if original_campaign.variable_mappings:
        try:
            variable_mappings = json.loads(original_campaign.variable_mappings)
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Detect variables
    detected_variables = detect_variables(original_campaign.seed_email.content_markdown)
    
    return render(request, 'emails/campaign_form.html', {
        'seeds': seeds,
        'templates': templates,
        'recipients': recipients,
        'detected_variables': detected_variables,
        'selected_seed_id': str(original_campaign.seed_email.pk),
        'original_campaign': original_campaign,
        'variable_mappings': variable_mappings,
        'variable_mappings_json': json.dumps(variable_mappings),
    })


def campaign_send(request, pk):
    """Send a campaign."""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if request.method == 'POST':
        # Redirect to progress page first, then start sending
        # The progress page will poll for updates while sending happens
        import threading
        from django.db import connections
        
        def send_in_background():
            try:
                # Close any existing database connections for this thread
                connections.close_all()
                
                # Get fresh campaign instance in this thread
                from .models import Campaign
                campaign_obj = Campaign.objects.get(pk=pk)
                send_campaign(campaign_obj)
            except Exception as e:
                print(f"Error in background send: {str(e)}")
                import traceback
                traceback.print_exc()
                # Update campaign status on error
                try:
                    from .models import Campaign
                    campaign_obj = Campaign.objects.get(pk=pk)
                    if campaign_obj.status == 'sending':
                        campaign_obj.status = 'draft'
                        campaign_obj.save()
                except:
                    pass
            finally:
                # Close database connections
                connections.close_all()
        
        # Start sending in background thread
        thread = threading.Thread(target=send_in_background)
        thread.daemon = True
        thread.start()
        
        # Redirect to progress page
        return redirect('campaign_send_progress', pk=pk)
    
    return render(request, 'emails/campaign_send.html', {'campaign': campaign})


def campaign_send_progress(request, pk):
    """Show progress of campaign sending."""
    campaign = get_object_or_404(Campaign, pk=pk)
    return render(request, 'emails/campaign_send_progress.html', {'campaign': campaign})


def campaign_send_progress_api(request, pk):
    """API endpoint to get campaign sending progress."""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    # Calculate percentage
    if campaign.sending_total > 0:
        percentage = int((campaign.sending_progress / campaign.sending_total) * 100)
    else:
        percentage = 0
    
    progress = {
        'status': campaign.status,
        'progress': campaign.sending_progress or 0,
        'total': campaign.sending_total or 0,
        'current_email': campaign.sending_current_email or '',
        'percentage': min(percentage, 100),  # Cap at 100%
        'is_complete': campaign.status == 'sent',
    }
    
    return JsonResponse(progress)
