from .plugin import Plugin
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class ChasePlugin(Plugin):

    def __init__(self):
        super().__init__()

    def get_input_schema(self):
        """Note: headers from file will be converted into snake case"""
        return [
            "transaction_date",
            "post_date",
            "description",
            "category",
            "type",
            "amount",
            "memo"
        ]

    def get_account_id(self):
        return "C"

    # date, type, amount, account, original_description
    def process_raw_transaction_df(self, df):
        processed_df = df.copy()
        processed_df.rename(columns={"description": "original_description"}, inplace=True)
        # -/+ amount is debit/credit
        processed_df["type"] = processed_df["amount"].apply(lambda x: self.sign_to_type(x))
        processed_df["amount"] = processed_df["amount"].astype(float).apply(abs)
        processed_df["date"] = processed_df["transaction_date"].apply(lambda x: datetime.strptime(x, "%m/%d/%Y").date())
        return processed_df[["date", "type", "original_description", "amount"]]
