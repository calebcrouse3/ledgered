from ..forms import TransactionForm
from ..models import Transaction
from .plugin import Plugin
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class MintPlugin(Plugin):

    def __init__(self):
        super().__init__()

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

    def get_account_name(self):
        return "Mint"

    def process_raw_transaction_df(self, df):
        df["amount"] = df["amount"].astype(float)
        rollup_df = df.groupby(self.ROLLUP_KEYS, as_index=False).sum("amount")
        return rollup_df
