"""Populates the database with default categories and description rules
Could be used to give starting point for new users.
Could be user to faciiliate a description and category reset
"""

import yaml
import os
from ..forms import CategoryForm, SubcategoryForm
from ..models import Category


class Seeder():
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


class CategorySeeder(Seeder):
    def __init__(self):
        self.SEED_FILEPATH = os.getcwd() + "/ledgered_app/seeding/categories.yml"

    def seed(self):
        print(self.SEED_FILEPATH)
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
        self.SEED_FILEPATH = "./descriptions.yml"

    def seed(self):
        values = self.load_yaml(self.SEED_FILEPATH)
        
