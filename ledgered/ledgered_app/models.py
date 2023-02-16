import os

from django.db import models

TRANSACTION_TYPES = [
    ("C", "Credit"),
    ("D", "Debit")
]

# define plugin types
PLUGINS = [
    ("A", "Amazon"),
    ("M", "Mint"),
    ("C", "Chase"),
    ("F", "Fidelity")
]

SEED_TYPES = [
    ("U", "Uncategorized"),
    ("C", "Categorized"),
]

class Account(models.Model):
    """A transaction category"""
    name = models.CharField(
        max_length=2,
        choices=PLUGINS,
        default="C"
    )
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Accounts'

    def __str__(self):
        """Return a simple string representing the account."""
        return f"{self.name}..."


class Category(models.Model):
    """A transaction category"""
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        """Return a simple string representing the transaction."""
        return f"{self.name}..."


class Subcategory(models.Model):
    """A transaction subcategory"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'subcategories'

    def __str__(self):
        """Return a simple string representing the transaction."""
        return f"{self.name}..."


class Transaction(models.Model):
    """A transaction in your ledger"""
    date = models.DateField()
    type = models.CharField(
        max_length=2,
        choices=TRANSACTION_TYPES,
        default="D",
    )
    amount = models.FloatField()
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    original_description = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    # nullable
    pretty_description = models.CharField(max_length=200, null=True, default=None, blank=True)
    # if category is deleted this value will then be null. Will want to give the user some way to reassign categories
    # blank indicates that when validating a form this must be filled but it can be blank at the data base level
    # TODO should category be blank=false?
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, default=None, blank=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, default=None, blank=True)

    def __str__(self):
        """Return a simple string representing the transaction."""
        return f"{self.original_description}: {self.amount}..."


class Description(models.Model):
    """A description rule. Used to guess the correct category and sub_category for a transaction"""
    # a boolean indicating if the description rule is an identify rule
    is_identity = models.BooleanField()
    description = models.CharField(max_length=200)
    predicate = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a simple string representing the transaction."""
        return f"{self.predicate}, {self.description}..."


class FileUpload(models.Model):
    account_type = models.CharField(
        max_length=2,
        choices=PLUGINS,
        default="C",
    )
    file = models.FileField()


class SeedRequest(models.Model):
    """Simple boolean to indicate is a user has had their account seeded yet"""
    descriptions_filename = models.CharField(max_length=200)
    categories_filename = models.CharField(max_length=200)
    transactions_filename = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
