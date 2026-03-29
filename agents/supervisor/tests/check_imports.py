import sys
import os

# Add project root to sys.path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/")))

try:
    from supervisor.agent import create_supervisor_agent  # noqa: F401

    print("✅ Successfully imported create_supervisor_agent")

except Exception as e:
    print(f"❌ Failed to import: {e}")
    import traceback

    traceback.print_exc()
