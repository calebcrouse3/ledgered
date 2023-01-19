from django import forms
from .models import FileUpload, Transaction, Category, Subcategory, Description, Seeded, Account


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['account_type', 'file']
        labels = {
            'account_type': 'Account Type',
            'file': 'File',
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'date',
            'type',
            'amount',
            'account',
            'original_description',
            'pretty_description',
            'category',
            'subcategory',    
        ]
        labels = {
            'date': 'Date'
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'name',
        ]

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'name',
        ]


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = [
            'category',
            'name',  
        ]
        exclude = ("category",)


class DescriptionForm(forms.ModelForm):
    class Meta:
        model = Description
        fields = [
            'is_identity',
            'description',
            'predicate',
        ]


class SeededForm(forms.ModelForm):
    class Meta:
        model = Seeded
        fields = [
            'seeded',
        ]
