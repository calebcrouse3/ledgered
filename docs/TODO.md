### Where you left off

### TODO List
- Nail down transaction processing logic. Make a runbook for ledgering!
  - Aggregation
  - Duplication
  - Updating
  - AUTH:
  - Transfers
- ENUMs
  - define and enforce transaction and plugin types
  - single letter versus whole word
- File uploads
  - would be nice to have some error handing for a file upload that only uploads a portions of the transactions.
    - complete versus incomplete
  - Is there a way to fail when processing raw transaction df by only dropping a single row and not the whole data frame?
  - Maybe do everything line by line and without pandas? Even the aggregation? Or maybe just do as little as possible with pandas
- What about using the CSV module for parsing resources?
- Need some sort of message on screen when not entering transaction data correctly
- Not subcategory options available when category is none. You can see all the subcategories in the DD when you first open the ledger queue

# Helpful!

if your jypter notebook cant find the installed packages, run this with the venv activated then select the right kernel
in the notebook

(venv) $ ipython kernel install --name "local-venv-kernel" --user