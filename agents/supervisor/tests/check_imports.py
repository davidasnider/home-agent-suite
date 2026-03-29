import sys
import os

# Add project root to sys.path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/")))

try:
    import supervisor.agent  # noqa: F401

    print(f"✅ Successfully imported {supervisor.agent.__name__}")

except Exception as e:
    print(f"❌ Failed to import: {e}")
    import traceback

    traceback.print_exc()
