# Steps for django project

create project folder (or just use github repo) \
`mkdir setlist_tracker` \
`cd setlist_tracker`

create virtual env \
`virtualenv env` \
`source env/bin/activate` \
`pi3p install django`

create django project \
`django-admin startproject setlist_tracker .` \
pst ( dont forget the dot ".") \

create data base \
`python manage.py migrate`

start server \
`python manage.py runserver`

create an app within the project \
`python manage.py startapp setlist_tracker_app`

folder structure should look like \
`ls setlist_tracker`
```
|-env
|-db.sqlite3
|-manage.py
|-setlist_tracker (main project)
|-setlist_tracker_app (main app)
```

define models in `setlist_tracker_app/models.py`

add app to project in `settings.py`
```
INSTALLED_APPS = [
    # my apps
    'setlist_tracker_app'

    ...
]
```

make migration files for new models \
`python manage.py makemigrations setlist_tracker_app`

apply migrations \
`python manage.py migrate`

create super user \
`python manage.py createsuperuser` \
`user: admin` \
`password hint: classic jazz`

register models with the admin site in `admin.py`

check out admin site to make sure things are working \
`http://localhost:8000/admin/`

add song tracker app urls file to main `urls.py` file
```
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('song_tracker_app.urls')),
]
```

create `urls.py` in song_tracker_app and add home page url pattern \

create new function in `setlist_tracker_app/views.py` to map url patterns to functions and templates \

create new folder to hold templates \
`mkdir setlist_tracker/setlist_tracker_app/templates/setlist_tracker_app` (is a little weird but thats the best structure to not confuse django) \


create new `index.html` file

create more hmtl files to view data on different pages

now we need to provide ways for user to enter their own data using forms

create new file `setlist_tracker_app/forms.py`

user djangos `forms.ModelForm` to automatically create forms from your defined models

create pages for deleting and editing songs and links

create new app for managing users  \ 
`python manage.py startapp users`

add `users` app to `settings.py`

include urls from `users` in url settings

add out of the box django user management urls to users/urls.py \
`django.contrib.auth.urls`

add folder `users/templates/registration`

add `login.html`

add login link to `base.html` with optional messaged based on authentication status

add logout link to `base.html`

add `logged_out.html` confirmation page

add `registration` url, view, and html

add `@login_required` decorator to any function which should require a login

add code to bottom of `settings` to redirect to login page whenever a non logged in user tries to access a restriced page
```
# My settings
LOGIN_URL = 'users:login'
```
add user field to song model

make migration on data base, will need to give a filler value for `owner` for the currently existing data \
`python manage.py makemigrations learning_logs`

run migrations \
`python manage.py migrate`

edit songs view so that it only retrieves results for the current user

add owner checks to make sure users dont manually enter urls that should not be accessible to them for any necessary views \
songs, edit_link, etc \
`raise Http404`

edit new_song view so that it assigns the current loged in user to the new song object

pip install django-bootstrap-v5

add bootstrap5 to apps in settings

