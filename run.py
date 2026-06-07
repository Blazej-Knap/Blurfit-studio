import sys
import os

# Add the current directory to sys.path to ensure proper package imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from blurfit_studio.app import main

if __name__ == "__main__":
    main()
