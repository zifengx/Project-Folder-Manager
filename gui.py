import os
import tkinter as tk
from tkinter import filedialog, messagebox
from core import ensure_structure_json, load_structure, create_project

def run_app():
    try:
        ensure_structure_json()
    except Exception as e:
        tk.Tk().withdraw()
        messagebox.showerror("Error", str(e))
        return

    def select_directory():
        selected = filedialog.askdirectory(title="Select parent directory for project")
        if selected:
            parent_dir_var.set(selected)

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

    def file_content_callback(filename):
        return simple_input_dialog(root, f"Enter content for {filename}:")

    def create_project_gui():
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
        structure = load_structure()
        try:
            create_project(project_path, structure, file_content_callback)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        messagebox.showinfo("Success", f"Project '{project_name}' structure created at {project_path}")

    root = tk.Tk()
    root.title("Project Folder Manager")

    tk.Label(root, text="Project Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    project_name_var = tk.StringVar()
    tk.Entry(root, textvariable=project_name_var, width=40).grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Parent Directory:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    parent_dir_var = tk.StringVar()
    tk.Entry(root, textvariable=parent_dir_var, width=40, state="readonly").grid(row=1, column=1, padx=10, pady=5)
    tk.Button(root, text="Browse...", command=select_directory).grid(row=1, column=2, padx=5, pady=5)

    tk.Button(root, text="Create Project", command=create_project_gui).grid(row=2, column=1, pady=15)

    root.mainloop()
