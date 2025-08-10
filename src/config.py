"""
Project Folder Manager - Configuration and Constants
"""
import sys
import os

# Application metadata
APP_NAME = "Project Folder Manager"
VERSION = "3.1.4"
APP_TITLE = f"{APP_NAME} v{VERSION}"

# Paths
if getattr(sys, 'frozen', False):
    PROGRAM_ROOT = os.path.dirname(sys.executable)
else:
    PROGRAM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STRUCTURE_FILENAME = "project_folder_structure.json"
STRUCTURE_JSON = os.path.join(PROGRAM_ROOT, STRUCTURE_FILENAME)
PROJECT_LISTS_FILE = os.path.join(PROGRAM_ROOT, "project_lists.json")

# UI Constants
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 700
MIN_WIDTH = 900
MIN_HEIGHT = 600

# Project status constants
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_OPTIONS = [STATUS_ACTIVE, STATUS_INACTIVE]
