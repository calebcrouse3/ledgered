"""Populates the database with default categories and description rules
Could be used to give starting point for new users or for a test account
Could be used to faciliate a description and category reset
"""

import yaml
import os
import csv
from ..forms import CategoryForm, SubcategoryForm, DescriptionForm, TransactionForm, AccountForm
from ..models import PLUGINS, Account, Category, Subcategory
import logging.config
from ..config import LOGGER_CONFIG_PATH
logging.config.fileConfig(LOGGER_CONFIG_PATH)


class Seeder:
    """Seeds the database with data from a yaml or csv file"""
    def save_form(self, form):
        """Save a form."""
        if form.is_valid():
            form.save()
            print(f"SUCCESS: {type(form)} submitted")
            return "new"

        else:
            print(f"ERROR: {type(form)} form not valid")
            print(form.errors)
            return "error"

    def load_yaml(self, file_path):
        with open(file_path, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
            
    def load_csv(self, file_path):
        with open(file_path, 'r') as read_obj:
            csv_reader = csv.reader(read_obj)
            return list(csv_reader)

    def set_run_seed(self, filename):
        if filename == "none":
            return False
        else:
            return True


class CategorySeeder(Seeder):
    """Seed the database with the categories"""

    def __init__(self, source_filename, user):
        self.SEED_FILEPATH = os.getcwd() + "/ledgered_app/resources/categories/" + source_filename
        self.RUN_SEED = self.set_run_seed(source_filename)
        self.USER = user
        self.LOGGER = logging.getLogger('seeder')

    def seed(self):
        if not self.RUN_SEED:
            return None

        values = self.load_yaml(self.SEED_FILEPATH)

        for category, subcategories in values.items():
            self.LOGGER.debug(f"number of subcategories for {category}: {len(subcategories)}")

            cat_data = {
                "owner": self.USER,
                "name": category.title()
            }
            cat_form = CategoryForm(cat_data)

            if cat_form.is_valid():
                cat_obj = cat_form.save(commit=False)
                cat_obj.save()
                self.LOGGER.debug(f"successfully saved category: {cat_form.data}")
            else:
                cat_obj = None
                self.LOGGER.debug(f"failed to save category: {cat_form.errors}")

            if cat_obj:
                for subcat in subcategories:

                    subcat_data = {
                        "name": subcat.title(),
                        "category": cat_obj
                    }
                    subcat_form = SubcategoryForm(subcat_data)

                    if subcat_form.is_valid():
                        subcat_obj = subcat_form.save(commit=False)
                        subcat_obj.save()
                        self.LOGGER.debug(f"successfully saved subcategory: {subcat_form.data}")
                    else:
                        self.LOGGER.debug(f"failed to save subcategory: {subcat_form.errors}")


class DescriptionSeeder(Seeder):
    def __init__(self, source_filename, user):
        self.SEED_FILEPATH = os.getcwd() + "/ledgered_app/resources/descriptions/" + source_filename
        self.RUN_SEED = self.set_run_seed(source_filename)
        self.USER = user

    def seed(self):
        if not self.RUN_SEED:
            return None

        values = self.load_yaml(self.SEED_FILEPATH)
        for rule in values["description_rules"]:
            # should only be one key per dict but use this format anyway
            for description, predicate in rule.items():
                dscr_data = {
                        "owner": self.USER,
                        "description": description.title(),
                        "predicate": predicate
                    }

                dscr_form = DescriptionForm(dscr_data)

                if dscr_form.is_valid():
                    descr_obj = dscr_form.save(commit=False)
                    descr_obj.save()


class AccountSeeder(Seeder):
    def seed(self):
        for name, _ in PLUGINS:
            account_form = AccountForm({"name": name})

            if account_form.is_valid():
                if len(Account.objects.filter(name=name)) == 0:
                    account_obj = account_form.save(commit=False)
                    account_obj.save()


class TransactionSeeder(Seeder):
    def __init__(self, source_filename, user):
        self.SEED_FILEPATH = os.getcwd() + "/ledgered_app/resources/transactions/" + source_filename
        self.RUN_SEED = self.set_run_seed(source_filename)
        self.USER = user

    def seed(self):
        if not self.RUN_SEED:
            return None

        csv_data = self.load_csv(self.SEED_FILEPATH)

        for row in csv_data:

            entry_data = {
                'owner': self.USER,
                'date': row[0],
                'type': row[1],
                'amount': row[2],
                'account': Account.objects.get(name=row[3]),
                'original_description': row[4]
            }

            # this means the data also has categories
            if len(row) == 8:
                entry_data['pretty_description'] = row[5]
                entry_data['category'] = Category.objects.get(name=row[6])
                if row[7] != "":
                    entry_data['subcategory'] = Subcategory.objects.get(name=row[7])

            transaction_form = TransactionForm(entry_data)

            if transaction_form.is_valid():
                entry_obj = transaction_form.save(commit=False)
                entry_obj.save()
            else:
                print(f"Seeder filed to validate transaction form with data {entry_data}")
                print(f"ERROR: {transaction_form.errors}")
