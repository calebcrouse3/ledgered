from django.shortcuts import render, redirect

from .seeder.seed import CategorySeeder, DescriptionSeeder, TransactionSeeder, AccountSeeder, DescriptionForm
from .upload_handler import handle_upload
from .forms import FileUploadForm, TransactionForm, SeedRequestForm
from .models import Category, Description, Transaction, SeedRequest, Subcategory, Account
from .config import RESOURCE_PATH
from django.views.generic import ListView
from bokeh.plotting import figure
from bokeh.embed import components
import os


def index(request):
    return render(request, 'ledgered_app/index.html')


def upload(request):
    """Page to upload transaction files."""

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_upload = form.save(commit=False)
            summary = handle_upload(request.FILES['file'], file_upload.account_type)
            return render(request, 'ledgered_app/upload_summary.html', context={"summary": summary})
    else:
        form = FileUploadForm()

    context = {'form': form}
    return render(request, 'ledgered_app/upload.html', context)


def ledger(request):
    """Entry point for categorizing new transactions."""
    context = {"num_uncategorized": get_num_uncategorized_transactions()}
    return render(request, 'ledgered_app/ledger.html', context)


def load_subcategories(request):
    category_id = request.GET.get('category')
    subcategories = Subcategory.objects.filter(category_id=category_id).order_by('name')
    return render(request, 'ledgered_app/subcategory_options.html', {'subcategories': subcategories})


def get_num_uncategorized_transactions():
    return Transaction.objects.filter(category=None).count()


def get_next_uncategorized_transaction():
    # returns none if transaction doesnt exist
    return Transaction.objects.filter(category=None).first()


def get_pretty_description(original_description):
    """Uses description rules to find a matching pretty description for this original description
    First looks through all the predicate rules and returns one of those if there's a match.
    Then look for any matching description rules without a predicate and return the match with the longest
    length.
    """
    for predicate_rule in Description.objects.filter(predicate__isnull=False):
        if predicate_rule.predicate.lower() in original_description.lower():
            return predicate_rule.description

    for rule in Description.objects.filter(predicate__isnull=True):
        if rule.description.lower() in original_description.lower():
            return rule.description

    return None


def get_prev_transaction(pretty_description):
    """Use the categories and subcategories of previous transactions to lookup category and subcategory
    TODO could check if theres multiple different cats and subcats and maybe you want to do something different
    """
    return Transaction.objects.filter(pretty_description=pretty_description, category__isnull=False).first()


def categorize_next_transaction(request):
    """Edit the category and subcategory of a transaction."""
    num_uncategorized = get_num_uncategorized_transactions()

    # if no remaining transactions go back to ledger landing page
    if num_uncategorized == 0:
        return redirect('ledgered_app:ledger')

    next_trxn = get_next_uncategorized_transaction()

    if request.method != 'POST':
        pretty_dscr = get_pretty_description(next_trxn.original_description)

        if pretty_dscr:
            next_trxn.pretty_description = pretty_dscr

            # use pretty description to lookup subcategory
            prev_trxn = get_prev_transaction(pretty_dscr)
            if prev_trxn:
                next_trxn.category = prev_trxn.category
                next_trxn.subcategory = prev_trxn.subcategory

        trxn_form = TransactionForm(instance=next_trxn)

        # if there's no description rule for this transaction,
        # give them a head start by putting the original string in the description box
        if not next_trxn.pretty_description:
            dscr_form = DescriptionForm({"description": next_trxn.original_description.title()})
        else:
            dscr_form = DescriptionForm()

    else:
        if 'submit_transaction' in request.POST:
            trxn_form = TransactionForm(instance=next_trxn, data=request.POST)
            if trxn_form.is_valid():
                trxn_form.save()
                return redirect('ledgered_app:categorize_next_transaction')
            else:
                print("Form Errors:\n", trxn_form.errors)
                return render(request, 'ledgered_app/invalid_transaction_form.html', {'error': trxn_form.errors})

        elif 'submit_description' in request.POST:
            dscr_form = DescriptionForm(data=request.POST)
            if dscr_form.is_valid():
                dscr_form.save()
                return redirect('ledgered_app:categorize_next_transaction')

    context = {
        'trxn_form': trxn_form,
        'dscr_form': dscr_form,
        "num_uncategorized": num_uncategorized
    }

    return render(request, 'ledgered_app/categorize_next_transaction.html', context)


def manage(request):
    """Page to manage user data."""
    return render(request, 'ledgered_app/manage.html')


def seeder(request):
    # posting a seed request for the first time
    if request.method == 'POST':
        form = SeedRequestForm(request.POST)
        if form.is_valid():
            seed_database(
                form['descriptions_filename'].data,
                form['categories_filename'].data,
                form['transactions_filename'].data
            )
            seeded_obj = form.save(commit=False)
            seeded_obj.save()
            return redirect('ledgered_app:seeder')
    else:
        def filename_options(folder):
            return [(f, f) for f in os.listdir(RESOURCE_PATH + folder) + ["none"]]

        seeds = SeedRequest.objects.all()
        form = SeedRequestForm()
        context = {
            "form": form,
            "descriptions": filename_options("descriptions"),
            "categories": filename_options("categories"),
            "transactions": filename_options("transactions"),
            "num_seeds": seeds.count(),
            "seeds": seeds
        }
        return render(request, 'ledgered_app/seed_request.html', context)


def seed_database(description_filename, category_filename, transaction_filename):
    account_seeder = AccountSeeder()
    cat_seeder = CategorySeeder(category_filename)
    descr_seeder = DescriptionSeeder(description_filename)
    entries_seeder = TransactionSeeder(transaction_filename)
    account_seeder.seed()
    cat_seeder.seed()
    descr_seeder.seed()
    entries_seeder.seed()


def list_categories(request):
    """Print all categories in data base"""
    cats_subcats = {}
    categories = Category.objects.order_by('name')
    for cat in categories:
        # get subcategories for each category
        subcategories = Category.objects.get(id=cat.id).subcategory_set.order_by('name')
        cats_subcats[cat.name] = [subcat.name for subcat in subcategories]

    context = {'cats_subcats': cats_subcats}

    return render(request, 'ledgered_app/list_categories.html', context)


def reports(request):
    """This is just a toy function. Replace with real plot later"""

    # Create a Bokeh figure
    p = figure()
    p.circle([1, 2, 3, 4, 5], [2, 5, 8, 2, 7])

    # Generate the HTML and JavaScript code for the Bokeh visualization
    script, div = components(p)

    # Render the template with the Bokeh visualization embedded
    return render(request, 'ledgered_app/reports.html', context={'script': script, 'div': div})


def delete_all(request):
    for model in [Transaction, Category, Subcategory, Description, SeedRequest, Account]:
        model.objects.all().delete()

    return render(request, 'ledgered_app/delete_all.html')


class TransactionListView(ListView):
    model = Transaction


class DescriptionListView(ListView):
    model = Description


class AccountListView(ListView):
    model = Account
