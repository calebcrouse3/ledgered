from numpy import deprecate
from numpy.lib.function_base import delete
from ..forms import EntryForm
from ..models import Entry
from .plugin import Plugin
from datetime import datetime
import pandas as pd
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# TODO need to add logic to determine if transaction are new one or not

class MintPlugin(): # make this a child class later (Plugin)
    def __init__(self):
        self.INPUT_SCHEMA = [
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

        # defines the columns on which entries will have amounts summed across
        self.ENTRY_ROLLUP_KEYS = [
            "date",
            "account",
            "entry_type",
            "original_description",
        ]

    def snake_string(self, s):
        return s.replace(" ", "_").lower()

    def verify_headers(self, headers):
        if len(headers) != len(self.INPUT_SCHEMA):
            return False

        for i in range(len(headers)):
            if self.snake_string(headers[i]) != self.INPUT_SCHEMA[i]:
                return False

        return True

    def get_matching_keyed_entries(self, entry):
        """Returns true if entry does not exist in the database"""
        e = (
            Entry.objects
            .filter(date = entry.date)
            .filter(account = entry.account)
            .filter(entry_type = entry.entry_type)
            .filter(original_description = entry.original_description)
        )
        return e


    @deprecate
    def process(self, file):
        """Process new file and handle submission of entries to DB"""
        #with open('some/file/name.txt', 'wb+') as destination:

        def process_line(line):
            return [x.replace('"', "") for x in line.split(",")]

        new_entry_count = 0
        if file.size < 10e5:
            file_data = file.read().decode("utf-8")
            lines = file_data.split("\n")
            headers = [self.snake_string(colname) for colname in process_line(lines[0])]

            if self.verify_headers(headers):
                for line in lines[1:]:

                    print(line)

                    values = process_line(line)
                    named_values = dict(zip(headers, values))

                    form = EntryForm()
                    entry = form.save(commit=False)

                    entry.date = str(datetime.strptime(named_values["Date"], "%m/%d/%Y"))
                    entry.entry_type = named_values["Transaction Type"]
                    entry.amount = float(named_values["Amount"])
                    entry.account = "Chase"
                    entry.original_description = named_values["Original Description"]
                    entry.pretty_description = None
                    entry.category = None
                    entry.subcategory = None

                    # make rows unique by adding an incrementor for similar entrys
                    # similar as in same date, account, amount, desc
                    entry.entry_key_idx_num = self.num_similar_entries(entry)

                    if form.is_valid():
                        
                        if True: # self.new_entry(entry):
                            entry.save()
                            print("SUCCESS: entry submitted")
                            new_entry_count += 1
     

                    else:
                        print("ERROR: form invalid")
                        print(form.errors)
                    
            else:
                print("ERROR: headers dont match")
                print(f"Headers: {headers}")
                print(f"Input Schema: {self.INPUT_SCHEMA}")

        else:
            print("ERROR: file too large")

        return new_entry_count






    def process_pandas(self, file):

        def process_line(line):
            return [x.replace('"', "") for x in line.split(",")]

        new_entry_count = 0

        if file.size < 10e5:
            file_data = file.read().decode("utf-8")
            lines = file_data.split("\n")
            headers = [self.snake_string(colname) for colname in process_line(lines[0])]

            if self.verify_headers(headers):
                # process each line after the header line by parsing them into lists
                processed_lines = [process_line(line) for line in lines[1:]]

                # if summed amount for the rollup group is larger than amount in matching entry in DB, replace with that larger amount
                # this might create some edge cases where uploading two files with mutually exlusive time windows dont produce the correct results for 
                # duplicate entries on the same day

                entries_df = pd.DataFrame(processed_lines, columns=headers)

                entries_df.rename(columns={"transaction_type":"entry_type"}, inplace=True)

                grouped_entries_df = entries_df.groupby(self.ENTRY_ROLLUP_KEYS).sum("amount")

                for row in grouped_entries_df.iterrows():
                    # TODO for each row, if the rollup key is not in the db, add the whole entry, 
                    # if it is in the DB but the amount is smaller, update the amount with the larger amount
                    # if it is and the amount is the same, ignore that entry, its considered a duplicate

                    form = EntryForm()
                    entry = form.save(commit=False)

                    entry.date = str(datetime.strptime(row["date"], "%m/%d/%Y"))
                    entry.entry_type = row["entry_type"]
                    entry.amount = float(row["amount"])
                    entry.account = "Mint"
                    entry.original_description = row["original_description"]
                    entry.pretty_description = None
                    entry.category = None
                    entry.subcategory = None

                    matching_entries = self.get_matching_keyed_entries(entry)

                    if len(matching_entries) == 0:
                        if form.is_valid():
                            entry.save()
                            print("SUCCESS: entry submitted")
                            new_entry_count += 1
                        

                    elif len(matching_entries) > 0:
                        # grab first matching entry in case there are multiple
                        matching_entry = matching_entries[0]

                        if entry.amount > matching_entry.amount:
                            pass
                            # TODO update existing entry with larger amount
                        

                    elif len(matching_entries > 1):
                        logger.error("ERROR -  number of matching entries is greater than 1")


            else:
                logger.error("ERROR Headers for uploaded file csv do match match plugin schema.")

        else:
            logger.error("ERROR Uploaded file too large.")
