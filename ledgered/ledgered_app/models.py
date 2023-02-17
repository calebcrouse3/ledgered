from django.db import models

TRANSACTION_TYPES = [
    ("Credit", "Credit"),
    ("Debit", "Debit")
]

PLUGINS = [
    ("Amazon", "Amazon"),
    ("Mint", "Mint"),
    ("Chase", "Chase"),
    ("Fidelity", "Fidelity")
]


class Account(models.Model):
    name = models.CharField(
        max_length=100,
        choices=PLUGINS,
        default=PLUGINS[0][0]
    )
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


class Category(models.Model):
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'subcategories'

    def __str__(self):
        return f"{self.name}"


class Transaction(models.Model):
    date = models.DateField()
    type = models.CharField(
        max_length=100,
        choices=TRANSACTION_TYPES,
        default=TRANSACTION_TYPES[0][0],
    )
    amount = models.FloatField()
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    original_description = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    # nullable
    pretty_description = models.CharField(max_length=200, null=True, default=None, blank=True)
    # need to give users some way to fill in or re ledger transactions with deleted categories
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, default=None, blank=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, default=None, blank=True)

    def __str__(self):
        return f"{self.original_description}: {self.amount}"


class Description(models.Model):
    """A description rule. Provides a pretty description for
    a transactions and is used to guess the correct category
    and sub_category for a transaction
    """
    is_identity = models.BooleanField()
    description = models.CharField(max_length=200)
    predicate = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.predicate}, {self.description}"


class FileUpload(models.Model):
    account_type = models.CharField(
        max_length=100,
        choices=PLUGINS,
        default=PLUGINS[0][0]
    )
    file = models.FileField()


class SeedRequest(models.Model):
    descriptions_filename = models.CharField(max_length=200)
    categories_filename = models.CharField(max_length=200)
    transactions_filename = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
