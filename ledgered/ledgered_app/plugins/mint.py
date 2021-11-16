from ..forms import EntryForm
from ..models import Entry
from .plugin import Plugin
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# TODO verify that we actually need to aggregate transactions at all?

class MintPlugin(Plugin):

    def __init__(self):
        super().__init__()


    def get_input_schema(self):
        """Define expected input schema for this plugin csv."""
        return [
            "date",
            "description",
            "original_description",
            "amount",
            "transaction_type",
            "category",
            "account_name",
            "labels",
            "notes",
        ]


    def get_matching_entry(self, form):
        """Returns matching entry if it exists and handles unexpected behaviors."""
        e = (
            Entry.objects
            .filter(date = form.data["date"])
            .filter(account = form.data["account"])
            .filter(entry_type = form.data["entry_type"])
            .filter(original_description = form.data["original_description"])
        )

        if len(e) > 0:

            if len(e) > 1:
                print("ERROR - number of matching entries is greater than 1")

            return e[0]

        else:
            return None



    def create_form_data(self, row):
        """Create a data dict from rollup df to pass into a form."""
        return {
            "date": datetime.strptime(row["date"], "%m/%d/%Y").date(),
            "entry_type": row["entry_type"],
            "amount": float(row["amount"]),
            "account": "Mint",
            "original_description": row["original_description"],
            "pretty_description": None,
            "category": None,
            "subcategory": None,
        }


    def handle_new_entry(self, form):
        """Save a new entry."""
        if form.is_valid():
            form.save()
            print("SUCCESS: entry submitted")
            return "new"

        else:
            print("ERROR new entry form not valid")
            print(form.errors)
            return "error"


    def handle_matching_entry(self, form, matching_entry):
        """Determine what to do with a entry with an existing match in the db."""
        if form.data["amount"] > matching_entry.amount:
            print("SUCCESS: existing entry amount overwritten")
            Entry.objects.filter(id=matching_entry.id).update(amount=form.data["amount"])
            return "updated"

        else:
            print("INFO: duplicate entry ignored")
            return "duplicate"

    
    def new_entry_handler(self, row):
        """Takes a row from the rollup df and determines what to do with it."""

        form = EntryForm(self.create_form_data(row))
        # if everything is working, there should only be one matching entry
        matching_entry = self.get_matching_entry(form)

        if matching_entry:
            result = self.handle_matching_entry(form, matching_entry)

        elif not matching_entry:
            result = self.handle_new_entry(form)

        else:
            result = "error"

        return result


    def rollup_file_data(self, lines):
        """Take parsed lines and rollup into df."""
        entries_df = pd.DataFrame(lines, columns=self.INPUT_SCHEMA)
        entries_df.rename(columns={"transaction_type":"entry_type"}, inplace=True)
        entries_df["amount"] = entries_df["amount"].astype(float)
        rollup_df = entries_df.groupby(self.ROLLUP_KEYS, as_index=False).sum("amount")
        return rollup_df


    def process(self, file):
        """Process file data into the data base"""

        file_upload_result_summary = {
            "new": 0,
            "updated": 0,
            "duplicate": 0,
            "error": 0
        }

        if file.size < 10e5:
            file_data = file.read().decode("utf-8")
            lines = file_data.split("\n")
            headers = [self.snake_string(colname) for colname in self.process_line(lines[0])]

            if self.verify_headers(headers):
                # parse csv text as 2d list to pass to data frames
                processed_lines = [self.process_line(line) for line in lines[1:]]
                rollup_df = self.rollup_file_data(processed_lines)

                for _, row in rollup_df.iterrows():
                    entry_results = self.new_entry_handler(row)
                    file_upload_result_summary[entry_results] += 1

            else:
                print("ERROR - Headers for uploaded file csv do match match plugin schema.")

        else:
            print("ERROR - Uploaded file too large.")

        return file_upload_result_summary
