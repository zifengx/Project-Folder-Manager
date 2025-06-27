import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json

APP_NAME = "Project Folder Manager"
VERSION = "2.0.1"
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
    import json
    from tkinter import ttk
    root = tk.Tk()
    root.title(APP_TITLE)
    # Set fixed window size and disable resizing
    fixed_width = 1400
    fixed_height = 640
    root.geometry(f"{fixed_width}x{fixed_height}")
    root.resizable(False, False)
    try:
        ensure_structure_json()
    except Exception as e:
        root.withdraw()
        messagebox.showerror("Error", str(e))
        return

    # --- Project List Management ---
    PROJECT_LISTS_FILE = os.path.join(PROGRAM_ROOT, "project_lists.json")
    DEFAULT_PROJECT_LISTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project_lists.json")

    def load_project_list():
        # If not found in PROGRAM_ROOT, try to copy from bundled or default location
        if not os.path.exists(PROJECT_LISTS_FILE):
            # If running as frozen, try to copy from the bundled location
            try:
                if getattr(sys, 'frozen', False):
                    import shutil
                    src = os.path.join(sys._MEIPASS, "project_lists.json")
                    if os.path.exists(src):
                        shutil.copyfile(src, PROJECT_LISTS_FILE)
                # If not frozen or not found, try to copy from script dir
                elif os.path.exists(DEFAULT_PROJECT_LISTS_FILE):
                    import shutil
                    shutil.copyfile(DEFAULT_PROJECT_LISTS_FILE, PROJECT_LISTS_FILE)
            except Exception:
                pass
        if os.path.exists(PROJECT_LISTS_FILE):
            try:
                with open(PROJECT_LISTS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_project_list(projects):
        with open(PROJECT_LISTS_FILE, "w", encoding="utf-8") as f:
            json.dump(projects, f, indent=2)

    def get_next_project_id(projects):
        if not projects:
            return 1
        return max(p.get("id", 0) for p in projects) + 1

    # --- Main Area (left) ---
    main_frame = tk.Frame(root)
    main_frame.grid(row=0, column=0, sticky="nsew", padx=(10,0), pady=10)
    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # --- Right Area: Project List (Visual Editor + Raw JSON) ---
    right_frame = tk.Frame(root, width=480)
    right_frame.grid(row=0, column=1, rowspan=10, sticky="nswe", padx=(10,10), pady=10)
    right_frame.grid_propagate(False)
    proj_labelframe = tk.LabelFrame(right_frame, text="Project List", padx=5, pady=5)
    proj_labelframe.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    project_notebook = ttk.Notebook(proj_labelframe)
    # --- Visual Editor Tab ---
    visual_proj_frame = tk.Frame(project_notebook)
    proj_tree = ttk.Treeview(visual_proj_frame, columns=("ID", "Name", "Description", "Status"), show="headings")
    proj_tree.heading("ID", text="ID")
    proj_tree.heading("Name", text="Name")
    proj_tree.heading("Description", text="Description")
    proj_tree.heading("Status", text="Status")
    proj_tree.column("ID", width=40, anchor="center")
    proj_tree.column("Name", width=140, anchor="w")
    proj_tree.column("Description", width=220, anchor="w")
    proj_tree.column("Status", width=100, anchor="center")
    proj_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def refresh_project_tree():
        proj_tree.delete(*proj_tree.get_children())
        # Sort projects in descending order by ID
        projects = sorted(load_project_list(), key=lambda p: p.get("id", 0), reverse=True)
        for proj in projects:
            values = (proj.get("id", ""), proj.get("name", ""), proj.get("description", ""), proj.get("status", ""))
            if proj.get("status", "") == "depredcated":
                proj_tree.insert("", tk.END, values=values, tags=("deprecated",))
            else:
                proj_tree.insert("", tk.END, values=values)
        proj_tree.tag_configure("deprecated", foreground="#888888", font=("Arial", 10, "overstrike"))

    def edit_project_dialog(parent, proj):
        dialog = tk.Toplevel(parent)
        dialog.title(f"Edit Project: {proj['name']}")
        tk.Label(dialog, text="Name:").grid(row=0, column=0, sticky="e", padx=8, pady=4)
        name_var = tk.StringVar(value=proj["name"])
        tk.Entry(dialog, textvariable=name_var, width=40).grid(row=0, column=1, padx=8, pady=4)
        tk.Label(dialog, text="Description:").grid(row=1, column=0, sticky="e", padx=8, pady=4)
        desc_var = tk.StringVar(value=proj.get("description", ""))
        tk.Entry(dialog, textvariable=desc_var, width=40).grid(row=1, column=1, padx=8, pady=4)
        tk.Label(dialog, text="Status:").grid(row=2, column=0, sticky="e", padx=8, pady=4)
        status_var = tk.StringVar(value=proj.get("status", "active"))
        status_options = ["active", "depredcated"]
        status_menu = ttk.Combobox(dialog, textvariable=status_var, values=status_options, state="readonly", width=18)
        status_menu.grid(row=2, column=1, padx=8, pady=4, sticky="w")
        result = {"ok": False}
        def on_ok():
            result["ok"] = True
            dialog.destroy()
        tk.Button(dialog, text="Save", command=on_ok).grid(row=3, column=0, columnspan=2, pady=10)
        dialog.transient(parent)
        dialog.grab_set()
        # Center the dialog on the parent window
        dialog.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        dialog_w = dialog.winfo_width()
        dialog_h = dialog.winfo_height()
        x = parent_x + (parent_w // 2) - (dialog_w // 2)
        y = parent_y + (parent_h // 2) - (dialog_h // 2)
        dialog.geometry(f"+{x}+{y}")
        dialog.wait_window()
        if result["ok"]:
            return {
                "id": proj["id"],
                "name": name_var.get().strip(),
                "description": desc_var.get().strip(),
                "status": status_var.get().strip()
            }
        return None

    def on_edit_project():
        selected = proj_tree.focus()
        if not selected:
            messagebox.showinfo("Edit Project", "Please select a project to edit.")
            return
        values = proj_tree.item(selected, "values")
        if not values:
            return
        proj_id = int(values[0])
        projects = load_project_list()
        for i, proj in enumerate(projects):
            if proj["id"] == proj_id:
                updated = edit_project_dialog(right_frame, proj)
                if updated:
                    projects[i] = updated
                    save_project_list(projects)
                    refresh_project_tree()
                    refresh_project_json()
                break

    btn_proj_frame = tk.Frame(visual_proj_frame)
    tk.Button(btn_proj_frame, text="Edit Selected", command=on_edit_project).pack(side=tk.LEFT, padx=5)

    def on_remove_project():
        selected = proj_tree.focus()
        if not selected:
            messagebox.showinfo("Remove Project", "Please select a project to remove.")
            return
        values = proj_tree.item(selected, "values")
        if not values:
            return
        proj_id = int(values[0])
        projects = load_project_list()
        for i, proj in enumerate(projects):
            if proj["id"] == proj_id:
                # Custom confirmation dialog centered over parent
                dialog = tk.Toplevel(right_frame)
                dialog.title("Remove Project")
                tk.Label(dialog, text=f"Are you sure you want to remove project '{proj['name']}'?").pack(padx=18, pady=16)
                result = {"ok": False}
                def on_yes():
                    result["ok"] = True
                    dialog.destroy()
                def on_no():
                    dialog.destroy()
                btns = tk.Frame(dialog)
                tk.Button(btns, text="Yes", command=on_yes, width=10).pack(side=tk.LEFT, padx=8)
                tk.Button(btns, text="No", command=on_no, width=10).pack(side=tk.LEFT, padx=8)
                btns.pack(pady=(0,12))
                dialog.transient(right_frame)
                dialog.grab_set()
                dialog.update_idletasks()
                parent_x = right_frame.winfo_rootx()
                parent_y = right_frame.winfo_rooty()
                parent_w = right_frame.winfo_width()
                parent_h = right_frame.winfo_height()
                dialog_w = dialog.winfo_width()
                dialog_h = dialog.winfo_height()
                x = parent_x + (parent_w // 2) - (dialog_w // 2)
                y = parent_y + (parent_h // 2) - (dialog_h // 2)
                dialog.geometry(f"+{x}+{y}")
                dialog.wait_window()
                if result["ok"]:
                    del projects[i]
                    save_project_list(projects)
                    refresh_project_tree()
                    refresh_project_json()
                break

    tk.Button(btn_proj_frame, text="Remove Selected", command=on_remove_project).pack(side=tk.LEFT, padx=5)
    btn_proj_frame.pack(pady=(0,8))
    visual_proj_frame.pack(fill=tk.BOTH, expand=True)

    # --- Raw JSON Tab ---
    json_proj_frame = tk.Frame(project_notebook)
    proj_text = scrolledtext.ScrolledText(json_proj_frame, wrap=tk.WORD, width=60, height=18)
    proj_text.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)

    def refresh_project_json():
        try:
            with open(PROJECT_LISTS_FILE, "r", encoding="utf-8") as f:
                proj_text.delete("1.0", tk.END)
                proj_text.insert(tk.END, f.read())
        except Exception:
            proj_text.delete("1.0", tk.END)
            proj_text.insert(tk.END, "[]")

    def save_project_json():
        try:
            new_json = proj_text.get("1.0", tk.END)
            parsed = json.loads(new_json)
            save_project_list(parsed)
            refresh_project_tree()
            messagebox.showinfo("Saved", "Project list saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")

    btn_json_proj = tk.Frame(json_proj_frame)
    tk.Button(btn_json_proj, text="Save", command=save_project_json).pack(side=tk.LEFT, padx=5)
    btn_json_proj.pack(pady=(0,8))
    json_proj_frame.pack(fill=tk.BOTH, expand=True)

    project_notebook.add(visual_proj_frame, text="Visual Editor")
    project_notebook.add(json_proj_frame, text="Raw JSON")
    project_notebook.pack(fill=tk.BOTH, expand=True)

    def refresh_projects_all():
        refresh_project_tree()
        refresh_project_json()
    refresh_projects_all()

    # --- Config/Structure Editor Panel (in main window) ---

    # --- Structure Editor Helper Functions ---
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

    def add_folder():
        selected = tree.focus()
        name = simple_input_dialog(root, "Enter folder name:")
        if not name:
            return
        struct = load_structure_json()
        def add_to(items):
            items.append({"name": name, "folders": []})
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
        name = simple_input_dialog(root, "Enter file name (with extension):")
        if not name:
            return
        struct = load_structure_json()
        struct["files"].append({"name": name})
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

    config_frame = tk.LabelFrame(main_frame, text="Config", padx=5, pady=5)
    config_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    config_frame.columnconfigure(0, weight=1)
    config_frame.rowconfigure(0, weight=1)
    pd_frame = tk.Frame(config_frame)
    struct = load_structure()
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
                struct = load_structure()
                struct["parent_directory"] = selected
                with open(STRUCTURE_JSON, "w", encoding="utf-8") as f:
                    json.dump(struct, f, indent=2)
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

    def edit_tree_item(event):
        selected = tree.focus()
        if not selected:
            return
        name = tree.item(selected, "text")
        values = tree.item(selected, "values")
        kind = values[0] if values else ""
        comment = values[1] if len(values) > 1 else ""
        # Dialog for editing name and comment
        dialog = tk.Toplevel(visual_frame)
        dialog.title(f"Edit {kind}")
        tk.Label(dialog, text="Name:").grid(row=0, column=0, padx=8, pady=6, sticky="e")
        name_var = tk.StringVar(value=name)
        tk.Entry(dialog, textvariable=name_var, width=48).grid(row=0, column=1, padx=8, pady=6)
        tk.Label(dialog, text="Comment:").grid(row=1, column=0, padx=8, pady=6, sticky="e")
        comment_var = tk.StringVar(value=comment)
        tk.Entry(dialog, textvariable=comment_var, width=48).grid(row=1, column=1, padx=8, pady=6)
        result = {"ok": False}
        def on_ok():
            result["ok"] = True
            dialog.destroy()
        tk.Button(dialog, text="Save", command=on_ok).grid(row=2, column=0, columnspan=2, pady=10)
        dialog.transient(visual_frame)
        dialog.grab_set()
        dialog.update_idletasks()
        # Center the dialog in the middle of the Folder Structure area (visual_frame)
        parent_x = visual_frame.winfo_rootx()
        parent_y = visual_frame.winfo_rooty()
        parent_w = visual_frame.winfo_width()
        parent_h = visual_frame.winfo_height()
        dialog_w = dialog.winfo_width()
        dialog_h = dialog.winfo_height()
        x = parent_x + (parent_w // 2) - (dialog_w // 2)
        y = parent_y + (parent_h // 2) - (dialog_h // 2)
        dialog.geometry(f"+{x}+{y}")
        dialog.wait_window()
        if not result["ok"]:
            return
        new_name = name_var.get().strip()
        new_comment = comment_var.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return
        # Update structure JSON
        struct = load_structure_json()
        def update_item(items):
            for item in items:
                if item["name"] == name:
                    item["name"] = new_name
                    if new_comment:
                        item["comment"] = new_comment
                    elif "comment" in item:
                        del item["comment"]
                    return True
                if "folders" in item and update_item(item["folders"]):
                    return True
            return False
        found = False
        if kind == "Folder":
            found = update_item(struct["folders"])
        elif kind == "File":
            for file_item in struct["files"]:
                if file_item["name"] == name:
                    file_item["name"] = new_name
                    if new_comment:
                        file_item["comment"] = new_comment
                    elif "comment" in file_item:
                        del file_item["comment"]
                    found = True
                    break
        if found:
            save_structure_json(struct)
            refresh_tree()
        else:
            messagebox.showerror("Error", "Could not update item.")

    tree.bind("<Double-1>", edit_tree_item)

    btn_frame = tk.Frame(visual_frame)
    tk.Button(btn_frame, text="Add Folder", command=add_folder).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Add File", command=add_file).pack(side=tk.LEFT, padx=5)
    def on_edit_tree_item():
        # Simulate double-click edit for selected item
        event = None
        edit_tree_item(event)
    tk.Button(btn_frame, text="Edit Selected", command=on_edit_tree_item).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Remove Selected", command=remove_item).pack(side=tk.LEFT, padx=5)
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
    btn_row.pack(pady=10)
    notebook.add(visual_frame, text="Visual Editor")
    notebook.add(json_frame, text="Raw JSON")
    notebook.pack(fill=tk.BOTH, expand=True)
    refresh_tree()

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
        # Save project info to project_lists.json (new structure)
        projects = load_project_list()
        if not any(p["name"] == project_name for p in projects):
            new_proj = {
                "id": get_next_project_id(projects),
                "name": project_name,
                "description": f"This is a description of {project_name}.",
                "status": "active"
            }
            projects.append(new_proj)
            save_project_list(projects)
            refresh_projects_all()
        notice_var.set(f"Project '{project_name}' Created!")

    project_name_var = tk.StringVar()
    tk.Label(main_frame, text="Project Name:").grid(row=0, column=0, padx=(10,0), pady=10, sticky="w")
    tk.Entry(main_frame, textvariable=project_name_var, width=60).grid(row=0, column=1, padx=(0,0), pady=10, sticky="w")
    tk.Button(main_frame, text="Create Project", command=create_project_gui).grid(row=0, column=2, padx=(4,0), pady=10, sticky="w")
    notice_var = tk.StringVar(value=" ")
    notice_label = tk.Label(main_frame, textvariable=notice_var, fg="green", width=24, anchor="w")
    notice_label.grid(row=0, column=3, padx=(10,10), pady=10, sticky="w")
    def center_window(win, width=1400, height=640):
        win.update_idletasks()
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")
    center_window(root)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=0)

    # Reduce vertical space between Project Name and Config area
    main_frame.grid_rowconfigure(1, minsize=10)
    config_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=(0,10), sticky="nsew")
    # Remove extra row=3 config_frame grid if present
    # (the config_frame.grid call in the original code with row=3 is now replaced above)

    def on_proj_tree_double_click(event):
        selected = proj_tree.focus()
        if not selected:
            return
        values = proj_tree.item(selected, "values")
        if not values:
            return
        proj_id = int(values[0])
        projects = load_project_list()
        for i, proj in enumerate(projects):
            if proj["id"] == proj_id:
                updated = edit_project_dialog(right_frame, proj)
                if updated:
                    projects[i] = updated
                    save_project_list(projects)
                    refresh_project_tree()
                    refresh_project_json()
                break
    proj_tree.bind("<Double-1>", on_proj_tree_double_click)

    root.mainloop()

if __name__ == "__main__":
    run_app()
