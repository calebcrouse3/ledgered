# ledgered
track your expenses, in a ledger

### where you left off
Fidelity file upload working

### TODO List
1. Find more graceful way to define and enforce the plugin types and transaction types (constants) and use them throughout
2. Find graceful way to enforce schemas of dataframe coming out of the plugin and going into data aggregation
3. Is there a way to fail when processing raw transaction df by only dropping a single row and not the whole data frame?
   4. Maybe do everything like by line and without pandas? Even the aggregation? Or maybe just do as little as possible with pandas
4. Find better way to do more error handling during file upload process
5. Figure out how to prevent data duplication for descriptions when seeding data

- revisit enums being a single letter versus a whole word and just yeah whats up with enums
- Make functionality to choose source of seeding data, either test data of default (caleb's) data

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

