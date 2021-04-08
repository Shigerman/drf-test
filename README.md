# drf-test
A test drive of Django Rest Framework.

### instruments used
* Python
* Django
* Django Rest Framework
* Poetry for virtual environment
* python-dotenv for .venv file handling

### App structure

Objects:
* users
* items

Actions:
* user can be created
* user can authenticate and get auth token
* item can be created and deleted by user
* user can see a list of their items
* a user can send an item to another user

### installing
```
python3 -m pip install poetry
poetry install
poetry run python3 -c "import django.core.management.utils as v; print(f'SECRET_KEY = \'{v.get_random_secret_key()}\'')" >> .env
echo "RELEASE=1" >> .env
poetry run python3 manage.py migrate
poetry run python3 manage.py runserver
```

### testing
```
poetry run python3 manage.py test
```
