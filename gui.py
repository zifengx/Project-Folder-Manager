import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from core import ensure_structure_json, load_structure, create_project

def get_structure_json_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "structure.json")
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "structure.json")

def get_parent_dir_config_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "parent_dir.cfg")
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "parent_dir.cfg")

def load_parent_dir(default_dir):
    config_path = get_parent_dir_config_path()
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            path = f.read().strip()
            if path and os.path.isdir(path):
                return path
    return default_dir

def save_parent_dir(path):
    config_path = get_parent_dir_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(path)

PROGRAM_ROOT = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

def run_app():
    STRUCTURE_JSON = get_structure_json_path()
    try:
        ensure_structure_json(STRUCTURE_JSON)
    except Exception as e:
        tk.Tk().withdraw()
        messagebox.showerror("Error", str(e))
        return

    def select_directory_menu():
        selected = filedialog.askdirectory(title="Select parent directory for project", initialdir=parent_dir_var.get())
        if selected:
            parent_dir_var.set(selected)
            save_parent_dir(selected)

    def select_directory():
        # This can just call the menu version for consistency
        select_directory_menu()

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
        # Center the dialog
        dialog.update_idletasks()
        width, height = 400, 120
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
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

    def open_config_panel():
        def save_structure():
            try:
                new_json = text.get("1.0", tk.END)
                import json
                parsed = json.loads(new_json)
                with open(STRUCTURE_JSON, "w", encoding="utf-8") as f:
                    f.write(json.dumps(parsed, indent=4))
                messagebox.showinfo("Saved", "Structure saved successfully.")
                config_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid JSON: {e}")

        config_win = tk.Toplevel(root)
        config_win.title("Edit Project Structure")
        config_win.geometry("600x500")
        tk.Label(config_win, text="Edit the folder structure JSON below:").pack(pady=5)
        text = scrolledtext.ScrolledText(config_win, wrap=tk.WORD, width=70, height=25)
        try:
            with open(STRUCTURE_JSON, "r", encoding="utf-8") as f:
                text.insert(tk.END, f.read())
        except Exception:
            text.insert(tk.END, '{\n    "folders": [],\n    "files": []\n}')
        text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        tk.Button(config_win, text="Save", command=save_structure).pack(pady=10)

    root = tk.Tk()
    root.title("Project Folder Manager")

    # Add menu for config and parent directory
    menubar = tk.Menu(root)
    config_menu = tk.Menu(menubar, tearoff=0)
    config_menu.add_command(label="Edit Structure...", command=open_config_panel)
    menubar.add_cascade(label="Config", menu=config_menu)

    parent_dir_menu = tk.Menu(menubar, tearoff=0)
    parent_dir_menu.add_command(label="Set Parent Directory...", command=select_directory_menu)
    menubar.add_cascade(label="Parent Directory", menu=parent_dir_menu)

    root.config(menu=menubar)

    # Center the window after widgets are created
    def center_window(win, width=500, height=180):
        win.update_idletasks()
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    parent_dir_var = tk.StringVar()
    parent_dir_var.set(load_parent_dir(PROGRAM_ROOT))

    # Parent Directory widgets at the top (remove label, entry, button)
    # tk.Label(root, text="Parent Directory:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    # tk.Entry(root, textvariable=parent_dir_var, width=40, state="readonly").grid(row=0, column=1, padx=10, pady=5)
    # tk.Button(root, text="Browse...", command=select_directory).grid(row=0, column=2, padx=5, pady=5)

    # Project Name widgets move up
    tk.Label(root, text="Project Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    project_name_var = tk.StringVar()
    tk.Entry(root, textvariable=project_name_var, width=40).grid(row=0, column=1, padx=10, pady=5)

    tk.Button(root, text="Create Project", command=create_project_gui).grid(row=1, column=1, pady=15)

    center_window(root)

    root.mainloop()
