Description:

Allows you to upload your transactions as files from bank websites, mint, amazon, etc, and keep one unified
database of your transactions. Allows you to label transactions with categories that you define and manage. 
Automatically infers possible categories for new transactions which you will verify. Allows you to see dashboards
and reports of your labeled transactions to analyze you spending habits.

### Pages:
- Welcome
- Register
- Login
- Upload
- Ledger
- Reports
- Manage
    - Category Manager
    - Description Manager
    - Transaction Manager


### Page Descriptions:
- Upload: \
Allows you to upload files from sources like your bank, mint, amazing, and will process any new transactions as 
items in the data base. Might allow you to see previously uploaded files

- New Transactions: \
View currently unlabeled transactions and assign them to categories one at a time to be commited to the data base.
Will automatically infer likely pretty descriptions and categories based on previous data. Will allow you to enter new 
description rules on the fly.

- Reports: \
Generate interactive reports and dashboards of you spending behavior for analysis. Report item include: spending by category over time, changes in spending, top expenses, total expenses over time, etc

- Category Manager
CRUD ops on transaction categories Will Update existing transactions accordingly

- Description Manager
CRUD existing description rules. Will Update existing transactions accordingly

- Transaction Manager
CRUD ops on categories of existing transactions. Delete transactions from the data base all together. Add manual transactions


### TODO List

create function to generate default categories, subcategories, description_rules