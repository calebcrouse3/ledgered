from django.shortcuts import render, redirect
from .upload_handler import handle_upload
from .forms import FileUploadForm


# Create your views here.
def index(request):
    """The index page for setlist tracker."""
    return render(request, 'ledgered_app/index.html')


def upload(request):
    """Page to upload transaction files."""

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_upload = form.save(commit=False)
            new_entry_num=handle_upload(request.FILES['file'], file_upload.account_type)
            return redirect(f'upload_success/{str(new_entry_num)}')
    else:
        form = FileUploadForm()

    context = {'form': form}
    return render(request, 'ledgered_app/upload.html', context)


def upload_success(request, new_entry_num):
    """Successful Upload"""
    return render(request, 'ledgered_app/upload_success.html', context={"new_entry_num": new_entry_num})


def ledger(request):
    """Page to categorize new ledger entries."""
    return render(request, 'ledgered_app/ledger.html')


def reports(request):
    """Page to render ledger reports."""
    return render(request, 'ledgered_app/reports.html')


def manage(request):
    """Page to manage user data."""
    return render(request, 'ledgered_app/manage.html')
