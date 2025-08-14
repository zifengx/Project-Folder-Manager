"""
Structure editor UI components
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
from typing import Dict, List, Optional
from .models import StructureManager
from .ui_utils import DialogManager, ValidationHelper, FormBuilder


class StructureItemDialog:
    """Dialog for adding/editing structure items"""
    
    def __init__(self, parent: tk.Widget, item_type: str, name: str = "", comment: str = "", attribute: str = "manual"):
        self.parent = parent
        self.item_type = item_type  # "Folder" or "File"
        self.result = None
        self.name = name
        self.comment = comment
        self.attribute = attribute
        self._create_dialog()
    
    def _create_dialog(self):
        title = f"{'Edit' if self.name else 'Add'} {self.item_type}"
        self.dialog = DialogManager.create_modal_dialog(self.parent, title)
        
        self.form = FormBuilder(self.dialog)
        
        # Name field
        self.name_var = self.form.add_text_field(f"{self.item_type} Name", self.name)
        
        # Special handling for files - add placeholder
        if self.item_type == "File" and not self.name:
            name_entry = self.dialog.grid_slaves(row=0, column=1)[0]
            self._setup_file_placeholder(name_entry)
        
        # Comment field
        self.comment_var = self.form.add_text_field("Comment", self.comment)
        
        # Sync field (for both folders and files)
        self.attribute_var = self.form.add_combobox(
            "Sync", ["manual", "auto"], self.attribute
        )
        
        # Buttons
        self.form.add_button_row([
            ("Save" if self.name else "Add", self._on_save),
            ("Cancel", self._on_cancel)
        ])
        
        # Auto-size and center the dialog
        DialogManager.auto_size_and_center(self.dialog, self.parent)
    
    def _setup_file_placeholder(self, entry: tk.Entry):
        """Setup placeholder text for file name entry"""
        def set_placeholder(event=None):
            if not self.name_var.get():
                entry.insert(0, "with extension")
                entry.config(fg="#888888")
        
        def clear_placeholder(event=None):
            if entry.get() == "with extension":
                entry.delete(0, tk.END)
                entry.config(fg="#000000")
        
        entry.bind("<FocusIn>", clear_placeholder)
        entry.bind("<FocusOut>", set_placeholder)
        set_placeholder()
    
    def _on_save(self):
        """Validate and save"""
        name = self.name_var.get().strip()
        
        # Validate name
        if not name or name == "with extension":
            messagebox.showerror("Error", f"{self.item_type} name cannot be empty.", 
                               parent=self.dialog)
            return
        
        self.result = {
            "name": name,
            "comment": self.comment_var.get().strip()
        }
        
        # Add attribute for both folders and files
        if self.attribute_var:
            self.result["attribute"] = self.attribute_var.get()
        
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()
    
    def show(self) -> Optional[Dict]:
        """Show dialog and return result"""
        self.dialog.wait_window()
        return self.result


class StructurePanel:
    """Panel for managing folder structure"""
    
    def __init__(self, parent: tk.Widget, structure_manager: StructureManager):
        self.parent = parent
        self.structure_manager = structure_manager
        self._create_ui()
        self.refresh()
    
    def _create_ui(self):
        """Create the UI components"""
        # Main frame - removed LabelFrame to avoid duplication
        self.frame = tk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        
        # Visual editor tab
        self._create_visual_tab()
        
        # Raw JSON tab
        self._create_json_tab()
        
        self.notebook.pack(fill=tk.BOTH, expand=True)
    
    def _create_visual_tab(self):
        """Create visual editor tab"""
        self.visual_frame = tk.Frame(self.notebook)
        
        # Treeview
        self.tree = ttk.Treeview(
            self.visual_frame,
            columns=("Type", "Attribute", "Comment"),
            show="tree headings"
        )
        
        # Configure columns
        self.tree.heading("#0", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Attribute", text="Sync")
        self.tree.heading("Comment", text="Comment")
        
        self.tree.column("#0", width=120, anchor="w")
        self.tree.column("Type", width=60, anchor="center")
        self.tree.column("Attribute", width=80, anchor="center")
        self.tree.column("Comment", width=240, anchor="w")
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bind double-click
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Button frame
        btn_frame = tk.Frame(self.visual_frame)
        tk.Button(btn_frame, text="Add Folder", command=self._add_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Add File", command=self._add_file).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit Selected", command=self._edit_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self._remove_selected).pack(side=tk.LEFT, padx=5)
        btn_frame.pack(pady=5)
        
        self.notebook.add(self.visual_frame, text="Visual Editor")
    
    def _create_json_tab(self):
        """Create raw JSON tab"""
        self.json_frame = tk.Frame(self.notebook)
        
        # Text widget
        self.json_text = scrolledtext.ScrolledText(
            self.json_frame, wrap=tk.WORD, width=70, height=15
        )
        self.json_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Button frame
        btn_frame = tk.Frame(self.json_frame)
        tk.Button(btn_frame, text="Save", command=self._save_json).pack(side=tk.LEFT, padx=5)
        btn_frame.pack(pady=10)
        
        self.notebook.add(self.json_frame, text="Raw JSON")
    
    def _add_folder(self):
        """Add new folder"""
        dialog = StructureItemDialog(self.frame, "Folder")
        result = dialog.show()
        
        if result:
            self._add_item_to_structure(result, is_folder=True)
    
    def _add_file(self):
        """Add new file"""
        dialog = StructureItemDialog(self.frame, "File")
        result = dialog.show()
        
        if result:
            self._add_item_to_structure(result, is_folder=False)
    
    def _edit_selected(self):
        """Edit selected item"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Edit Item", "Please select an item to edit.")
            return
        
        name = self.tree.item(selected, "text")
        values = self.tree.item(selected, "values")
        item_type = values[0] if values else ""
        attribute = values[1] if len(values) > 1 else "manual"
        comment = values[2] if len(values) > 2 else ""
        
        dialog = StructureItemDialog(self.frame, item_type, name, comment, attribute)
        result = dialog.show()
        
        if result:
            self._update_item_in_structure(name, result, item_type)
    
    def _remove_selected(self):
        """Remove selected item"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Remove Item", "Please select an item to remove.")
            return
        
        name = self.tree.item(selected, "text")
        values = self.tree.item(selected, "values")
        item_type = values[0] if values else ""
        
        if DialogManager.confirm_dialog(
            self.frame, "Remove Item",
            f"Are you sure you want to remove {item_type.lower()} '{name}'?"
        ):
            self._remove_item_from_structure(name, item_type)
    
    def _on_double_click(self, event):
        """Handle double-click on tree item"""
        # Get the region that was clicked
        region = self.tree.identify_region(event.x, event.y)
        
        # Only trigger edit if the click was on the item content, not on the tree icon
        if region == "tree":
            # Check if click was on the expand/collapse icon
            element = self.tree.identify_element(event.x, event.y)
            if element == "Treeitem.indicator":
                # Click was on expand/collapse icon, don't trigger edit
                return
        
        # Only edit if click was on item text or other content areas
        if region in ("tree", "cell"):
            # Prevent the default tree behavior (expand/collapse) when editing
            self._edit_selected()
            # Return "break" to stop event propagation
            return "break"
    
    def _add_item_to_structure(self, item_data: Dict, is_folder: bool):
        """Add item to structure"""
        try:
            structure = self.structure_manager.load_structure()
            
            if is_folder:
                # Add to folders list or selected folder
                selected = self.tree.focus()
                folder_item = {"name": item_data["name"], "folders": []}
                if item_data["comment"]:
                    folder_item["comment"] = item_data["comment"]
                if item_data.get("attribute", "manual") != "manual":
                    folder_item["attribute"] = item_data["attribute"]
                
                if not selected:
                    structure["folders"].append(folder_item)
                else:
                    # Add to selected folder
                    self._add_to_selected_folder(structure["folders"], selected, folder_item)
            else:
                # Add to files list
                file_item = {"name": item_data["name"]}
                if item_data["comment"]:
                    file_item["comment"] = item_data["comment"]
                if item_data.get("attribute", "manual") != "manual":
                    file_item["attribute"] = item_data["attribute"]
                structure["files"].append(file_item)
            
            self.structure_manager.save_structure(structure)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {e}")
    
    def _add_to_selected_folder(self, folders: List[Dict], selected_node: str, new_folder: Dict):
        """Add folder to selected parent folder"""
        selected_name = self.tree.item(selected_node, "text")
        
        def find_and_add(items):
            for item in items:
                if item["name"] == selected_name:
                    if "folders" not in item:
                        item["folders"] = []
                    item["folders"].append(new_folder)
                    return True
                if "folders" in item and find_and_add(item["folders"]):
                    return True
            return False
        
        find_and_add(folders)
    
    def _update_item_in_structure(self, old_name: str, new_data: Dict, item_type: str):
        """Update item in structure"""
        try:
            structure = self.structure_manager.load_structure()
            
            if item_type == "Folder":
                self._update_folder_recursive(structure["folders"], old_name, new_data)
            else:
                # Update file
                for file_item in structure["files"]:
                    if file_item["name"] == old_name:
                        file_item["name"] = new_data["name"]
                        if new_data["comment"]:
                            file_item["comment"] = new_data["comment"]
                        elif "comment" in file_item:
                            del file_item["comment"]
                        
                        # Handle attribute for files
                        if new_data.get("attribute", "manual") != "manual":
                            file_item["attribute"] = new_data["attribute"]
                        elif "attribute" in file_item:
                            del file_item["attribute"]
                        break
            
            self.structure_manager.save_structure(structure)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update item: {e}")
    
    def _update_folder_recursive(self, folders: List[Dict], old_name: str, new_data: Dict):
        """Update folder recursively"""
        for folder in folders:
            if folder["name"] == old_name:
                folder["name"] = new_data["name"]
                if new_data["comment"]:
                    folder["comment"] = new_data["comment"]
                elif "comment" in folder:
                    del folder["comment"]
                
                # Handle attribute
                if new_data.get("attribute", "manual") != "manual":
                    folder["attribute"] = new_data["attribute"]
                elif "attribute" in folder:
                    del folder["attribute"]
                
                return True
            if "folders" in folder and self._update_folder_recursive(folder["folders"], old_name, new_data):
                return True
        return False
    
    def _remove_item_from_structure(self, name: str, item_type: str):
        """Remove item from structure"""
        try:
            structure = self.structure_manager.load_structure()
            
            if item_type == "Folder":
                self._remove_folder_recursive(structure["folders"], name)
            else:
                structure["files"] = [f for f in structure["files"] if f["name"] != name]
            
            self.structure_manager.save_structure(structure)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove item: {e}")
    
    def _remove_folder_recursive(self, folders: List[Dict], name: str):
        """Remove folder recursively"""
        for i, folder in enumerate(folders):
            if folder["name"] == name:
                del folders[i]
                return True
            if "folders" in folder and self._remove_folder_recursive(folder["folders"], name):
                return True
        return False
    
    def _save_json(self):
        """Save JSON text"""
        try:
            json_text = self.json_text.get("1.0", tk.END)
            structure = json.loads(json_text)
            self.structure_manager.save_structure(structure)
            self.refresh()
            messagebox.showinfo("Saved", "Structure saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")
    
    def refresh(self):
        """Refresh both visual and JSON views"""
        self._refresh_tree()
        self._refresh_json()
    
    def _refresh_tree(self):
        """Refresh tree view"""
        self.tree.delete(*self.tree.get_children())
        
        try:
            structure = self.structure_manager.load_structure()
            # Sort folders and files by sync attribute first (manual before auto), then alphabetically by name
            def sort_key(x):
                attr = x.get("attribute", "manual")
                # Use 0 for manual, 1 for auto to ensure manual comes first
                attr_priority = 0 if attr == "manual" else 1
                return (attr_priority, x["name"].lower())
            
            folders = sorted(structure.get("folders", []), key=sort_key)
            files = sorted(structure.get("files", []), key=sort_key)
            self._insert_items("", folders, True)
            self._insert_items("", files, False)
        except Exception:
            pass
    
    def _insert_items(self, parent: str, items: List[Dict], is_folder: bool):
        """Insert items into tree"""
        # Sort items by sync attribute first (manual before auto), then alphabetically by name (case-insensitive)
        def sort_key(x):
            attr = x.get("attribute", "manual")
            # Use 0 for manual, 1 for auto to ensure manual comes first
            attr_priority = 0 if attr == "manual" else 1
            return (attr_priority, x["name"].lower())
        
        sorted_items = sorted(items, key=sort_key)
        
        for item in sorted_items:
            comment = item.get("comment", "")
            item_type = "Folder" if is_folder else "File"
            attribute = item.get("attribute", "manual")
            
            values = (item_type, attribute, comment)
            
            node = self.tree.insert(
                parent, "end", 
                text=item["name"], 
                open=True,
                values=values
            )
            
            # Recursively add subfolders (they will also be sorted with manual before auto, then alphabetically)
            if is_folder and "folders" in item:
                self._insert_items(node, item["folders"], True)
    
    def _refresh_json(self):
        """Refresh JSON view"""
        try:
            structure = self.structure_manager.load_structure()
            json_str = json.dumps(structure, indent=4, ensure_ascii=False)
            
            self.json_text.delete("1.0", tk.END)
            self.json_text.insert(tk.END, json_str)
        except Exception:
            self.json_text.delete("1.0", tk.END)
            self.json_text.insert(tk.END, '{\n    "folders": [],\n    "files": []\n}')


class ParentDirectoryPanel:
    """Panel for managing parent directory"""
    
    def __init__(self, parent: tk.Widget, structure_manager: StructureManager):
        self.parent = parent
        self.structure_manager = structure_manager
        self._create_ui()
        self.refresh()
    
    def _create_ui(self):
        """Create the UI components"""
        self.frame = tk.Frame(self.parent)
        
        # Entry (readonly) - removed redundant label
        self.path_var = tk.StringVar()
        self.entry = tk.Entry(self.frame, textvariable=self.path_var, width=80, state="readonly")
        self.entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Browse button
        tk.Button(self.frame, text="Browse...", command=self._browse).pack(side=tk.LEFT)
        
        self.frame.pack(pady=5, anchor="w")
    
    def _browse(self):
        """Browse for directory"""
        selected = filedialog.askdirectory(
            title="Select parent directory",
            initialdir=self.path_var.get()
        )
        
        if selected:
            try:
                self.structure_manager.set_parent_directory(selected)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save parent directory: {e}")
    
    def refresh(self):
        """Refresh the display"""
        try:
            path = self.structure_manager.get_parent_directory()
            self.path_var.set(path)
        except Exception:
            pass


class SyncDirectoryPanel:
    """Panel for managing sync directory"""
    
    def __init__(self, parent: tk.Widget, structure_manager: StructureManager):
        self.parent = parent
        self.structure_manager = structure_manager
        self._create_ui()
        self.refresh()
    
    def _create_ui(self):
        """Create the UI components"""
        self.frame = tk.Frame(self.parent)
        
        # Entry (readonly) - removed redundant label
        self.path_var = tk.StringVar()
        self.entry = tk.Entry(self.frame, textvariable=self.path_var, width=80, state="readonly")
        self.entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Browse button
        tk.Button(self.frame, text="Browse...", command=self._browse).pack(side=tk.LEFT)
        
        self.frame.pack(pady=5, anchor="w")
    
    def _browse(self):
        """Browse for directory"""
        selected = filedialog.askdirectory(
            title="Select sync directory",
            initialdir=self.path_var.get()
        )
        
        if selected:
            try:
                self.structure_manager.set_sync_directory(selected)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save sync directory: {e}")
    
    def refresh(self):
        """Refresh the display"""
        try:
            path = self.structure_manager.get_sync_directory()
            self.path_var.set(path)
        except Exception:
            pass


class StructureConfigDialog:
    """Dialog for structure configuration including parent directory, sync directory, and structure editing"""
    
    def __init__(self, parent: tk.Widget, structure_manager: StructureManager):
        self.parent = parent
        self.structure_manager = structure_manager
        self.dialog = None
        
    def show(self):
        """Show the structure config dialog using smooth DialogManager approach"""
        self.dialog = DialogManager.create_modal_dialog(self.parent, "Structure Configuration", 900, 700)
        
        # Create main container with proper layout
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Configure main frame grid
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=0)  # Parent directory
        main_frame.grid_rowconfigure(1, weight=0)  # Sync directory  
        main_frame.grid_rowconfigure(2, weight=1)  # Structure panel
        
        # Parent directory section
        parent_frame = tk.LabelFrame(main_frame, text="Parent Directory", padx=8, pady=8)
        parent_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.parent_dir_panel = ParentDirectoryPanel(parent_frame, self.structure_manager)
        
        # Sync directory section  
        sync_frame = tk.LabelFrame(main_frame, text="Sync Directory", padx=8, pady=8)
        sync_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.sync_dir_panel = SyncDirectoryPanel(sync_frame, self.structure_manager)
        
        # Structure editor section
        structure_frame = tk.LabelFrame(main_frame, text="Folder Structure", padx=8, pady=8)
        structure_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 15))
        self.structure_panel = StructurePanel(structure_frame, self.structure_manager)
        
        # Center dialog using DialogManager
        DialogManager.center_dialog(self.dialog, self.parent)
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._close)
        
    def _close(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.destroy()
