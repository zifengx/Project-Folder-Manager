import sys
import os
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from core import ensure_structure_json, load_structure, create_project

def get_db_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "settings.db")
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.db")

def init_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS structure (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    json TEXT
                )''')
    conn.commit()
    conn.close()

def save_setting(key, value):
    db_path = get_db_path()
    import sqlite3
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def load_setting(key, default=None):
    db_path = get_db_path()
    import sqlite3
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return default

def save_structure_json(json_str):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO structure (id, json) VALUES (1, ?)", (json_str,))
    conn.commit()
    conn.close()

def load_structure_json():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT json FROM structure WHERE id=1")
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return row[0]
    # fallback: try to load from file if db is empty
    try:
        with open(get_structure_json_path(), "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return '{\n    "folders": [],\n    "files": []\n}'

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
    init_db()
    STRUCTURE_JSON = get_structure_json_path()
    try:
        ensure_structure_json(STRUCTURE_JSON)
    except Exception as e:
        tk.Tk().withdraw()
        messagebox.showerror("Error", str(e))
        return

    def update_parent_dir_label():
        parent_dir_label_var.set(f"Current Parent Directory:\n{parent_dir_var.get()}")

    def select_directory_menu():
        selected = filedialog.askdirectory(title="Select parent directory for project", initialdir=parent_dir_var.get())
        if selected:
            parent_dir_var.set(selected)
            save_setting("parent_dir", selected)
            update_parent_dir_label()

    def select_directory():
        select_directory_menu()

    def load_parent_dir(default_dir):
        path = load_setting("parent_dir", None)
        if path and os.path.isdir(path):
            return path
        return default_dir

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
        project_name_var.set("")  # Clear project name input

    def open_config_panel():
        import json
        def refresh_lists():
            folders_list.delete(0, tk.END)
            for folder in folders_data:
                folders_list.insert(tk.END, folder["name"])
            files_list.delete(0, tk.END)
            for file in files_data:
                files_list.insert(tk.END, file["name"])

        def add_folder():
            name = simple_input_dialog(config_win, "Enter new folder name:")
            if name:
                folders_data.append({"name": name})
                refresh_lists()

        def remove_folder():
            sel = folders_list.curselection()
            if sel:
                del folders_data[sel[0]]
                refresh_lists()

        def rename_folder():
            sel = folders_list.curselection()
            if sel:
                old_name = folders_data[sel[0]]["name"]
                name = simple_input_dialog(config_win, f"Rename folder '{old_name}' to:")
                if name:
                    folders_data[sel[0]]["name"] = name
                    refresh_lists()

        def add_file():
            name = simple_input_dialog(config_win, "Enter new txt file name (without extension):")
            if name:
                if not name.lower().endswith('.txt'):
                    name = f"{name}.txt"
                files_data.append({"name": name})
                refresh_lists()

        def remove_file():
            sel = files_list.curselection()
            if sel:
                del files_data[sel[0]]
                refresh_lists()

        def rename_file():
            sel = files_list.curselection()
            if sel:
                old_name = files_data[sel[0]]["name"]
                name = simple_input_dialog(config_win, f"Rename txt file '{old_name}' to (without extension):")
                if name:
                    if not name.lower().endswith('.txt'):
                        name = f"{name}.txt"
                    files_data[sel[0]]["name"] = name
                    refresh_lists()

        def save_structure():
            structure = {
                "folders": folders_data,
                "files": files_data
            }
            json_str = json.dumps(structure, indent=4)
            save_structure_json(json_str)
            messagebox.showinfo("Saved", "Structure saved successfully.")
            config_win.destroy()

        try:
            structure = json.loads(load_structure_json())
        except Exception:
            structure = {"folders": [], "files": []}
        folders_data = structure.get("folders", [])
        files_data = structure.get("files", [])

        config_win = tk.Toplevel(root)
        config_win.title("Edit Project Structure")
        config_win.geometry("500x400")

        tk.Label(config_win, text="Folders:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        folders_list = tk.Listbox(config_win, height=10, width=30)
        folders_list.grid(row=1, column=0, rowspan=4, padx=10, pady=5, sticky="n")
        tk.Button(config_win, text="Add", command=add_folder).grid(row=1, column=1, sticky="ew")
        tk.Button(config_win, text="Remove", command=remove_folder).grid(row=2, column=1, sticky="ew")
        tk.Button(config_win, text="Rename", command=rename_folder).grid(row=3, column=1, sticky="ew")

        # Rename "Files" to "Txt files"
        tk.Label(config_win, text="Txt files:").grid(row=5, column=0, padx=10, pady=(15,5), sticky="w")
        files_list = tk.Listbox(config_win, height=7, width=30)
        files_list.grid(row=6, column=0, rowspan=3, padx=10, pady=5, sticky="n")
        tk.Button(config_win, text="Add", command=add_file).grid(row=6, column=1, sticky="ew")
        tk.Button(config_win, text="Remove", command=remove_file).grid(row=7, column=1, sticky="ew")
        tk.Button(config_win, text="Rename", command=rename_file).grid(row=8, column=1, sticky="ew")

        tk.Button(config_win, text="Save", command=save_structure).grid(row=9, column=0, columnspan=2, pady=15)

        refresh_lists()

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

    # Panel to show current parent directory
    parent_dir_label_var = tk.StringVar()
    parent_dir_label = tk.Label(root, textvariable=parent_dir_label_var, justify="left", fg="blue")
    parent_dir_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 0), sticky="w")
    update_parent_dir_label()

    # Project Name widgets
    tk.Label(root, text="Project Name:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    project_name_var = tk.StringVar()
    tk.Entry(root, textvariable=project_name_var, width=40).grid(row=1, column=1, padx=10, pady=5)

    tk.Button(root, text="Create Project", command=create_project_gui).grid(row=2, column=1, pady=15)

    center_window(root)

    root.mainloop()

def load_structure(structure_json_path=None):
    import json
    try:
        return json.loads(load_structure_json())
    except Exception:
        return {"folders": [], "files": []}

def ensure_structure_json(structure_json_path=None):
    # Always valid if db is present, so just pass
    pass
