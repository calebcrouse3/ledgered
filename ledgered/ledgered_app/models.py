from django.db import models

class Entry(models.Model):
    """An entry in your ledger"""
    date = models.DateField()
    entry_type = models.CharField(max_length=200)
    amount = models.FloatField()
    account = models.CharField(max_length=200)
    original_description = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    # nullable
    pretty_description = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=200, blank=True, null=True)
    subcategory = models.CharField(max_length=200, blank=True, null=True)


class Category(models.Model):
    """An entry category"""
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)


class Subcategory(models.Model):
    """An entry subcategory"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)


class Description(models.Model):
    """A discreption rule"""
    # a boolean indicating if the description rule is an identify rule
    is_identity = models.BooleanField()
    description = models.CharField(max_length=200)
    predicate = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)


# define plugin types
PLUGINS = [
    ("A", "Amazon"),
    ("M", "Mint"),
]

class FileUpload(models.Model):
    account_type = models.CharField(
        max_length=2,
        choices=PLUGINS,
        default="M",
    )
    file = models.FileField()
