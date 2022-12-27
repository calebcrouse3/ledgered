"""Populates the database with default categories and description rules
Could be used to give starting point for new users or for a test account
Could be used to faciliate a description and category reset
"""

import yaml
import os
import csv
from ..forms import CategoryForm, SubcategoryForm, DescriptionForm, EntryForm
from ..models import Category


class Seeder():
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

    def load_yaml(self, file_path) -> dict:
        with open(file_path, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def load_csv(self, file_path) -> dict:
        """ return a csv reader on which you can call next line"""
        with open(file_path, newline='') as csvfile:
            csv_reader = csv.reader(file_path, delimiter=' ', quotechar='|')
            return [row for row in csv_reader]
            


class CategorySeeder(Seeder):
    """Seed the database with the test.yml categories"""

    def __init__(self):
        self.SEED_FILEPATH = os.getcwd() + "/ledgered_app/resources/categories/test.yml"

    def seed(self):
        values = self.load_yaml(self.SEED_FILEPATH)

        for category, subcategories in values.items():
            cat_data = {"name": category}
            cat_form = CategoryForm(cat_data)
            if cat_form.is_valid():
                cat_obj = cat_form.save(commit=False)
                cat_obj.save()

                if cat_obj:
                    for subcat in subcategories:
                        subcat_data = {"name": subcat}
                        subcat_form = SubcategoryForm(subcat_data)

                        if subcat_form.is_valid():
                            subcat_obj = subcat_form.save(commit=False)
                            subcat_obj.category = cat_obj
                            subcat_obj.save()


class DescriptionSeeder(Seeder):
    def __init__(self):
        self.SEED_FILEPATH = os.getcwd() + "/ledgered_app/resources/descriptions/test.yml"

    def seed(self):
        values = self.load_yaml(self.SEED_FILEPATH)

        for descr, params in values.items():
            descr_data = {
                    "is_identity": params["is_identity"],
                    "description": descr
                }

            if "predicate" in params.keys():
                descr_data["predicate"] = params["predicate"]
            else:
                descr_data["predicate"] = descr


            descr_form = DescriptionForm(descr_data)

            if descr_form.is_valid():
                descr_obj = descr_form.save(commit=False)
                descr_obj.save()


class EntriesSeeder(Seeder):
    def __init__(self):
        self.SEED_FILEPATH = os.getcwd() + "/ledgered_app/resources/entries/test.csv"

    def seed(self):
        csv_data = self.load_csv(self.SEED_FILEPATH)

        for row in csv_data:
            entry_data = {
                'date': row[0],
                'entry_type': row[1],
                'amount': row[2],
                'account': row[3],
                'original_description': row[4],
                'pretty_description': row[5],
                'category': row[6],
                'subcategory': row[7] 
            }

            entry_form = EntryForm(entry_data)

            if entry_form.is_valid():
                entry_obj = entry_form.save(commit=False)
                entry_obj.save()
