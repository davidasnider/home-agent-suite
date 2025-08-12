#!/usr/bin/env python3
"""
Demo script to run the Streamlit chatbot application

Usage:
    poetry run streamlit run demo_app.py

This script runs the main app.py through Streamlit with proper configuration.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Run the Streamlit app"""
    app_path = Path(__file__).parent / "app.py"

    # Run streamlit with the app
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Chatbot application stopped by user")
    except Exception as e:
        print(f"❌ Error running the application: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
