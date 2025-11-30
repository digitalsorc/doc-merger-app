#!/usr/bin/env python3
"""
Markdown Merger - Application Entry Point

This is the main entry point for the Markdown Merger application.
Run this file to start the GUI application.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui import main

if __name__ == "__main__":
    main()
