import os
import json
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent.parent

with open(os.path.join(BASE_DIR, 'secrets.json')) as secrets_file:
    secrets = json.load(secrets_file)


def get_secret(setting, secret_in=secrets):
    try:
        return secret_in[setting]
    except KeyError:
        raise ImproperlyConfigured("Set the {} settings".format(settings))


DJANGO_MODULE_STR = get_secret('DJANGO_MODULE_STR')

if DJANGO_MODULE_STR == 'local':
    from .local_settings import *
else:
    from .production import *
