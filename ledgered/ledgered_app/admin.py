from django.contrib import admin

# Register your models here.
from .models import Entry, Category, Subcategory, Description, Seeded

admin.site.register(Entry)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Description)
admin.site.register(Seeded)