build:
	@docker build -t ledgered-django-app ledgered_parent

start:
	@docker run \
		-it \
		-p 8000:8000 \
		-v $(PWD)/ledgered_parent/ledgered_app:/ledgered_parent/ledgered_app \
		-v $(PWD)/ledgered_parent/db.sqlite3:/ledgered_parent/db.sqlite3 \
		--name ledgered-django-app \
		ledgered-django-app

stop:
	@docker stop ledgered-django-app
	@docker rm ledgered-django-app