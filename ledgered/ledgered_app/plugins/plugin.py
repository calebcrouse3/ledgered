"""Defines a plugin which is a class that handles parsing of data from file 
uploads from various 3rd parties and inserts transactions data into the database."""

import re
from pandas import DataFrame
from ..forms import TransactionForm, UploadSummaryForm
from ..models import Transaction, Account
from ..utils.form_utils import save_form

import logging

logger = logging.getLogger(__name__)


NEW = "new"
UPDATED = "updated"  # this could be used for post AUTH transactions that show up twice with a new, higher, amount
DUPLICATE = "duplicate"
ERROR = "error"


def sign_to_type(number):
    if float(number) > 0:
        return "Credit"
    else:
        return "Debit"


def snake_case(s):
    """Convert strings to snake case"""
    return s.replace(" ", "_").lower()


def csv_line_to_list(line):
    """TODO there has to be a package that already does this better
    Splits contents of a single csv line into a list."""

    # removes white space and remaining quotes
    def clean(s):
        return re.sub(' +', ' ', s.replace('"', ""))

    # some plugins have quotes around each value. Handle these differently.
    if '"' in line:
        split_on = '","'
    else:
        split_on = ','

    return [clean(x) for x in line.split(split_on) if line != '']


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

    def verify_upload_headers(self, headers):
        """Checks that csv headers from file upload match the expected input schema"""

        msg = f"""ERROR: Headers for uploaded file csv do match match plugin schema."
        f"expected headers {self.INPUT_SCHEMA}"
        f"actual headers {headers}
        """

        if len(headers) != len(self.INPUT_SCHEMA):
            raise Exception(msg)

        for i in range(len(headers)):
            if snake_case(headers[i]) != self.INPUT_SCHEMA[i]:
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
            msg = "there were more than one transactions in the database matching this filter conditions. This should" \
                  "theoretically never happen!"
            raise ValueError(msg)
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
        """Determine what to do with an entry with an existing match in the db.
        If it's an exact duplicate, do nothing. If the amount in the new uploaded file
        is greater than that already in the database (could happen with transaction rollup or authorization updates)
        then overwrite the amount with the new larger amount."""

        if form.data["amount"] > matching_entry.amount:
            matching_entry.amount = form.data.amount
            matching_entry.save()
            return UPDATED
        else:
            return DUPLICATE

    def consolidate_amount(self, df):
        """Multiple transactions from the same vendor on the same day will get their amounts aggregated.
        This handles the edge case where subsequent transactions on the same day get ignored because we check all new
        transactions against existing transactions in the database and ignore those that already appear. This step is
        necessary to not duplicate transactions from file uploads for the same account with overlapping time frames"""

        return df.groupby(['date', 'type', 'original_description'], as_index=False).amount.sum()

    def process_new_potential_transaction(self, row):
        """Takes a row from df and determines what to do with it."""

        form_data = {
            "date": row["date"],
            "type": row["type"],
            "amount": round(row["amount"], 2),
            "account": Account.objects.get(name=self.ACCOUNT_NAME),
            "original_description": row["original_description"],
            "pretty_description": None,
            "category": None
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

    def parse_lines(self, lines):
        """Split each line of text from the csv file into a list of values.
        Verify the length of each list is correct
        """

        parsed_lines = []
        errors = 0
        # start at one so we ignore the header
        for line in lines:
            next_line = csv_line_to_list(line)

            if len(next_line) != len(self.INPUT_SCHEMA):
                errors += 1
                logger.error(f"Error parsing line from csv file. Length did not match. {next_line}")
            else:
                parsed_lines.append(next_line)

        return parsed_lines, errors

    def process_file(self, file):
        """Process file data into the database"""

        file_upload_summary_data = {
            "new": 0,
            "updated": 0,
            "duplicate": 0,
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
        headers = lines.pop(0)
        parsed_headers = [snake_case(colname) for colname in csv_line_to_list(headers)]

        self.verify_upload_headers(parsed_headers)

        # parse csv text as 2d list to pass to data frames. Start at index=1 to ignore header line
        parsed_lines, errors = self.parse_lines(lines)
        file_upload_summary_data[ERROR] += errors

        raw_df = DataFrame(parsed_lines, columns=parsed_headers)
        processed_df = self.consolidate_amount(self.process_raw_transaction_df(raw_df))

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

            # process contents and get back NEW, DUPLICATE, IGNORE, ERROR, etc
            entry_results = self.process_new_potential_transaction(row)
            file_upload_summary_data[entry_results] += 1

        summary_form = UploadSummaryForm(data=file_upload_summary_data)
        save_form(summary_form, self.USER)
