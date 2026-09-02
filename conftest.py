"""
pytest configuration and path setup.
Ensures the kdp_puzzle_book directory is on sys.path so imports work correctly.
"""
import sys
import os

# Add the project root (kdp_puzzle_book/) to sys.path
sys.path.insert(0, os.path.dirname(__file__))
