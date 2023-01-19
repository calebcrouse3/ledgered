from django.contrib import admin

# Register your models here.
from .models import Transaction, Category, Subcategory, Description, Seeded, Account

admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Description)
admin.site.register(Seeded)
admin.site.register(Account)
