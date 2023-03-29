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
- make an editor for description rules next to the description rule box
- add a "divide" box for amount to compensate for things that will get split over venmo
  - what about adding things you've paid to other people on venmo???
  - Or things that were requested but not associated with a purchase?
- Add accounts, categories, subcategories, descriptions for categorized transaction seeding if they don't already exist in database
- Add tool tips for the different categories when going through the ledger process

# Helpful!

if your jypter notebook cant find the installed packages, run this with the venv activated then select the right kernel
in the notebook

(venv) $ ipython kernel install --name "local-venv-kernel" --user


# Category Updates
what would OPEN AI art be?

should categories/subcategories be connected to descriptions? That way the user can get category guesses with just
a descriptions file? This is the best if the logic for looking up categories stays the same
