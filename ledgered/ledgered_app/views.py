from django.shortcuts import render, redirect

from .forms import FileUploadForm

# Create your views here.
def index(request):
    """The index page for setlist tracker."""
    return render(request, 'ledgered_app/index.html')


def handle_uploaded_file(file, account_type=None):
    """Function to process file contents into the data base."""
    assert file


def upload(request):
    """Page to upload transaction files."""

    if request.method == 'POST':
        print("$ HEY this printed")
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            print("$ FORM is valid")
            handle_uploaded_file(request.FILES['file']) # todo also pass in the file type paramters: request.POST['access the form contents?']
            return redirect('ledgered_app:upload_success')
    else:
        form = FileUploadForm()

    context = {'form': form}
    return render(request, 'ledgered_app/upload.html', context)


def upload_success(request):
    """Successful Upload"""
    return render(request, 'ledgered_app/upload_success.html')


def ledger(request):
    """Page to categorize new ledger entries."""
    return render(request, 'ledgered_app/ledger.html')


def reports(request):
    """Page to render ledger reports."""
    return render(request, 'ledgered_app/reports.html')


def manage(request):
    """Page to manage user data."""
    return render(request, 'ledgered_app/manage.html')
