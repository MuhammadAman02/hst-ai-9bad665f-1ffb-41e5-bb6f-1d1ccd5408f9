#!/usr/bin/env python3
"""
Temple Run Game - Entry Point
A thrilling endless runner game built with NiceGUI
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import and run the game
from app.main import main

if __name__ == "__main__":
    main()