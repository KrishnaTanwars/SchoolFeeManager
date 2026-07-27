import sys
from pathlib import Path

# Add parent directory to sys.path so web_server can import models and controllers
base_dir = Path(__file__).resolve().parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from web_server import app

# Vercel WSGI entry point
app = app
