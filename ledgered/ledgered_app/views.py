from django.shortcuts import render

# Create your views here.
def index(request):
    """The index page for setlist tracker."""
    return render(request, 'ledgered_app/index.html')


def upload(request):
    """Page to upload transaction files."""
    return render(request, 'ledgered_app/upload.html')


def ledger(request):
    """Page to categorize new ledger entries."""
    return render(request, 'ledgered_app/ledger.html')


def reports(request):
    """Page to render ledger reports."""
    return render(request, 'ledgered_app/reports.html')


def manage(request):
    """Page to manage user data."""
    return render(request, 'ledgered_app/manage.html')