import os
import sys
import time
from pathlib import Path

import django


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartcity_backend.settings")
django.setup()

from smartcity_backend.api.services import simulate_system_step


def simulate(pause_seconds=2):
    print("Starting real-time simulation. Press Ctrl+C to stop.")

    while True:
        try:
            summary = simulate_system_step()
            print(
                "[STEP] sensors={sensor_updates} trips={trips_created} "
                "interventions={interventions_created}".format(**summary)
            )
            time.sleep(pause_seconds)
        except KeyboardInterrupt:
            print("Simulation stopped.")
            break
        except Exception as exc:
            print(f"Simulation error: {exc}")
            time.sleep(5)


if __name__ == "__main__":
    simulate()
