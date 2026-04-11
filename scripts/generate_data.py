import os
import sys
from pathlib import Path

import django
from django.core.management import call_command


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcity_backend.settings")
django.setup()


if __name__ == "__main__":
    call_command("generate_test_data")
