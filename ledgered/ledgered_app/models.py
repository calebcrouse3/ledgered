from django.db import models


TRANSACTION_TYPES = [
    ("C", "Credit"),
    ("D", "Debit")
]


class Transaction(models.Model):
    """A transaction in your ledger"""
    date = models.DateField()
    type = models.CharField(
        max_length=2,
        choices=TRANSACTION_TYPES,
        default="D",
    )
    amount = models.FloatField()
    account = models.CharField(max_length=200)
    original_description = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    # nullable
    pretty_description = models.CharField(max_length=200, blank=True, null=True)
    category = models.CharField(max_length=200, blank=True, null=True)
    subcategory = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        """Return a simple string representing the transaction."""
        return f"{self.original_description}: {self.amount}..."


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


# define plugin types
PLUGINS = [
    ("A", "Amazon"),
    ("M", "Mint"),
    ("C", "Chase"),
    ("F", "Fidelity")
]


class FileUpload(models.Model):
    account_type = models.CharField(
        max_length=2,
        choices=PLUGINS,
        default="F",
    )
    file = models.FileField()


class Seeded(models.Model):
    """Simple boolean to indicate is a user has had their account seeded yet"""
    seeded = models.BooleanField()
    date_added = models.DateTimeField(auto_now_add=True)
