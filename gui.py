import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from core import ensure_structure_json, load_structure, create_project
import json

STRUCTURE_JSON = os.path.join(os.path.dirname(__file__), "structure.json")

if getattr(sys, 'frozen', False):
    # Running as a bundled executable
    PROGRAM_ROOT = os.path.dirname(sys.executable)
else:
    # Running as a script
    PROGRAM_ROOT = os.path.dirname(os.path.abspath(__file__))

PARENT_OF_PROGRAM_ROOT = os.path.dirname(PROGRAM_ROOT)

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

def run_app():
    root = tk.Tk()
    root.title("Project Folder Manager")
    try:
        ensure_structure_json()
    except Exception as e:
        root.withdraw()
        messagebox.showerror("Error", str(e))
        return

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
        parent_dir = load_parent_dir().strip()
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

    # --- Config/Structure Editor Panel (in main window) ---
    import json
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
                node = tree.insert(parent, "end", text=item["name"], open=True, values=("Folder" if is_folder else "File"))
                if is_folder and "folders" in item:
                    insert_items(node, item["folders"], True)
        struct = load_structure_json()
        insert_items("", struct.get("folders", []), True)
        insert_items("", struct.get("files", []), False)
    def add_folder():
        selected = tree.focus()
        name = simple_input_dialog(root, "Folder name:")
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
        name = simple_input_dialog(root, "File name:")
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
    config_frame = tk.LabelFrame(root, text="Config", padx=5, pady=5)
    config_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
    config_frame.columnconfigure(0, weight=1)
    config_frame.rowconfigure(0, weight=1)
    # Parent Directory Setting
    pd_frame = tk.Frame(config_frame)
    struct = load_structure_json()
    pd_value = struct.get("parent_directory", "").strip() or PROGRAM_ROOT
    pd_var = tk.StringVar(value=pd_value)
    pd_label = tk.Label(pd_frame, text="Parent Directory:")
    pd_label.pack(side=tk.LEFT, padx=(0,5))
    pd_entry = tk.Entry(pd_frame, textvariable=pd_var, width=40, state="readonly")
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
    # Add a titled frame for the folder structure editor, using only pack inside
    structure_frame = tk.LabelFrame(config_frame, text="Folder Structure", padx=5, pady=5)
    structure_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    notebook = ttk.Notebook(structure_frame)
    visual_frame = tk.Frame(notebook)
    tree = ttk.Treeview(visual_frame, columns=("Type",), show="tree headings")
    tree.heading("#0", text="Name")
    tree.heading("Type", text="Type")
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
    tk.Button(json_frame, text="Save", command=save_from_json).pack(pady=10)
    tk.Button(json_frame, text="Reset", command=reset_to_saved).pack(pady=5)
    notebook.add(visual_frame, text="Visual Editor")
    notebook.add(json_frame, text="Raw JSON")
    notebook.pack(fill=tk.BOTH, expand=True)
    refresh_tree()
    # --- End Config/Structure Editor Panel ---

    # --- Center the Config section and make it fill the window ---
    config_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)
    config_frame.grid_propagate(False)
    config_frame.pack_propagate(False)
    config_frame.rowconfigure(1, weight=1)
    config_frame.columnconfigure(0, weight=1)
    notebook.pack(fill=tk.BOTH, expand=True)
    # --- End Center ---

    # Set a larger initial window size and center it
    def center_window(win, width=800, height=600):
        win.update_idletasks()
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    # Project Name widgets at the top, all side by side and tightly spaced
    tk.Label(root, text="Project Name:").grid(row=0, column=0, padx=(10,0), pady=10, sticky="w")
    project_name_var = tk.StringVar()
    tk.Entry(root, textvariable=project_name_var, width=40).grid(row=0, column=1, padx=(0,0), pady=10, sticky="w")
    tk.Button(root, text="Create Project", command=create_project_gui).grid(row=0, column=2, padx=(4,10), pady=10, sticky="w")

    # Make the window stay on top at launch
    root.lift()
    root.attributes('-topmost', True)


    center_window(root)

    root.mainloop()
