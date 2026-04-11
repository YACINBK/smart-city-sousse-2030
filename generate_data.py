import os

import django
from django.core.management import call_command


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcity_backend.settings")
django.setup()


if __name__ == "__main__":
    call_command("generate_test_data")
