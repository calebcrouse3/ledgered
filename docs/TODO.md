### Where you left off

### TODO List
- Nail down transaction processing logic. Make a runbook for ledgering!
  - Aggregation
  - Duplication
  - Updating
  - AUTH:
  - Transfers
- cascading dropdowns for subcategories not working because need to get categories only for current user
- ENUMs
  - define and enforce transaction and plugin types
  - single letter versus whole word
- File uploads
  - would be nice to have some error handing for a file upload that only uploads a portions of the transactions.
    - complete versus incomplete
  - Is there a way to fail when processing raw transaction df by only dropping a single row and not the whole data frame?
  - Maybe do everything like by line and without pandas? Even the aggregation? Or maybe just do as little as possible with pandas