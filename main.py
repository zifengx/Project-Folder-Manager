import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json

APP_NAME = "Project Folder Manager"
VERSION = "1.1.1"
APP_TITLE = f"{APP_NAME} v{VERSION}"

# Use a persistent structure file in the exe/script directory
if getattr(sys, 'frozen', False):
    PROGRAM_ROOT = os.path.dirname(sys.executable)
else:
    PROGRAM_ROOT = os.path.dirname(os.path.abspath(__file__))

STRUCTURE_FILENAME = "project_folder_structure.json"
STRUCTURE_JSON = os.path.join(PROGRAM_ROOT, STRUCTURE_FILENAME)

# --- Structure logic ---
def ensure_structure_json():
    import tempfile
    temp_json = os.path.join(tempfile.gettempdir(), STRUCTURE_FILENAME)
    # Try to get from PyInstaller bundle if running as frozen
    bundled_json = None
    if getattr(sys, 'frozen', False):
        bundled_json = os.path.join(sys._MEIPASS, STRUCTURE_FILENAME)

    def try_copy(src_path, dst_path):
        with open(src_path, "r", encoding="utf-8") as src, open(dst_path, "w", encoding="utf-8") as dst:
            dst.write(src.read())

    if not os.path.exists(STRUCTURE_JSON):
        # 1. Try PyInstaller bundle
        if bundled_json and os.path.exists(bundled_json):
            try_copy(bundled_json, STRUCTURE_JSON)
            return
        # 2. Try TEMP folder
        if os.path.exists(temp_json):
            try_copy(temp_json, STRUCTURE_JSON)
            return
        # 3. Not found
        raise FileNotFoundError(f"Structure file '{STRUCTURE_JSON}' does not exist and was not found in PyInstaller bundle or TEMP folder. Please provide it.")
    if os.path.getsize(STRUCTURE_JSON) == 0:
        # 1. Try PyInstaller bundle
        if bundled_json and os.path.exists(bundled_json):
            try_copy(bundled_json, STRUCTURE_JSON)
            return
        # 2. Try TEMP folder
        if os.path.exists(temp_json):
            try_copy(temp_json, STRUCTURE_JSON)
            return
        # 3. Not found
        raise ValueError(f"Structure file '{STRUCTURE_JSON}' is empty and was not found in PyInstaller bundle or TEMP folder. Please provide it.")

def load_structure():
    with open(STRUCTURE_JSON, encoding="utf-8") as f:
        return json.load(f)

def create_items(base_path, items):
    for item in items:
        folder_path = os.path.join(base_path, item["name"])
        os.makedirs(folder_path, exist_ok=True)
        if "folders" in item:
            create_items(folder_path, item["folders"])

def create_project(project_path, structure):
    os.makedirs(project_path)
    create_items(project_path, structure.get("folders", []))
    for file_item in structure.get("files", []):
        file_path = os.path.join(project_path, file_item["name"])
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")

# --- GUI logic ---
def run_app():
    root = tk.Tk()
    root.title(APP_TITLE)
    try:
        ensure_structure_json()
    except Exception as e:
        root.withdraw()
        messagebox.showerror("Error", str(e))
        return

    def load_parent_dir():
        try:
            struct = load_structure()
            return struct.get("parent_directory", PROGRAM_ROOT)
        except Exception:
            return PROGRAM_ROOT

    def save_parent_dir(path):
        try:
            struct = load_structure()
            struct["parent_directory"] = path
            with open(STRUCTURE_JSON, "w", encoding="utf-8") as f:
                json.dump(struct, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save parent directory: {e}")

    def create_project_gui():
        parent_dir = load_parent_dir().strip()
        project_name = project_name_var.get().strip()
        notice_var.set("")
        if not parent_dir:
            parent_dir = PROGRAM_ROOT
        if not project_name:
            messagebox.showerror("Error", "Project name cannot be empty.")
            return
        project_path = os.path.join(parent_dir, project_name)
        if os.path.exists(project_path):
            messagebox.showerror("Error", f"Project '{project_name}' already exists.")
            return
        structure = load_structure()
        try:
            create_project(project_path, structure)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        notice_var.set(f"Project '{project_name}' Created!")

    # --- Config/Structure Editor Panel (in main window) ---
    from tkinter import ttk
    def load_structure_json():
        try:
            with open(STRUCTURE_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"folders": [], "files": []}
    def save_structure_json(struct):
        with open(STRUCTURE_JSON, "w", encoding="utf-8") as f:
            json.dump(struct, f, indent=4)
    def refresh_tree():
        tree.delete(*tree.get_children())
        def insert_items(parent, items, is_folder):
            for item in items:
                comment = item.get("comment", "")
                node = tree.insert(parent, "end", text=item["name"], open=True, values=("Folder" if is_folder else "File", comment))
                if is_folder and "folders" in item:
                    insert_items(node, item["folders"], True)
        struct = load_structure_json()
        insert_items("", struct.get("folders", []), True)
        insert_items("", struct.get("files", []), False)
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
        dialog.update_idletasks()
        width, height = 400, 120
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        parent.wait_window(dialog)
        return result["value"]
    def name_comment_dialog(parent, title, name_label, comment_label):
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        tk.Label(dialog, text=name_label).pack(padx=10, pady=(10, 2), anchor="w")
        name_entry = tk.Entry(dialog, width=50)
        name_entry.pack(padx=10, pady=(0, 8))
        tk.Label(dialog, text=comment_label).pack(padx=10, pady=(0, 2), anchor="w")
        comment_entry = tk.Entry(dialog, width=50)
        comment_entry.pack(padx=10, pady=(0, 10))
        name_entry.focus_set()
        result = {"name": None, "comment": None}
        def on_ok():
            result["name"] = name_entry.get()
            result["comment"] = comment_entry.get()
            dialog.destroy()
        tk.Button(dialog, text="OK", command=on_ok).pack(pady=(0, 10))
        dialog.transient(parent)
        dialog.grab_set()
        dialog.update_idletasks()
        width, height = 400, 200
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        parent.wait_window(dialog)
        return result["name"], result["comment"]
    def add_folder():
        selected = tree.focus()
        name, comment = name_comment_dialog(root, "Add Folder", "Folder name:", "Comment (optional):")
        if not name:
            return
        struct = load_structure_json()
        def add_to(items):
            folder = {"name": name, "folders": []}
            if comment:
                folder["comment"] = comment
            items.append(folder)
        if not selected:
            add_to(struct["folders"])
        else:
            def find_and_add(items, node):
                for item in items:
                    if item["name"] == tree.item(node, "text"):
                        if "folders" not in item:
                            item["folders"] = []
                        add_to(item["folders"])
                        return True
                    if "folders" in item and find_and_add(item["folders"], node):
                        return True
                return False
            find_and_add(struct["folders"], selected)
        save_structure_json(struct)
        refresh_tree()
    def add_file():
        name, comment = name_comment_dialog(root, "Add File", "File name (with suffix):", "Comment (optional):")
        if not name:
            return
        struct = load_structure_json()
        file_obj = {"name": name}
        if comment:
            file_obj["comment"] = comment
        struct["files"].append(file_obj)
        save_structure_json(struct)
        refresh_tree()
    def remove_item():
        selected = tree.focus()
        if not selected:
            return
        name = tree.item(selected, "text")
        kind = tree.item(selected, "values")[0]
        struct = load_structure_json()
        if kind == "Folder":
            def remove_from(items):
                for i, item in enumerate(items):
                    if item["name"] == name:
                        del items[i]
                        return True
                    if "folders" in item and remove_from(item["folders"]):
                        return True
                return False
            remove_from(struct["folders"])
        else:
            struct["files"] = [f for f in struct["files"] if f["name"] != name]
        save_structure_json(struct)
        refresh_tree()
    def reset_to_saved():
        refresh_tree()
        text.delete("1.0", tk.END)
        with open(STRUCTURE_JSON, "r", encoding="utf-8") as f:
            text.insert(tk.END, f.read())
    def save_from_json():
        try:
            new_json = text.get("1.0", tk.END)
            parsed = json.loads(new_json)
            save_structure_json(parsed)
            messagebox.showinfo("Saved", "Structure saved successfully.")
            refresh_tree()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")
    config_frame = tk.LabelFrame(root, text="Config", padx=5, pady=5)
    config_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    config_frame.columnconfigure(0, weight=1)
    config_frame.rowconfigure(0, weight=1)
    pd_frame = tk.Frame(config_frame)
    struct = load_structure_json()
    pd_value = struct.get("parent_directory", "").strip() or PROGRAM_ROOT
    pd_var = tk.StringVar(value=pd_value)
    pd_label = tk.Label(pd_frame, text="Parent Directory:")
    pd_label.pack(side=tk.LEFT, padx=(0,5))
    pd_entry = tk.Entry(pd_frame, textvariable=pd_var, width=80, state="readonly")
    pd_entry.pack(side=tk.LEFT, padx=(0,5))
    def browse_parent_dir():
        selected = filedialog.askdirectory(title="Select parent directory", initialdir=pd_var.get())
        if selected:
            pd_var.set(selected)
            try:
                struct = load_structure_json()
                struct["parent_directory"] = selected
                save_structure_json(struct)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save parent directory: {e}")
    tk.Button(pd_frame, text="Browse...", command=browse_parent_dir).pack(side=tk.LEFT)
    pd_frame.pack(pady=5, anchor="w")
    structure_frame = tk.LabelFrame(config_frame, text="Folder Structure", padx=5, pady=5)
    structure_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    notebook = ttk.Notebook(structure_frame)
    visual_frame = tk.Frame(notebook)
    tree = ttk.Treeview(visual_frame, columns=("Type", "Comment"), show="tree headings")
    tree.heading("#0", text="Name")
    tree.heading("Type", text="Type")
    tree.heading("Comment", text="Comment")
    tree.column("#0", width=120, anchor="w")
    tree.column("Type", width=60, anchor="center")
    tree.column("Comment", width=320, anchor="w")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    btn_frame = tk.Frame(visual_frame)
    tk.Button(btn_frame, text="Add Folder", command=add_folder).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Add File", command=add_file).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Remove Selected", command=remove_item).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Reset", command=reset_to_saved).pack(side=tk.LEFT, padx=5)
    btn_frame.pack(pady=5)
    visual_frame.pack(fill=tk.BOTH, expand=True)
    json_frame = tk.Frame(notebook)
    text = scrolledtext.ScrolledText(json_frame, wrap=tk.WORD, width=70, height=15)
    try:
        with open(STRUCTURE_JSON, "r", encoding="utf-8") as f:
            text.insert(tk.END, f.read())
    except Exception:
        text.insert(tk.END, '{\n    "folders": [],\n    "files": []\n}')
    text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    btn_row = tk.Frame(json_frame)
    tk.Button(btn_row, text="Save", command=save_from_json).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_row, text="Reset", command=reset_to_saved).pack(side=tk.LEFT, padx=5)
    btn_row.pack(pady=10)
    notebook.add(visual_frame, text="Visual Editor")
    notebook.add(json_frame, text="Raw JSON")
    notebook.pack(fill=tk.BOTH, expand=True)
    refresh_tree()
    config_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    root.grid_rowconfigure(1, weight=1)
    for col in range(4):
        root.grid_columnconfigure(col, weight=1)
    config_frame.grid_propagate(True)
    config_frame.pack_propagate(True)
    config_frame.rowconfigure(1, weight=1)
    config_frame.columnconfigure(0, weight=1)
    notebook.pack(fill=tk.BOTH, expand=True)
    def center_window(win, width=800, height=600):
        win.update_idletasks()
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")
    tk.Label(root, text="Project Name:").grid(row=0, column=0, padx=(10,0), pady=10, sticky="w")
    project_name_var = tk.StringVar()
    tk.Entry(root, textvariable=project_name_var, width=40).grid(row=0, column=1, padx=(0,0), pady=10, sticky="w")
    tk.Button(root, text="Create Project", command=create_project_gui).grid(row=0, column=2, padx=(4,0), pady=10, sticky="w")
    notice_var = tk.StringVar(value=" ")
    notice_label = tk.Label(root, textvariable=notice_var, fg="green", width=24, anchor="w")
    notice_label.grid(row=0, column=3, padx=(10,10), pady=10, sticky="w")
    center_window(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()
