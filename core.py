import os
import json

STRUCTURE_JSON = os.path.join(os.path.dirname(__file__), "structure.json")

def ensure_structure_json():
    if not os.path.exists(STRUCTURE_JSON):
        raise FileNotFoundError(f"Structure file '{STRUCTURE_JSON}' does not exist. Please create it first.")
    if os.path.getsize(STRUCTURE_JSON) == 0:
        raise ValueError(f"Structure file '{STRUCTURE_JSON}' is empty. Please fill it with valid JSON structure.")

def load_structure():
    with open(STRUCTURE_JSON, encoding="utf-8") as f:
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
