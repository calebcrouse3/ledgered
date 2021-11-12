from django import forms


# define plugin types
AMAZON = "A"
MINT = "M"

PLUGINS = [
    (AMAZON, "Amazon"),
    (MINT, "Mint"),
]

class FileUpload():
    """An external file upload"""
    account_type = forms.CharField(
        max_length=2,
        choices=PLUGINS,
        default=MINT,
    )
    file = forms.FileField()
