"""Defines URL patterns for ledgered_app."""

from django.urls import path

from . import views

app_name = 'ledgered_app'
urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload, name='upload'),
    path('ledger', views.ledger, name='ledger'),
    path('categorize_next_transaction', views.categorize_next_transaction, name='categorize_next_transaction'),
    path('reports', views.reports, name='reports'),
    path('manage', views.manage, name='manage'),
    path('upload_success/<int:new>/<int:updated>/<int:duplicate>/<int:error>/', views.upload_success, name='upload_success'),
    path('seeder', views.seeder, name='seeder'),
    path('ajax/load_subcategories/', views.load_subcategories, name='ajax_load_subcategories'),
    path('invalid_transaction_form', views.categorize_next_transaction, name='invalid_transaction_form'),

    # for debugging
    path('transaction_list', views.TransactionListView.as_view(), name='transaction_list'),
    path('description_list', views.DescriptionListView.as_view(), name='description_list'),
    path('delete_all', views.delete_all, name='delete_all'),
    path('categories_list', views.list_categories, name='categories_list')
]

