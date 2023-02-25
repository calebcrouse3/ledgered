from django.contrib import admin

# Register your models here.
from .models import Transaction, Category, Subcategory, Description, SeedRequest, Account, UploadSummary

admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Description)
admin.site.register(SeedRequest)
admin.site.register(Account)
admin.site.register(UploadSummary)
