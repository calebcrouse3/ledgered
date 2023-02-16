from django import forms
from .models import FileUpload, Transaction, Category, Subcategory, Description, SeedRequest, Account


class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = '__all__'


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # read only keeps us from editing these fields in the form. Doesn't seem to work with dropdowns.
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


class SeedRequestForm(forms.ModelForm):
    class Meta:
        model = SeedRequest
        fields = '__all__'
