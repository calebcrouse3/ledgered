"""Defines a plugin which is a class that handles parsing of data from file 
uploads from various 3rd parties and insert file transactions data into the database.

how files are processed
1. Input file is validated against plugins defined input schema
2. Input file is read in row by row and converted into a pandas dataframe
3. Columns from dataframe are translated into master transaction schema
4. Transaction from dataframe are aggregated to remove transaction with duplicate keys
5. Each transaction is converted into a form and checked against the database to see if its already been uploaded,
if not its uploaded into the database
"""

import re
from pandas import DataFrame
from datetime import datetime
from ..forms import TransactionForm
from ..models import Transaction


class Plugin:
    def __init__(self):
        self.INPUT_SCHEMA = self.get_input_schema()
        self.ACCOUNT_NAME = self.get_account_name()

    """
    Abstract methods
    """

    def get_input_schema(self):
        """List of expected columns from a file upload csv for this plugin type"""
        pass

    def get_account_name(self):
        """Get the account name of this plugin"""
        pass

    def process_raw_transaction_df(self, transactions_df: DataFrame) -> DataFrame:
        """Converts and formats transactions from plugin schema to master schema"""
        pass

    """
    Defined methods
    """

    def to_snake_string(self, s):
        """convert title strings to snake case"""
        return s.replace(" ", "_").lower()

    def csv_line_to_list(self, line):
        """Splits contents of a single csv line into a list"""
        return [re.sub(' +', ' ', x.replace('"', "")) for x in line.split(",")]

    def verify_headers(self, headers):
        """Checks that csv headers from file upload match the expected input schema"""

        if len(headers) != len(self.INPUT_SCHEMA):
            return False

        for i in range(len(headers)):
            if self.to_snake_string(headers[i]) != self.INPUT_SCHEMA[i]:
                return False

        return True

    def aggregated_transaction_data(self, df: DataFrame) -> DataFrame:
        rollup_keys = ["date", "type", "original_description"]
        return df.groupby(rollup_keys, as_index=False).sum("amount")

    def get_matching_transactions(self, form):
        """If transaction already exists in database with the same information as this form,
        return that entry. This function is used to determine when we are trying to upload
        a file with transactions that already exist in the database and should not be
        uploaded twice.
        """

        e = (
            Transaction.objects
            .filter(date=form.data["date"])
            .filter(account=form.data["account"])
            .filter(type=form.data["type"])
            .filter(original_description=form.data["original_description"])
        )

        if len(e) > 0:

            if len(e) > 1:
                print("ERROR - number of matching transactions is greater than 1")

            return e[0]

        else:
            return None

    def handle_matching_transcation(self, form, matching_entry):
        """Determine what to do with an entry with an existing match in the db.
        If it's an exact duplicate, do nothing. If the amount in the new uploaded file
        is greater than that already in the database (could happen with transaction rollup)
        then overwrite the amount with the new larger amount."""

        if form.data["amount"] > matching_entry.amount:
            print("SUCCESS: existing entry amount overwritten")
            Transaction.objects.filter(id=matching_entry.id).update(amount=form.data["amount"])
            return "updated"

        else:
            print("INFO: duplicate entry ignored")
            return "duplicate"

    def save_new_transaction(self, form):
        """Save a new database entry using a form."""
        if form.is_valid():
            form.save()
            print("SUCCESS: entry submitted")
            return "new"

        else:
            print("ERROR new entry form not valid")
            print(form.errors)
            return "error"

    def process_new_potential_transaction(self, row):
        """Takes a row from the rollup df and determines what to do with it."""

        form = TransactionForm(self.create_form_data(row))
        # if everything is working, there should only be one matching entry at most
        matching_entry = self.get_matching_transactions(form)

        if matching_entry:
            result = self.handle_matching_transcation(form, matching_entry)

        elif not matching_entry:
            result = self.save_new_transaction(form)

        else:
            result = "error"

        return result

    def create_form_data(self, row):
        """Create a data dict from a row on the transactions rollup df to pass into a form."""
        return {
            "date": row["date"],
            "type": row["type"],
            "amount": row["amount"],
            "account": self.ACCOUNT_NAME,
            "original_description": row["original_description"],
            "pretty_description": None,
            "category": None,
            "subcategory": None,
        }

    def process_file(self, file):
        """Process file data into the database"""

        file_upload_result_summary = {
            "new": 0,
            "updated": 0,
            "duplicate": 0,
            "error": 0 # should error just throw an exception?
        }

        if file.size < 10e5:
            file_data = file.read().decode("utf-8")
            lines = file_data.split("\n")
            headers = [self.to_snake_string(colname) for colname in self.csv_line_to_list(lines[0])]

            if self.verify_headers(headers):
                # parse csv text as 2d list to pass to data frames
                processed_lines = [self.csv_line_to_list(line) for line in lines[1:] if len(line) > 0]
                raw_df = DataFrame(processed_lines, columns=self.INPUT_SCHEMA)
                processed_df = self.aggregated_transaction_data(self.process_raw_transaction_df(raw_df))

                for _, row in processed_df.iterrows():
                    entry_results = self.process_new_potential_transaction(row)
                    file_upload_result_summary[entry_results] += 1

            else:
                print("ERROR - Headers for uploaded file csv do match match plugin schema.")
                print(f"expected headers {self.INPUT_SCHEMA}")
                print(f"actual headers {headers}")

        else:
            print("ERROR - Uploaded file too large.")

        return file_upload_result_summary
