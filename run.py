#!/usr/bin/env python3
"""
Run the Sports Performance Analysis Platform.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend.streamlit.app import main

if __name__ == "__main__":
    main()

