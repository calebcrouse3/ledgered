build:
	@docker build -t ledgered-django-app ledgered

start:
	@docker run \
		--detach \
		-p 8000:8000 \
		-v $(PWD)/ledgered/ledgered_app:/ledgered/ledgered_app \
		-v $(PWD)/ledgered/db.sqlite3:/ledgered/db.sqlite3 \
		--name ledgered-django-app \
		ledgered-django-app
	@sleep 3
	@open http://127.0.0.1:8000/

stop:
	@docker stop ledgered-django-app
	@docker rm ledgered-django-app