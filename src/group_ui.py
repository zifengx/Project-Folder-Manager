"""
Project group management UI components
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from typing import List, Optional, Callable
from .models import ProjectGroup, ProjectManager
from .ui_utils import DialogManager, ValidationHelper, FormBuilder
from .config import STATUS_OPTIONS, STATUS_ACTIVE, STATUS_INACTIVE


class GroupDialog:
    """Dialog for adding/editing project groups"""
    
    def __init__(self, parent: tk.Widget, project_manager: ProjectManager, group: Optional[ProjectGroup] = None):
        self.parent = parent
        self.project_manager = project_manager
        self.group = group
        self.result = None
        self._create_dialog()
    
    def _create_dialog(self):
        title = f"Edit Group: {self.group.name}" if self.group else "Add Group"
        self.dialog = DialogManager.create_modal_dialog(self.parent, title)
        
        self.form = FormBuilder(self.dialog)
        
        # Form fields
        self.name_var = self.form.add_text_field(
            "Group Name", self.group.name if self.group else ""
        )
        self.desc_var = self.form.add_text_field(
            "Description", self.group.description if self.group else ""
        )
        self.status_var = self.form.add_combobox(
            "Status", STATUS_OPTIONS, 
            getattr(self.group, 'status', STATUS_ACTIVE) if self.group else STATUS_ACTIVE
        )
        
        # Buttons
        self.form.add_button_row([
            ("Save" if self.group else "Add", self._on_save),
            ("Cancel", self._on_cancel)
        ])
        
        # Auto-size and center the dialog
        DialogManager.auto_size_and_center(self.dialog, self.parent)
    
    def _on_save(self):
        """Validate and save group"""
        # Validate required fields
        name_error = ValidationHelper.validate_required_field(
            self.name_var.get(), "Group name"
        )
        if name_error:
            messagebox.showerror("Error", name_error, parent=self.dialog)
            return
        
        # Create result group
        if self.group:
            self.result = ProjectGroup(
                id=self.group.id,
                name=self.name_var.get().strip(),
                description=self.desc_var.get().strip(),
                status=self.status_var.get()
            )
        else:
            self.result = ProjectGroup(
                id=0,  # Will be set by manager
                name=self.name_var.get().strip(),
                description=self.desc_var.get().strip(),
                status=self.status_var.get()
            )
        
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()
    
    def show(self) -> Optional[ProjectGroup]:
        """Show dialog and return result"""
        self.dialog.wait_window()
        return self.result


class GroupListPanel:
    """Panel for managing project group list"""
    
    def __init__(self, parent: tk.Widget, project_manager: ProjectManager):
        self.parent = parent
        self.project_manager = project_manager
        self.on_group_changed: Optional[Callable] = None
        self._create_ui()
        self.refresh()
    
    def _create_ui(self):
        """Create the UI components"""
        # Main frame
        self.frame = tk.LabelFrame(self.parent, text="Group List", padx=5, pady=5)
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
            columns=("ID", "Name", "Description", "Status"),
            show="headings"
        )
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name") 
        self.tree.heading("Description", text="Description")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Name", width=120, anchor="w")
        self.tree.column("Description", width=180, anchor="w")
        self.tree.column("Status", width=80, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Configure styling for inactive groups
        self.tree.tag_configure("inactive", foreground="#888888", 
                               font=("Arial", 10, "overstrike"))
        
        # Bind double-click
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Button frame
        btn_frame = tk.Frame(self.visual_frame)
        tk.Button(btn_frame, text="Add Group", command=self._on_add).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit Selected", command=self._on_edit).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Remove Selected", command=self._on_remove).pack(side=tk.LEFT, padx=5)
        btn_frame.pack(pady=(0, 8))
        
        self.notebook.add(self.visual_frame, text="Visual Editor")
    
    def _create_json_tab(self):
        """Create raw JSON tab"""
        self.json_frame = tk.Frame(self.notebook)
        
        # Text widget
        self.json_text = scrolledtext.ScrolledText(
            self.json_frame, wrap=tk.WORD, width=60, height=18
        )
        self.json_text.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
        
        # Button frame
        btn_frame = tk.Frame(self.json_frame)
        tk.Button(btn_frame, text="Save", command=self._save_json).pack(side=tk.LEFT, padx=5)
        btn_frame.pack(pady=(0, 8))
        
        self.notebook.add(self.json_frame, text="Raw JSON")
    
    def _on_add(self):
        """Add new group"""
        dialog = GroupDialog(self.frame, self.project_manager)
        group = dialog.show()
        
        if group:
            try:
                self.project_manager.add_group(
                    group.name, group.description, getattr(group, 'status', STATUS_ACTIVE)
                )
                self.refresh()
                if self.on_group_changed:
                    self.on_group_changed()
                messagebox.showinfo("Success", f"Group '{group.name}' added.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
    
    def _on_edit(self):
        """Edit selected group"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Edit Group", "Please select a group to edit.")
            return
        
        group = self._get_selected_group()
        if not group:
            return
        
        dialog = GroupDialog(self.frame, self.project_manager, group)
        updated_group = dialog.show()
        
        if updated_group:
            try:
                self.project_manager.update_group(
                    updated_group.id, updated_group.name, 
                    updated_group.description, getattr(updated_group, 'status', STATUS_ACTIVE)
                )
                self.refresh()
                if self.on_group_changed:
                    self.on_group_changed()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
    
    def _on_remove(self):
        """Remove selected group"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Remove Group", "Please select a group to remove.")
            return
        
        group = self._get_selected_group()
        if not group:
            return
        
        if DialogManager.confirm_dialog(
            self.frame, "Remove Group", 
            f"Are you sure you want to remove group '{group.name}'?"
        ):
            self.project_manager.delete_group(group.id)
            self.refresh()
            if self.on_group_changed:
                self.on_group_changed()
    
    def _on_double_click(self, event):
        """Handle double-click on tree item"""
        self._on_edit()
    
    def _get_selected_group(self) -> Optional[ProjectGroup]:
        """Get currently selected group"""
        selected = self.tree.focus()
        if not selected:
            return None
        
        values = self.tree.item(selected, "values")
        if not values:
            return None
        
        group_id = int(values[0])
        groups = self.project_manager.load_groups()
        
        for group in groups:
            if group.id == group_id:
                return group
        
        return None
    
    def _save_json(self):
        """Save JSON text"""
        try:
            json_text = self.json_text.get("1.0", tk.END)
            data = json.loads(json_text)
            groups = [ProjectGroup.from_dict(group_data) for group_data in data]
            self.project_manager.save_groups(groups)
            self.refresh()
            if self.on_group_changed:
                self.on_group_changed()
            messagebox.showinfo("Saved", "Group list saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")
    
    def refresh(self):
        """Refresh both visual and JSON views"""
        self._refresh_tree()
        self._refresh_json()
    
    def _refresh_tree(self):
        """Refresh tree view"""
        self.tree.delete(*self.tree.get_children())
        
        # Sort groups by ID descending
        groups = sorted(self.project_manager.load_groups(), 
                       key=lambda g: g.id, reverse=True)
        
        for group in groups:
            status = getattr(group, 'status', STATUS_ACTIVE)
            values = (
                group.id,
                group.name,
                group.description,
                status
            )
            
            if status == STATUS_INACTIVE:
                self.tree.insert("", tk.END, values=values, tags=("inactive",))
            else:
                self.tree.insert("", tk.END, values=values)
    
    def _refresh_json(self):
        """Refresh JSON view"""
        try:
            groups = self.project_manager.load_groups()
            data = [group.to_dict() for group in groups]
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            
            self.json_text.delete("1.0", tk.END)
            self.json_text.insert(tk.END, json_str)
        except Exception:
            self.json_text.delete("1.0", tk.END)
            self.json_text.insert(tk.END, "[]")
