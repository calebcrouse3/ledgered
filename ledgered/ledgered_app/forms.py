from django import forms
from .models import *


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = '__all__'


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'
        exclude = ('owner',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # read only keeps us from editing these fields in the form.
        # Doesn't seem to work with dropdowns.
        readonly_fields = [
            'date',
            'amount',
            'original_description',
            'pretty_description',
            'type',
            'account'
        ]

        # set the attributes on the form field widget for certain fields
        for field_name, field in self.fields.items():
            if field_name in readonly_fields:
                field.widget.attrs['readonly'] = True


class LedgerTransactionForm(TransactionForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(owner=user)


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = '__all__'


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        exclude = ('owner',)


class DescriptionForm(forms.ModelForm):
    class Meta:
        model = Description
        fields = '__all__'
        exclude = ('owner',)


class SeedRequestForm(forms.ModelForm):
    class Meta:
        model = SeedRequest
        fields = '__all__'
        exclude = ('owner',)


class UploadSummaryForm(forms.ModelForm):
    class Meta:
        model = UploadSummary
        fields = '__all__'
        exclude = ('owner',)
