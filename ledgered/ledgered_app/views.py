from django.shortcuts import render, redirect

from .seeder.seed import CategorySeeder, DescriptionSeeder, TransactionSeeder, AccountSeeder
from .upload_handler import handle_upload
from .forms import FileUploadForm, SeededForm, TransactionForm
from .models import Category, Description, Transaction, Seeded, Subcategory, Account
from django.views.generic import ListView, CreateView, UpdateView


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


def load_subcategories(request):
    category_id = request.GET.get('category')
    subcategories = Subcategory.objects.filter(category_id=category_id).order_by('name')
    return render(request, 'ledgered_app/subcategory_dropdown_list_options.html', {'subcategories': subcategories})


def get_cat_data():
    t = Transaction.objects.filter(category=None)
    data = {"num": len(t), "next": None}
    if data["num"] > 0:
        data["next"] = t[0]
    return data


def get_pretty_description(original_description):
    # first check for predicate rules
    # TODO i forget why you might want a predicate rule or how they work so skip for now
    # then check for identity rules
    # this is gonna be inefficient because it has to load all the rules each time
    # todo need to go back to a little more smart rule adding but for now its just going to return
    # the first rule description that matches any predicate
    # something about using the rule that matches to the longest predicate?
    for rule in Description.objects.all():
        if rule.predicate.lower() in original_description.lower():
            return rule.description
    return None


def categorize_next_transaction(request):
    """Edit the category and subcategory of a transaction."""
    cat_data = get_cat_data()
    t = cat_data["next"]

    # if no remaining transactions go back to ledger landing page
    if cat_data["num"] == 0:
        return redirect('ledgered_app:ledger')

    if request.method != 'POST':
        t.pretty_description = get_pretty_description(t.original_description)
        form = TransactionForm(instance=t)
    else:
        print(request.POST)
        form = TransactionForm(instance=t, data=request.POST)
        print("form created")
        print(form.data)
        if form.is_valid():
            print("form is valid")
            form.save()
            return redirect('ledgered_app:categorize_next_transaction')
        else:
            print("form was invalid")
            print(form.errors)
            return render(request, 'ledgered_app/invalid_transaction_form.html', {'error': form.errors})

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


def list_categories(request):
    """Print all categories in data base"""

    # dict where key is cat name and value is list of subcats 
    cats_subcats = {}

    categories = Category.objects.order_by('name')
    for cat in categories:
        # get subcategories for each category
        subcategories = Category.objects.get(id=cat.id).subcategory_set.order_by('name')
        cats_subcats[cat.name] = [subcat.name for subcat in subcategories]

    context = {'cats_subcats': cats_subcats}

    return render(request, 'ledgered_app/list_categories.html', context)


def delete_all(request):
    """Page to manage user data."""
    Transaction.objects.all().delete()
    Category.objects.all().delete()
    Subcategory.objects.all().delete()
    Description.objects.all().delete()
    Seeded.objects.all().delete()
    Account.objects.all().delete()
    return render(request, 'ledgered_app/delete_all.html')


class TransactionListView(ListView):
    model = Transaction


class DescriptionListView(ListView):
    model = Description
