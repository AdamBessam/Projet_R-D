import os
import sys

# Ensure project root is on sys.path so tests can import `src` package
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Also allow importing modules using unqualified names (project uses some bare imports)
SRC_DIR = os.path.join(ROOT, "src")
if os.path.isdir(SRC_DIR) and SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
