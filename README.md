# ledgered
track your expenses, in a ledger

## Transaction Schema and File Uploads

ledgered has a single unified transaction schema

| Column               | Description                                                                     | From Source File | Nullable | Blank-able |
|----------------------|---------------------------------------------------------------------------------|------------------|----------|------------|
| date                 | The date of the transaction                                                     | T                |          |            |
| account              | Which account this transaction corresponds to                                   | T                |          |            |
| type                 | Debit - value subtracted from this account / Credit value added to this account | T                |          |            |
| amount               | Amount of credit/debit. Always positive.                                        | T                |          |            |
| original description | Raw description provided from upload                                            | T                |          |            |
| pretty description   | Pretty description generated from description rule                              |                  | T        | T          |
| category             | Primary category for this transaction                                           |                  | T        |            |
| subcategory          | More detailed category for this transaction                                     |                  | T        | T          |

Uploaded files from your accounts and banks are facilitated by a "plugin" (ex: chase, fidelity). A plugin defines the
name of the account/plugin, the input schema, and a function that transforms the uploaded data into the unified 
transaction schema. The "Plugin" parent class defines all the other generic operations needed to convert a file upload 
into transaction data which can be written into the database.

The fields that unique define a transaction (not considered the pk's from the database, though) are:
(date, account, type, amount, original_description)

This basically means that if you had more than one of the same transaction in the same account from the same day that 
we are going to sum the amounts for those transactions and only save a single value to the database. We need a way to 
unique identify transactions so that when a user uploads another transaction file we don't accidentally duplicate transaction in the database for instances where 
the timeframe of 2 uploads overlaps. We only want to add new transactions to the database. 

The steps of processing an uploaded file using a plugin are roughly as follows.

Steps:
- receive upload form with account type (corresponding to plugin type), filename, and file data
  - account types are stored in database and correspond to enum in models.py
- Instantiate the correct plugin class corresponding to the upload form
- pass file contents (probably always .csv) to plugin.process_file()
- check that file isn't too large
- parse file headers and values into lists
- verify that headers from file match the expected headers defined in the plugin
- create a dataframe from file
- call process_raw_df() defined on plugin subclasses to transform raw df into unified transaction schema
- aggregate the processed df by (date, type, amount, original_description)
  - since each raw dataframe can only correspond to one account, we implicitly group by account type
- verify the processed output df from the plugin subclass
- For each transaction, determine if its already in the database, if not, add it!
  - If we find an existing transaction with the same (date, account, type, amount, original_description) then skip

## The Ledger

Go through transactions one by one where the objective is to give them a helpful pretty description and add a category
and (optional) subcategory.

### Pretty Descriptions

Pretty descriptions cannot be entered manually, but they are not required. However, the ledger will attempt to use 
previous pretty descriptions to find the appropriate category and subcategory for the current uncategorized transaction. 
Pretty descriptions are applied to a transaction using description rules. There are two types of description rules: 
Those with and without a predicate. For all description rules, the "description" field will be copied into the pretty 
description if this description is a match. For predicate description rules, if the predicate is a substring of the 
original description, the rule is a match. For rules without a predicate, the description is both the predicate and 
description.

The ledger will first look through all rules with a custom predicate and return that if its found. If no match is found
then it will look through all the rules without a custom predicate.

### Guessing Categories and Subcategories

For each new transaction, if there is a matching description rule (and thus a pretty description for this transaction),
then the ledger will look in the database for a previously ledgered transaction with this pretty description and 
use the category and subcategory of the previous transaction for the current transaction.
