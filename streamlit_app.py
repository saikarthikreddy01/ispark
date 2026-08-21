import sys
from pathlib import Path
import runpy

# Ensure root directory is in sys.path
ROOT = Path(__file__).parent.resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Run main app entry point
runpy.run_path(str(ROOT / "app" / "app.py"), run_name="__main__")
