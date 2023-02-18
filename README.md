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
name of the account/plugin, the input schema, and a function that converts the uploaded data into the correct format.
The parent plugin class defines all the other generic operations needed to convert a file upload into transactions
which can be written into the database.

The fields that unique define a transaction (not considered the pk's though) are:
[date, account, type, amount, original_description]

This basically means that if you had more than one of the same transaction in the same account from the same day that 
we are going to only take the transaction with the highest value. We need a way to unique identify transactions so that
when a user uploads another transaction file we don't accidentally duplicate transaction in the database. We only want
to add new transactions to the database. Do we need to aggregate these values though? When would not aggregating mess
us up? 

If a transaction is updated with a new amount, like adding a tip.

What does this buy us?

What might go wrong here?

The steps of processing an uploaded file using a plugin are roughly as follows.

Steps:
- receive upload form with account type and filename/contents
  - account types are stored in database and correspond to enum in models.py
- Instantiate the correct plugin class by reading the upload form account type
- pass file contents (probably always .csv) to plugin.process_file()
- check that file isn't too large
- parse file headers and values into lists
- verify that headers from file match the expected headers defined in the plugin
- create a dataframe from file
- call plugin subclass specific process_raw_df() to map raw df into master transaction schema
- aggregate the processed df # gonna skip this for now!
- verify the processed output df from the plugin subclass
- For each transaction, determine if its already in the database, if not, add it!

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

# DEV

### where you left off

get_matching_transactions not finding matching transactions (maybe because it errors when it doesn't match?)
Should account be a database option? Need to fix where we enter in uploaded transactions account value
Account needs to be a database value and you can only upload accounts after adding the database value. Just use seed the database with all the accounts we have plugins for.
Need to be able to seed description/categories/accounts different from transactions because we might want to get transactions through a raw upload
Need to enforce that there's no duplicates in account names for each user. Or maybe even just globally.

### TODO List
1. Find more graceful way to define and enforce the plugin types and transaction types (constants) and use them throughout
2. Find graceful way to enforce schemas of dataframe coming out of the plugin and going into data aggregation
3. Is there a way to fail when processing raw transaction df by only dropping a single row and not the whole data frame?
   4. Maybe do everything like by line and without pandas? Even the aggregation? Or maybe just do as little as possible with pandas
4. Find better way to do more error handling during file upload process
5. Figure out how to prevent data duplication for descriptions when seeding data
6. Find somewhere to hard code the transaction fields which define a unique transaction (date, account, type, amount, original_description). Do we actually need to do this?
7. make abbrevioations for long words
   8. trxn - transaction
   9. dscr - descrition
   10. acct - account
   11. cat - category
   12. subcat - subcategory

13. Make some upload tests
    14. mostly with how to handle uploading new transactions

- revisit enums being a single letter versus a whole word and just yeah what's up with enums

#### more commands
open django shell
`python manage.py shell`


view all categories in database
```
from ledgered_app.models import Category
cats = Category.objects.all()
for cat in cats:
    print(cat.id, cat.name)
```


view all subcategories in database
```
from ledgered_app.models import Subcategory
subcats = Subcategory.objects.all()
for subcat in subcats:
    print(subcat.id, subcat.name, subcat.category.name)
```


view subcategories for a particular category.
subcategory has a forgeign key as category which allows us to call "subcategory_set" on a category
```
c = Category.objects.get(id=90)
c.subcategory_set.all()
```


Find transactions that match filter conditions
```
from ledgered_app.models import Transaction, Account
import datetime

Transaction.objects.filter(
   #account__name="Chase",
   type="Debit",
   date=datetime.date(2023, 2, 14),
   #original_description=form.data["original_description"],
).count()
```

