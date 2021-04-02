Usage:

```
poetry install
poetry run python3 -c "import django.core.management.utils as v; print(f'SECRET_KEY = \'{v.get_random_secret_key()}\'')" >> .env
```
