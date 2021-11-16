from django.shortcuts import render, redirect

from .seeding.populate import CategorySeeder
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
            upload_summary=handle_upload(request.FILES['file'], file_upload.account_type)
            return redirect(
                f'ledgered_app:upload_success', 
                new=upload_summary["new"], 
                updated=upload_summary["updated"], 
                duplicate=upload_summary["duplicate"], 
                error=upload_summary["error"])
    else:
        form = FileUploadForm()

    context = {'form': form}
    return render(request, 'ledgered_app/upload.html', context)


def upload_success(request, new, updated, duplicate, error):
    """Successful Upload"""
    context = {
        "new": new,
        "updated": updated,
        "duplicate": duplicate,
        "error": error
    }
    return render(request, 'ledgered_app/upload_success.html', context=context)


def ledger(request):
    """Page to categorize new ledger entries."""
    return render(request, 'ledgered_app/ledger.html')


def reports(request):
    """Page to render ledger reports."""
    return render(request, 'ledgered_app/reports.html')


def manage(request):
    """Page to manage user data."""
    return render(request, 'ledgered_app/manage.html')


def seeder(request):
    cat_seeder = CategorySeeder()
    cat_seeder.seed()
    return render(request, 'ledgered_app/seeder.html')
