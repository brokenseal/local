import os
import sys

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
INCLUDE_PATHS = (
    PROJECT_PATH,
)

for path in INCLUDE_PATHS:
    if path not in sys.path:
        sys.path.insert(0, path)

if __name__ == "__main__":
    os.environ["DJANGO_SETTINGS_MODULE"] = "local.settings"

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
