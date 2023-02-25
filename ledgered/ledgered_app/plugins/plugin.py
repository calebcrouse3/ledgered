"""Defines a plugin which is a class that handles parsing of data from file 
uploads from various 3rd parties and inserts transactions data into the database."""

import re
from pandas import DataFrame
from ..forms import TransactionForm, UploadSummaryForm
from ..models import Transaction, Account
from ..utils.form_utils import save_form

NEW = "new"
UPDATED = "updated"
IGNORED = "ignored"
ERROR = "error"


class Plugin:
    def __init__(self, user):
        self.INPUT_SCHEMA = self.get_input_schema()
        self.ACCOUNT_NAME = self.get_account_name()

        # expected output df schema after processing by plugin subclass
        self.OUTPUT_SCHEMA = {
            "date": "object",
            "type": "string",
            "amount": "float64",
            "original_description": "string"
        }

        self.USER = user

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

    def sign_to_type(self, number):
        if float(number) > 0:
            return "Credit"
        else:
            return "Debit"

    def snake_case(self, s):
        """Convert strings to snake case"""
        return s.replace(" ", "_").lower()

    def csv_line_to_list(self, line):
        """Splits contents of a single csv line into a list"""
        return [re.sub(' +', ' ', x.replace('"', "")) for x in line.split(",")]

    def verify_upload_headers(self, headers):
        """Checks that csv headers from file upload match the expected input schema"""

        msg = f"""ERROR: Headers for uploaded file csv do match match plugin schema."
        f"expected headers {self.INPUT_SCHEMA}"
        f"actual headers {headers}
        """

        if len(headers) != len(self.INPUT_SCHEMA):
            raise Exception(msg)

        for i in range(len(headers)):
            if self.snake_case(headers[i]) != self.INPUT_SCHEMA[i]:
                raise Exception(msg)

    def get_matching_transactions(self, form):
        """Return any transactions already in the database that match this form"""

        count = Transaction.objects.filter(
            owner=self.USER,
            date=form.data["date"],
            type=form.data["type"],
            account__name__exact=form.data["account"].name,
            original_description=form.data["original_description"]
        ).count()

        if count > 1:
            raise ValueError("there were more than one transactions in the database matching this filter conditions")
        elif count == 1:
            match = Transaction.objects.get(
                owner=self.USER,
                date=form.data["date"],
                type=form.data["type"],
                account__name__exact=form.data["account"].name,
                original_description=form.data["original_description"]
            )
            return match
        else:
            return None

    def handle_matching_trxn(self, form, matching_entry):
        """TODO TBD how we are going to handle duplicate transactions.
        Determine what to do with an entry with an existing match in the db.
        If it's an exact duplicate, do nothing. If the amount in the new uploaded file
        is greater than that already in the database (could happen with transaction rollup)
        then overwrite the amount with the new larger amount."""
        return IGNORED

    def process_new_potential_transaction(self, row):
        """Takes a row from df and determines what to do with it."""

        form_data = {
            "date": row["date"],
            "type": row["type"],
            "amount": round(row["amount"], 2),
            "account": Account.objects.get(name=self.ACCOUNT_NAME),
            "original_description": row["original_description"],
            "pretty_description": None,
            "category": None,
            "subcategory": None,
        }

        form = TransactionForm(form_data)
        matching_entry = self.get_matching_transactions(form)

        if matching_entry:
            return self.handle_matching_trxn(form, matching_entry)

        elif not matching_entry:
            save_form(form, self.USER)
            return NEW

        else:
            return ERROR

    def verify_processed_df(self, df):
        # verify all columns are present and there's no extra columns
        expect_cols = set(self.OUTPUT_SCHEMA.keys())
        actual_cols = set(df.columns.values)
        if expect_cols != actual_cols:
            msg = f"""Processed df for plugin {self.ACCOUNT_NAME} did not match the expected output schema
            expected: {expect_cols}
            actual: {actual_cols}
            """
            raise Exception(msg)

        # verify the data type of each column is correct
        for column, dtype in self.OUTPUT_SCHEMA.items():
            if df[column].dtype != self.OUTPUT_SCHEMA[column]:
                msg = f"""dtype for column "{column}" in processed transactions df from plugin {self.ACCOUNT_NAME} did 
                not match the expected dtype
                expected: {dtype}
                actual: {df[column].dtype}
                """
                raise Exception(msg)

    def process_file(self, file):
        """Process file data into the database"""

        file_upload_summary_data = {
            "new": 0,
            "updated": 0,
            "ignored": 0,
            "error": 0,
            "filename": file.name,
            "account": self.ACCOUNT_NAME,
            "min_date": None,
            "max_date": None
        }

        if file.size > 10e5:
            raise Exception("ERROR: Uploaded file too large.")

        file_data = file.read().decode("utf-8")
        lines = file_data.split("\n")
        headers = [self.snake_case(colname) for colname in self.csv_line_to_list(lines[0])]

        self.verify_upload_headers(headers)

        # parse csv text as 2d list to pass to data frames
        upload_lines = [self.csv_line_to_list(line) for line in lines[1:] if len(line) > 0]
        upload_df = DataFrame(upload_lines, columns=self.INPUT_SCHEMA)
        processed_df = self.process_raw_transaction_df(upload_df)

        self.verify_processed_df(processed_df)

        for _, row in processed_df.iterrows():

            # handle dates
            date = row['date']

            if not file_upload_summary_data["min_date"]:
                file_upload_summary_data["min_date"] = date
                file_upload_summary_data["max_date"] = date

            if date < file_upload_summary_data["min_date"]:
                file_upload_summary_data["min_date"] = date

            if date > file_upload_summary_data["max_date"]:
                file_upload_summary_data["max_date"] = date

            # process contents and get back NEW, DUPLICATE, IGNORE, ERROR
            entry_results = self.process_new_potential_transaction(row)
            file_upload_summary_data[entry_results] += 1

        summary_form = UploadSummaryForm(data=file_upload_summary_data)
        save_form(summary_form, self.USER)
