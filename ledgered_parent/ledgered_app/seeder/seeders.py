"""Populates the database with default categories and description rules
Could be used to give starting point for new users or for a test account
Could be used to faciliate a description and category reset
"""

import logging.config
import os
from ..forms import CategoryForm, DescriptionForm, TransactionForm, AccountForm
from ..models import PLUGINS, Account, Category, get_enum_values
from ..configs.config import LOGGER_CONFIG_PATH, RESOURCE_PATH
from ..utils.file_utils import *
from ..utils.form_utils import save_form


logging.config.fileConfig(LOGGER_CONFIG_PATH)
logger = logging.getLogger('root')


def seed_categories(filename, user):
    filepath = RESOURCE_PATH + "categories/" + filename

    if "none" in filename:
        return None

    values = load_yaml(filepath)

    for category in values["categories"]:
        cat_data = {"name": category.title()}
        cat_form = CategoryForm(cat_data)
        save_form(cat_form, user)


def seed_descriptions(filename, user):
    filepath = RESOURCE_PATH + "descriptions/" + filename

    if "none" in filename:
        return None

    values = load_yaml(filepath)

    for rule in values["description_rules"]:
        # should only be one key per dict but use this format anyway
        for description, predicate in rule.items():
            dscr_data = {"description": description.title(),
                         "predicate": predicate}
            dscr_form = DescriptionForm(dscr_data)
            save_form(dscr_form, user)


def seed_transactions(filename, user):
    filepath = RESOURCE_PATH + "transactions/" + filename

    if "none" in filename:
        return None

    trxn_data = load_csv(filepath)
    
    print(trxn_data)

    for trxn in trxn_data:

        entry_data = {
            'date': trxn[0],
            'type': trxn[1],
            'amount': trxn[2],
            'account': Account.objects.get(name=trxn[3]),
            'original_description': trxn[4]
        }

        # this means the data also has a category
        if len(trxn) > 5:
            entry_data['pretty_description'] = trxn[5]
            print("TXN category", trxn[6])
            entry_data['category'] = Category.objects.get(name=trxn[6])

        transaction_form = TransactionForm(entry_data)
        save_form(transaction_form, user)


# TODO revisit the relationship between account and plugin
# TODO revisit how to save unique values and not duplicate ACCOUNT with multiple seeds
def seed_accounts():
    for account in get_enum_values(PLUGINS):
        account_form = AccountForm({"name": account})
        save_form(account_form)
