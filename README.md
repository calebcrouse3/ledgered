# ledgered
track your expenses, in a ledger

### where you left off

- seeding entries from csv file. not working yet

### TODO List
- create function to generate test entries
- create plugin for chase credit card
- make field entry_type for Model entry an enum
- Make functionality to choose source of seeding data, either test data of default (calebs) data
- get small samples of raw data transactions for resources where those raw transactions are not in the test entries data


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

