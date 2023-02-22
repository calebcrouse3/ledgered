from .plugin import Plugin
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class FidelityPlugin(Plugin):

    def __init__(self, user):
        super().__init__(user)

    def get_account_name(self):
        return "Fidelity"

    def get_input_schema(self):
        """Note: headers from file will be converted into snake case"""
        return [
            "date",
            "transaction",
            "name",
            "memo",
            "amount"
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
        processed_df = df.copy()
        processed_df.rename(columns={"transaction": "type", "name": "original_description"}, inplace=True)
        # get first letter from "CREDIT", "DEBIT" since that's what the transaction form accepts
        processed_df["type"] = processed_df["type"].apply(lambda x: x[0])
        processed_df["amount"] = processed_df["amount"].astype(float).apply(abs)
        processed_df["date"] = processed_df["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").date())
        return processed_df[["date", "type", "original_description", "amount"]]
