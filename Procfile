web: gunicorn pools.wsgi
release: python manage.py makemigrations
release: python manage.py migrate

release: python manage.py collectstatic --noinput
