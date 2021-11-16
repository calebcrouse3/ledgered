"""Defines a plugin which is a class that handles parsing of data from file 
uploads from various 3rd parties and insert file data into the data base"""

import re
# from abc import ABC
# from abc import abstractmethod

class Plugin():
    def __init__(self):
        self.INPUT_SCHEMA = self.get_input_schema()
        self.ROLLUP_KEYS = self.get_rollup_keys()


    def snake_string(self, s):
        """convert title strings to snake case"""
        return s.replace(" ", "_").lower()


    def process_line(self, line):
        """Plits contents of a single csv line into a list"""
        return [re.sub(' +', ' ', x.replace('"', "")) for x in line.split(",")]


    def get_rollup_keys(self):
        """defines the columns on which entries will have amounts summed across"""
        return [
            "date",
            "entry_type",
            "original_description",
        ]


    def verify_headers(self, headers):
        """Checks that csv headers from file upload match the expected input schema"""

        if len(headers) != len(self.INPUT_SCHEMA):
            return False

        for i in range(len(headers)):
            if self.snake_string(headers[i]) != self.INPUT_SCHEMA[i]:
                return False

        return True


    def get_input_schema(self):
        """Expect list of input columns for a specific plugin"""
        pass
