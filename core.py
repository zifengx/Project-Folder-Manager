import os
import json

def ensure_structure_json(structure_json_path=None):
    if structure_json_path is None:
        structure_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "structure.json")
    if not os.path.exists(structure_json_path):
        raise FileNotFoundError(f"Structure file '{structure_json_path}' does not exist. Please create it first.")
    if os.path.getsize(structure_json_path) == 0:
        raise ValueError(f"Structure file '{structure_json_path}' is empty. Please fill it with valid JSON structure.")

def load_structure(structure_json_path=None):
    if structure_json_path is None:
        structure_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "structure.json")
    with open(structure_json_path, encoding="utf-8") as f:
        return json.load(f)

def create_items(base_path, items):
    for item in items:
        folder_path = os.path.join(base_path, item["name"])
        os.makedirs(folder_path, exist_ok=True)
        if "folders" in item:
            create_items(folder_path, item["folders"])

def create_project(project_path, structure, file_content_callback):
    os.makedirs(project_path)
    create_items(project_path, structure.get("folders", []))
    for file_item in structure.get("files", []):
        file_path = os.path.join(project_path, file_item["name"])
        content = file_item.get("content")
        if content is None:
            content = file_content_callback(file_item["name"])
            if content is None:
                content = ""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
