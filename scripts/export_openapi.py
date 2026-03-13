"""Export the FastAPI OpenAPI spec to openapi/openapi.json.

The Supabase client is lazy (only initialized on the first request), so
setting dummy env vars is enough to import the app without a real Supabase
instance.
"""

import json
import os
import sys
from pathlib import Path

# Must be set before importing any qxilt module so Pydantic Settings can load.
os.environ.setdefault("SUPABASE_URL", "http://localhost:54321")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "dummy")

# Allow running as `python scripts/export_openapi.py` from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qxilt.api.main import app  # noqa: E402

OUTPUT = Path(__file__).resolve().parent.parent / "openapi" / "openapi.json"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

spec = app.openapi()
with OUTPUT.open("w") as f:
    json.dump(spec, f, indent=2)
    f.write("\n")

print(f"OpenAPI spec written to {OUTPUT}")
