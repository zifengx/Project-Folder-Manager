import os
import json
import tkinter as tk
from tkinter import filedialog

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
STRUCTURE_JSON = os.path.join(os.path.dirname(__file__), "structure.json")

def ensure_structure_json():
    if not os.path.exists(STRUCTURE_JSON):
        print(f"Structure file '{STRUCTURE_JSON}' does not exist. Please create it first.")
        exit(1)
    if os.path.getsize(STRUCTURE_JSON) == 0:
        print(f"Structure file '{STRUCTURE_JSON}' is empty. Please fill it with valid JSON structure.")
        exit(1)

def load_structure():
    with open(STRUCTURE_JSON, encoding="utf-8") as f:
        return json.load(f)

def create_items(base_path, items):
    for item in items:
        folder_path = os.path.join(base_path, item["name"])
        os.makedirs(folder_path, exist_ok=True)
        if "folders" in item:
            create_items(folder_path, item["folders"])

def select_directory_gui():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select parent directory for project")
    root.destroy()
    return folder_selected

def main():
    ensure_structure_json()
    structure = load_structure()

    parent_dir = select_directory_gui()
    if not parent_dir:
        print("No directory selected. Exiting.")
        return

    project_name = input("Enter project name: ").strip()
    if not project_name:
        print("Project name cannot be empty.")
        return
    project_path = os.path.join(parent_dir, project_name)
    if os.path.exists(project_path):
        print(f"Project '{project_name}' already exists.")
        return

    os.makedirs(project_path)
    create_items(project_path, structure.get("folders", []))

    # Create files
    for file_item in structure.get("files", []):
        file_path = os.path.join(project_path, file_item["name"])
        file_content = input(f"Enter content for {file_item['name']}: ")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)

    print(f"Project '{project_name}' structure created at {project_path}")

if __name__ == "__main__":
    main()
