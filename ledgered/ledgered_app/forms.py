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

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['owner'].widget = forms.HiddenInput()

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


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = '__all__'


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['owner'].widget = forms.HiddenInput()

    class Meta:
        model = Category
        fields = '__all__'


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = '__all__'


class DescriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DescriptionForm, self).__init__(*args, **kwargs)
        self.fields['owner'].widget = forms.HiddenInput()

    class Meta:
        model = Description
        fields = '__all__'


class SeedRequestForm(forms.ModelForm):
    class Meta:
        model = SeedRequest
        fields = '__all__'
