from django import forms
from .models import FileUpload, Entry


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ['account_type', 'file']
        labels = {
            'account_type': 'Account Type',
            'file': 'File',
        }


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = [
            'date',
            'entry_type',
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
