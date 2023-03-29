from django.shortcuts import render, redirect

from .seeder.seeders import *
from .utils.handle_upload import handle_upload
from .forms import FileUploadForm, TransactionForm, SeedRequestForm, DescriptionForm, LedgerTransactionForm
from .models import *
from .utils.form_utils import save_form
from .configs.config import RESOURCE_PATH
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from bokeh.plotting import figure
from bokeh.embed import components
import os


def index(request):
    return render(request, 'ledgered_app/index.html')


@login_required
def ledger(request):
    """Entry point for categorizing new transactions."""
    context = {"num_uncategorized": get_queue_size(request.user)}
    return render(request, 'ledgered_app/ledger.html', context)


def get_queue_size(user):
    return Transaction.objects.filter(category=None, owner=user).count()


def get_pretty_description(original_description, user):
    """Uses description rules to find a matching pretty description for this original description
    First looks through all the predicate rules and returns one of those if there's a match.
    Then look for any matching description rules without a predicate and return the match with the longest
    length.
    """
    for predicate_rule in Description.objects.filter(predicate__isnull=False, owner=user):
        if predicate_rule.predicate.lower() in original_description.lower():
            return predicate_rule.description

    for rule in Description.objects.filter(predicate__isnull=True, owner=user):
        if rule.description.lower() in original_description.lower():
            return rule.description

    return None


@login_required
def ledger_queue(request):
    """Edit the category and subcategory of a transaction."""
    num_uncategorized = get_queue_size(request.user)

    # if no remaining transactions go back to ledger landing page
    if num_uncategorized == 0:
        return redirect('ledgered_app:ledger')

    # get the next transaction in the ledger queue
    next_trxn = Transaction.objects.filter(category=None, owner=request.user).first()

    # return transaction and description form for user input
    if request.method != 'POST':
        context = {"num_uncategorized": num_uncategorized}

        pretty_dscr = get_pretty_description(next_trxn.original_description, request.user)

        if pretty_dscr:
            next_trxn.pretty_description = pretty_dscr
            # use pretty description to lookup subcategory
            # could expand this to be smarter later
            prev_trxn = Transaction.objects.filter(
                owner=request.user,
                pretty_description=pretty_dscr,
                category__isnull=False
            ).first()

            if prev_trxn:
                next_trxn.category = prev_trxn.category

            context['dscr_form'] = DescriptionForm()

        # if there's no pretty description and this, description rule, for this transaction,
        # give them a head start by putting the original string in the description form box
        else:
            context['dscr_form'] = DescriptionForm({"description": next_trxn.original_description.title()})

        # here need to limit the categories to only this user
        trxn_form = LedgerTransactionForm(instance=next_trxn, user=request.user)
        context['trxn_form'] = trxn_form

        return render(request, 'ledgered_app/ledger_queue.html', context)

    # save the submitted transaction and redirect to the ledger queue
    else:
        # id from the form defined in the template
        if 'submit_transaction' in request.POST:
            trxn_form = TransactionForm(instance=next_trxn, data=request.POST)
            save_form(trxn_form, request.user)
            return redirect('ledgered_app:ledger_queue')

        # id from the form defined in the template
        elif 'submit_description' in request.POST:
            dscr_form = DescriptionForm(data=request.POST)
            save_form(dscr_form, request.user)
            return redirect('ledgered_app:ledger_queue')


@login_required
def manage(request):
    """Page to manage user data."""
    return render(request, 'ledgered_app/manage.html')


@login_required
def seed(request):
    # posting a seed request for the first time
    if request.method == 'POST':
        form = SeedRequestForm(request.POST)
        save_form(form, request.user)

        # TODO accounts per owner. This is ugly. Only add accounts of first request
        if SeedRequest.objects.all().count() == 1:
            seed_accounts()

        seed_categories(form['categories_filename'].data, request.user)
        seed_descriptions(form['descriptions_filename'].data, request.user)
        seed_transactions(form['transactions_filename'].data, request.user)
        return redirect('ledgered_app:seed')
    else:
        # populate the form with the filenames from the correct resource's folder + "none"
        def filename_options(folder):
            return [(f, f) for f in os.listdir(RESOURCE_PATH + folder) + ["none"]]

        seeds = SeedRequest.objects.filter(owner=request.user)
        form = SeedRequestForm()
        context = {
            "form": form,
            "descriptions": filename_options("descriptions"),
            "categories": filename_options("categories"),
            "transactions": filename_options("transactions"),
            "seeds": seeds
        }
        return render(request, 'ledgered_app/seed.html', context)


@login_required
def upload(request):
    """Page to upload transaction files."""

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_upload = form.save(commit=False)
            handle_upload(request.FILES['file'], file_upload.account_type, request.user)
            return redirect('ledgered_app:upload')
    else:
        uploads = UploadSummary.objects.filter(owner=request.user)
        form = FileUploadForm()
        context = {
            "form": form,
            "uploads": uploads
        }

        return render(request, 'ledgered_app/upload.html', context)


@login_required
def reports(request):
    """This is just a toy function. Replace with real plot later"""

    # Create a Bokeh figure
    p = figure()
    p.circle([1, 2, 3, 4, 5], [2, 5, 8, 2, 7])

    # Generate the HTML and JavaScript code for the Bokeh visualization
    script, div = components(p)

    # Render the template with the Bokeh visualization embedded
    return render(request, 'ledgered_app/reports.html', context={'script': script, 'div': div})


@login_required
def delete_all(request):
    # TODO give options to only delete for this user
    for model in [Transaction, Category, Description, SeedRequest, Account, UploadSummary]:
        model.objects.all().delete()

    return render(request, 'ledgered_app/delete_all.html')


def export(request):
    columns = [
        "date",
        "type",
        "amount",
        "account",
        "original_description",
        "pretty_description",
        "category"
    ]
    transactions = Transaction.objects.all()
    data = download_csv(request, transactions, columns)
    response = HttpResponse(data, content_type='text/csv')
    return response


class TransactionListView(ListView):
    model = Transaction

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        return queryset


class DescriptionListView(ListView):
    model = Description

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        return queryset
    

class CategoriesListView(ListView):
    model = Category

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(owner=self.request.user)
        return queryset


class AccountListView(ListView):
    model = Account


""" @login_required
def list_categories(request):
    # Print all categories in data base
    categories = Category.objects.filter(owner=request.user).order_by('name')
    context = {'categories': categories}
    return render(request, 'ledgered_app/list_categories.html', context)
 """