from django.db import models
from django.contrib.auth.models import User

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


def get_enum_values(nested_enum):
    """Returns the second value in each struct of an enum like PLUGINS or TRANSACTION_TYPES"""
    return [x[1] for x in nested_enum]


def get_enum_keys(nested_enum):
    """Returns the first value in each struct of an enum like PLUGINS or TRANSACTION_TYPES"""
    return [x[0] for x in nested_enum]


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
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.name}"


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "subcategories"

    def __str__(self):
        return f"{self.name}"


class Transaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
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
        return f"""
            {self.date}
            {self.type}
            {self.account}
            {self.amount}
            {self.original_description}
            {self.pretty_description}
            {self.category}
            {self.subcategory}"""


class Description(models.Model):
    """A description rule. Provides a pretty description for
    a transactions and is used to guess the correct category
    and sub_category for a transaction
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    predicate = models.CharField(max_length=200, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    # TODO could make category and sub category a FK for faster lookup?

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
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    descriptions_filename = models.CharField(max_length=200)
    categories_filename = models.CharField(max_length=200)
    transactions_filename = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)


class UploadSummary(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    account = models.CharField(max_length=200)
    min_date = models.DateField()
    max_date = models.DateField()
    new = models.IntegerField()
    updated = models.IntegerField()
    duplicate = models.IntegerField()
    error = models.IntegerField()
