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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # todo this isnt working to overcome value set error
        self.fields['subcategory'].queryset = Subcategory.objects.none()

        if 'category' in self.data:
            try:
                print("trying to set subcategories")
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Subcategory.objects.filter(category_id=category_id).order_by('name')
                print(self.fields['subcategory'].queryset)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk: # todo error here
            self.fields['subcategory'].queryset = self.instance.category.subcategories_set.order_by('name')


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
