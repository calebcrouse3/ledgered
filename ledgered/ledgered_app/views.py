from django.shortcuts import render, redirect

from .seeder.seed import CategorySeeder, DescriptionSeeder, TransactionSeeder, AccountSeeder
from .upload_handler import handle_upload
from .forms import FileUploadForm, SeededForm, TransactionForm
from .models import Category, Description, Transaction, Seeded, Subcategory, Account


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
    """Entry point for categorizing new transactions."""
    cat_data = get_cat_data()
    context = {
        "num_uncategorized": cat_data["num"],
    }
    return render(request, 'ledgered_app/ledger.html', context)


def get_cat_data():
    t = Transaction.objects.filter(category=None)
    data = {"num": len(t), "next": None}
    if data["num"] > 0:
        data["next"] = t[0]
    return data


def categorize_next_transaction(request):
    """Edit the category and subcategory of a transaction."""
    cat_data = get_cat_data()
    t = cat_data["next"]

    # if no remaining transactions go back to ledger landing page
    if cat_data["num"] == 0:
        return redirect('ledgered_app:ledger')

    if request.method != 'POST':
        # TODO make the only visible subcategories those that are a foreign key of the category
        form = TransactionForm(instance=t)
    else:
        form = TransactionForm(instance=t, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('ledgered_app:categorize_next_transaction')

    context = {'transaction': t, 'form': form, "num_uncategorized": cat_data["num"]}
    return render(request, 'ledgered_app/categorize_next_transaction.html', context)


def reports(request):
    """Page to render ledger reports."""
    return render(request, 'ledgered_app/reports.html')


def manage(request):
    """Page to manage user data."""
    return render(request, 'ledgered_app/manage.html')


def seeder(request):
    """If not already called, this URL will populate the data base with category, entry, and description data"""
    seeded = len(Seeded.objects.all()) > 0

    if not seeded:
        account_seeder = AccountSeeder()
        account_seeder.seed()

        cat_seeder = CategorySeeder()
        cat_seeder.seed()

        descr_seeder = DescriptionSeeder()
        descr_seeder.seed()

        entries_seeder = TransactionSeeder()
        entries_seeder.seed()

        seeded_form = SeededForm({"seeded": True})
        if seeded_form.is_valid():
            seeded_obj = seeded_form.save(commit=False)
            seeded_obj.save()

    context = {"seeded": seeded}

    return render(request, 'ledgered_app/seeder.html', context)


def print_categories(request):
    """Print all categories in data base"""

    # dict where key is cat name and value is list of subcats 
    cats_subcats = {}

    categories = Category.objects.order_by('name')
    for cat in categories:
        # get subcategories for each category
        subcategories = Category.objects.get(id=cat.id).subcategory_set.order_by('name')
        cats_subcats[cat.name] = [subcat.name for subcat in subcategories]

    context = {'cats_subcats': cats_subcats}

    return render(request, 'ledgered_app/print_categories.html', context)


def print_descriptions(request):
    """Print all categories in data base"""
    descriptions = Description.objects.order_by('is_identity')
    context = {'descriptions': descriptions}
    return render(request, 'ledgered_app/print_descriptions.html', context)


def print_transactions(request):
    """Print all categories in data base"""
    transactions = Transaction.objects.order_by('date_added')
    context = {'transactions': transactions}
    return render(request, 'ledgered_app/print_transactions.html', context)


def delete_all(request):
    """Page to manage user data."""
    Transaction.objects.all().delete()
    Category.objects.all().delete()
    Subcategory.objects.all().delete()
    Description.objects.all().delete()
    Seeded.objects.all().delete()
    Account.objects.all().delete()
    return render(request, 'ledgered_app/delete_all.html')
