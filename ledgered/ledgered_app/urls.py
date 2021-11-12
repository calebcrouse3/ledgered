"""Defines URL patterns for ledgered_app."""

from django.urls import path

from . import views

app_name = 'ledgered_app'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload, name='upload'),
    path('ledger', views.ledger, name='ledger'),
    path('reports', views.reports, name='reports'),
    path('manage', views.manage, name='manage'),
    path('upload_success', views.upload_success, name='upload_success'),
]