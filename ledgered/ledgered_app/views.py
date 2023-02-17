from django.shortcuts import render, redirect

from .seeder.seed import CategorySeeder, DescriptionSeeder, TransactionSeeder, AccountSeeder, DescriptionForm
from .upload_handler import handle_upload
from .forms import FileUploadForm, TransactionForm, SeedRequestForm
from .models import Category, Description, Transaction, SeedRequest, Subcategory, Account
from django.views.generic import ListView, CreateView, UpdateView
from bokeh.plotting import figure, show
from bokeh.embed import components
import os
from time import sleep


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
            upload_summary = handle_upload(request.FILES['file'], file_upload.account_type)
            return redirect(
                f'ledgered_app:upload_success', 
                new=upload_summary["new"], 
                updated=upload_summary["updated"], 
                ignored=upload_summary["ignored"],
                form_error=upload_summary["form_error"],
                other_error=upload_summary["other_error"])
    else:
        form = FileUploadForm()

    context = {'form': form}
    return render(request, 'ledgered_app/upload.html', context)


def upload_success(request, new, updated, ignored, form_error, other_error):
    """Successful Upload"""
    context = {
        "new": new,
        "updated": updated,
        "ignored": ignored,
        "form_error": form_error,
        "other_error": other_error
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
        t_form = TransactionForm(instance=t)
        # if there's no description rule for this transaction,
        # give them a head start by putting the original string in the description box
        if not t.pretty_description:
            d_form = DescriptionForm({"description": t.original_description.title()})
        else:
            d_form = DescriptionForm()
    else:
        if 'submit_transaction' in request.POST:
            t_form = TransactionForm(instance=t, data=request.POST)
            if t_form.is_valid():
                print("form is valid")
                t_form.save()
                return redirect('ledgered_app:categorize_next_transaction')
            else:
                print("form was invalid")
                print(t_form.errors)
                return render(request, 'ledgered_app/invalid_transaction_form.html', {'error': t_form.errors})

        elif 'submit_description' in request.POST:
            d_form = DescriptionForm(data=request.POST)
            if d_form.is_valid():
                d_form.save()
                return redirect('ledgered_app:categorize_next_transaction')
        else:
            print("neither form was found")

    context = {'transaction': t, 't_form': t_form, 'd_form': d_form, "num_uncategorized": cat_data["num"]}
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
        form = SeedRequestForm()
        form_options = {
            "form": form,
            "descriptions": [(f, f) for f in os.listdir(os.getcwd()+"/ledgered_app/resources/descriptions") + ["none"]],
            "categories": [(f, f) for f in os.listdir(os.getcwd()+"/ledgered_app/resources/categories") + ["none"]],
            "transactions": [(f, f) for f in os.listdir(os.getcwd()+"/ledgered_app/resources/transactions") + ["none"]]
        }
        seed_status = get_seed_status()
        context = {**seed_status, **form_options}
        print(context)
        return render(request, 'ledgered_app/seed_request.html', context)


def get_seed_status():
    seeds = SeedRequest.objects.all()
    num_seeds = len(seeds)
    if num_seeds > 0:
        return {
            "status_descriptions": ', '.join([x.descriptions_filename for x in seeds if x.descriptions_filename != "none"]),
            "status_categories": ', '.join([x.categories_filename for x in seeds if x.categories_filename != "none"]),
            "status_transactions": ', '.join([x.transactions_filename for x in seeds if x.transactions_filename != "none"]),
            "status_num_seeds": num_seeds
        }
    else:
        # if no seeds yet just give empty strings
        return {
            "status_descriptions": "",
            "status_categories": "",
            "status_transactions": "",
            "status_num_seeds": num_seeds
        }


def seed_database(description_filename, category_filename, transaction_filename):
    account_seeder = AccountSeeder()
    account_seeder.seed()

    cat_seeder = CategorySeeder(category_filename)
    cat_seeder.seed()

    descr_seeder = DescriptionSeeder(description_filename)
    descr_seeder.seed()

    entries_seeder = TransactionSeeder(transaction_filename)
    entries_seeder.seed()


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


def reports(request):
    # Create a Bokeh figure
    p = figure()
    p.circle([1, 2, 3, 4, 5], [2, 5, 8, 2, 7])

    # Generate the HTML and JavaScript code for the Bokeh visualization
    script, div = components(p)

    # Render the template with the Bokeh visualization embedded
    return render(request, 'ledgered_app/reports.html', context={'script': script, 'div': div})


def delete_all(request):
    """Page to manage user data."""
    Transaction.objects.all().delete()
    Category.objects.all().delete()
    Subcategory.objects.all().delete()
    Description.objects.all().delete()
    SeedRequest.objects.all().delete()
    Account.objects.all().delete()
    return render(request, 'ledgered_app/delete_all.html')


class TransactionListView(ListView):
    model = Transaction


class DescriptionListView(ListView):
    model = Description


class AccountListView(ListView):
    model = Account
