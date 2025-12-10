from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Seed Emails
    path('seed-emails/', views.seed_email_list, name='seed_email_list'),
    path('seed-emails/create/', views.seed_email_create, name='seed_email_create'),
    path('seed-emails/<int:pk>/', views.seed_email_detail, name='seed_email_detail'),
    path('seed-emails/<int:pk>/edit/', views.seed_email_edit, name='seed_email_edit'),
    path('seed-emails/<int:pk>/delete/', views.seed_email_delete, name='seed_email_delete'),
    
    # Templates
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:pk>/', views.template_detail, name='template_detail'),
    path('templates/<int:pk>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:pk>/delete/', views.template_delete, name='template_delete'),
    
    # Recipients
    path('recipients/', views.recipient_list, name='recipient_list'),
    path('recipients/add/', views.recipient_add, name='recipient_add'),
    path('recipients/<int:pk>/edit/', views.recipient_edit, name='recipient_edit'),
    path('recipients/<int:pk>/delete/', views.recipient_delete, name='recipient_delete'),
    
    # Campaigns
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/create/', views.campaign_create, name='campaign_create'),
    path('campaigns/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/<int:pk>/copy/', views.campaign_copy, name='campaign_copy'),
    path('campaigns/<int:pk>/send/', views.campaign_send, name='campaign_send'),
    path('campaigns/<int:pk>/send/progress/', views.campaign_send_progress, name='campaign_send_progress'),
    path('campaigns/<int:pk>/send/progress/api/', views.campaign_send_progress_api, name='campaign_send_progress_api'),
]




