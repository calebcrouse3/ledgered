"""Defines URL patterns for ledgered_app."""

from django.urls import path

from . import views

app_name = 'ledgered_app'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload, name='upload'),
    path('ledger', views.ledger, name='ledger'),
    path('ledger_queue', views.ledger_queue, name='ledger_queue'),
    path('reports', views.reports, name='reports'),
    path('manage', views.manage, name='manage'),
    path('seed', views.seed, name='seed'),
    path('ajax/load_subcategories/', views.load_subcategories, name='ajax_load_subcategories'),
    path('export', views.export, name='export'),

    # for debugging
    path('list_categories', views.list_categories, name='list_categories'),

    path('list_transactions', views.TransactionListView.as_view(template_name="ledgered_app/list_transactions.html")
         , name='list_transactions'),
    path('list_descriptions', views.DescriptionListView.as_view(template_name="ledgered_app/list_descriptions.html")
         , name='list_descriptions'),
    path('list_accounts', views.AccountListView.as_view(template_name="ledgered_app/list_accounts.html")
         , name='list_accounts'),

    path('delete_all', views.delete_all, name='delete_all')
]

