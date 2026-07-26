import os
import sys

# Automatically locate and add local .venv packages if not present
venv_site_packages = os.path.abspath(os.path.join(os.path.dirname(__file__), ".venv", "Lib", "site-packages"))
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)