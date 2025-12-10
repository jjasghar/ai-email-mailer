"""
URL configuration for newsletter_mailer project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('emails.urls')),
]
