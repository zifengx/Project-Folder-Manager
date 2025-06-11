import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox

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

def create_project_gui():
    def select_directory():
        selected = filedialog.askdirectory(title="Select parent directory for project")
        if selected:
            parent_dir_var.set(selected)

    def create_project():
        parent_dir = parent_dir_var.get().strip()
        project_name = project_name_var.get().strip()
        if not parent_dir:
            messagebox.showerror("Error", "Please select a parent directory.")
            return
        if not project_name:
            messagebox.showerror("Error", "Project name cannot be empty.")
            return
        project_path = os.path.join(parent_dir, project_name)
        if os.path.exists(project_path):
            messagebox.showerror("Error", f"Project '{project_name}' already exists.")
            return

        os.makedirs(project_path)
        structure = load_structure()
        create_items(project_path, structure.get("folders", []))

        # Create files
        for file_item in structure.get("files", []):
            file_path = os.path.join(project_path, file_item["name"])
            content = ""
            if "content" in file_item:
                content = file_item["content"]
            else:
                content = simple_input_dialog(root, f"Enter content for {file_item['name']}:")
                if content is None:
                    content = ""
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

        messagebox.showinfo("Success", f"Project '{project_name}' structure created at {project_path}")

    def simple_input_dialog(parent, prompt):
        dialog = tk.Toplevel(parent)
        dialog.title("Input")
        tk.Label(dialog, text=prompt).pack(padx=10, pady=5)
        entry = tk.Entry(dialog, width=50)
        entry.pack(padx=10, pady=5)
        entry.focus_set()
        result = {"value": None}
        def on_ok():
            result["value"] = entry.get()
            dialog.destroy()
        tk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
        dialog.transient(parent)
        dialog.grab_set()
        parent.wait_window(dialog)
        return result["value"]

    root = tk.Tk()
    root.title("Project Folder Manager")

    tk.Label(root, text="Project Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    project_name_var = tk.StringVar()
    tk.Entry(root, textvariable=project_name_var, width=40).grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Parent Directory:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    parent_dir_var = tk.StringVar()
    tk.Entry(root, textvariable=parent_dir_var, width=40, state="readonly").grid(row=1, column=1, padx=10, pady=5)
    tk.Button(root, text="Browse...", command=select_directory).grid(row=1, column=2, padx=5, pady=5)

    tk.Button(root, text="Create Project", command=create_project).grid(row=2, column=1, pady=15)

    root.mainloop()

def main():
    ensure_structure_json()
    create_project_gui()

if __name__ == "__main__":
    main()
