from .plugin import Plugin
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class MintPlugin(Plugin):

    def __init__(self, user):
        super().__init__(user)

    def get_account_name(self):
        return "Mint"

    def get_input_schema(self):
        """Note: headers from file will be converted into snake case"""
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

    def process_raw_transaction_df(self, df):
        """Expected Output:
        {
            "date": "object",
            "type": "string",
            "amount": "float64",
            "original_description": "string"
        }
        """
        return df
