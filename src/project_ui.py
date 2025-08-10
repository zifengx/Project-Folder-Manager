"""
Project management UI components
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from typing import List, Optional, Callable
from .models import Project, ProjectManager, ProjectGroup
from .ui_utils import DialogManager, ValidationHelper, FormBuilder
from .config import STATUS_OPTIONS, STATUS_ACTIVE, STATUS_INACTIVE
import datetime


class ProjectDialog:
    """Dialog for adding/editing projects"""
    
    def __init__(self, parent: tk.Widget, project_manager: ProjectManager, project: Optional[Project] = None):
        self.parent = parent
        self.project_manager = project_manager
        self.project = project
        self.result = None
        self._create_dialog()
    
    def _create_dialog(self):
        title = f"Edit Project: {self.project.name}" if self.project else "Add Project"
        self.dialog = DialogManager.create_modal_dialog(self.parent, title)
        
        self.form = FormBuilder(self.dialog)
        
        # Form fields
        self.name_var = self.form.add_text_field(
            "Project Name", self.project.name if self.project else ""
        )
        self.desc_var = self.form.add_text_field(
            "Description", self.project.description if self.project else ""
        )
        self.status_var = self.form.add_combobox(
            "Status", STATUS_OPTIONS, 
            self.project.status if self.project else STATUS_ACTIVE
        )
        self.start_date_var = self.form.add_text_field(
            "Start Date", 
            self.project.start_date if self.project else datetime.date.today().isoformat(),
            width=20
        )
        
        # Group selection field
        groups = self.project_manager.load_groups()
        group_options = [("None", 0)] + [(group.name, group.id) for group in groups]
        group_names = [item[0] for item in group_options]
        
        current_group_id = self.project.group_id if self.project else 0
        current_group_name = "None"
        for name, gid in group_options:
            if gid == current_group_id:
                current_group_name = name
                break
        
        self.group_var = self.form.add_combobox(
            "Project Group", group_names, current_group_name
        )
        self.group_options = group_options  # Store for later lookup
        
        # End date field (manual to maintain control logic)
        tk.Label(self.dialog, text="End Date:").grid(
            row=self.form.row, column=0, sticky="e", padx=5, pady=2
        )
        self.end_date_var = tk.StringVar(
            value=self.project.end_date if self.project else ""
        )
        self.end_date_entry = tk.Entry(
            self.dialog, textvariable=self.end_date_var, width=20
        )
        self.end_date_entry.grid(
            row=self.form.row, column=1, padx=5, pady=2, sticky="w"
        )
        self.form.row += 1
        
        # Bind status change
        self.status_var.trace("w", self._on_status_change)
        self._on_status_change()
        
        # Buttons
        self.form.add_button_row([
            ("Save" if self.project else "Add", self._on_save),
            ("Cancel", self._on_cancel)
        ])
        
        # Auto-size and center the dialog
        DialogManager.auto_size_and_center(self.dialog, self.parent)
    
    def _on_status_change(self, *args):
        """Handle status change"""
        if self.status_var.get() == STATUS_INACTIVE:
            self.end_date_entry.config(state="normal")
            if not self.end_date_var.get():
                self.end_date_var.set(datetime.date.today().isoformat())
        else:
            self.end_date_entry.config(state="normal")
            self.end_date_var.set("")
            self.end_date_entry.config(state="disabled")
    
    def _on_save(self):
        """Validate and save project"""
        # Validate required fields
        name_error = ValidationHelper.validate_required_field(
            self.name_var.get(), "Project name"
        )
        if name_error:
            messagebox.showerror("Error", name_error, parent=self.dialog)
            return
        
        # Validate dates
        if not ValidationHelper.validate_date(self.start_date_var.get()):
            messagebox.showerror(
                "Error", "Start Date must be in YYYY-MM-DD format", parent=self.dialog
            )
            return
        
        if not ValidationHelper.validate_date(self.end_date_var.get()):
            messagebox.showerror(
                "Error", "End Date must be in YYYY-MM-DD format", parent=self.dialog
            )
            return
        
        # Get selected group ID
        selected_group_name = self.group_var.get()
        selected_group_id = 0
        for name, gid in self.group_options:
            if name == selected_group_name:
                selected_group_id = gid
                break
        
        # Create result project
        if self.project:
            self.result = Project(
                id=self.project.id,
                name=self.name_var.get().strip(),
                description=self.desc_var.get().strip(),
                status=self.status_var.get(),
                start_date=self.start_date_var.get().strip(),
                end_date=self.end_date_var.get().strip(),
                group_id=selected_group_id
            )
        else:
            self.result = Project(
                id=0,  # Will be set by manager
                name=self.name_var.get().strip(),
                description=self.desc_var.get().strip(),
                status=self.status_var.get(),
                start_date=self.start_date_var.get().strip(),
                end_date=self.end_date_var.get().strip(),
                group_id=selected_group_id
            )
        
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()
    
    def show(self) -> Optional[Project]:
        """Show dialog and return result"""
        self.dialog.wait_window()
        return self.result


class ProjectListPanel:
    """Panel for managing project list"""
    
    def __init__(self, parent: tk.Widget, project_manager: ProjectManager):
        self.parent = parent
        self.project_manager = project_manager
        self.on_project_changed: Optional[Callable] = None
        self._create_ui()
        self.refresh()
    
    def _create_ui(self):
        """Create the UI components"""
        # Main frame
        self.frame = tk.LabelFrame(self.parent, text="Project List", padx=5, pady=5)
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
            columns=("ID", "Name", "Description", "Group", "Status", "Start Date", "End Date"),
            show="headings"
        )
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name") 
        self.tree.heading("Description", text="Description")
        self.tree.heading("Group", text="Group")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Start Date", text="Start Date")
        self.tree.heading("End Date", text="End Date")
        
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Name", width=120, anchor="w")
        self.tree.column("Description", width=180, anchor="w")
        self.tree.column("Group", width=100, anchor="w")
        self.tree.column("Status", width=60, anchor="center")
        self.tree.column("Start Date", width=80, anchor="center")
        self.tree.column("End Date", width=80, anchor="center")
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Configure styling for inactive projects
        self.tree.tag_configure("inactive", foreground="#888888", 
                               font=("Arial", 10, "overstrike"))
        
        # Bind double-click
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Button frame
        btn_frame = tk.Frame(self.visual_frame)
        tk.Button(btn_frame, text="Add Project", command=self._on_add).pack(side=tk.LEFT, padx=5)
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
        """Add new project"""
        dialog = ProjectDialog(self.frame, self.project_manager)
        project = dialog.show()
        
        if project:
            try:
                self.project_manager.add_project(
                    project.name, project.description, project.status, project.group_id
                )
                self.refresh()
                if self.on_project_changed:
                    self.on_project_changed()
                messagebox.showinfo("Success", f"Project '{project.name}' added.")
            except ValueError as e:
                messagebox.showerror("Error", str(e))
    
    def _on_edit(self):
        """Edit selected project"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Edit Project", "Please select a project to edit.")
            return
        
        project = self._get_selected_project()
        if not project:
            return
        
        dialog = ProjectDialog(self.frame, self.project_manager, project)
        updated_project = dialog.show()
        
        if updated_project:
            try:
                self.project_manager.update_project(updated_project)
                self.refresh()
                if self.on_project_changed:
                    self.on_project_changed()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
    
    def _on_remove(self):
        """Remove selected project"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showinfo("Remove Project", "Please select a project to remove.")
            return
        
        project = self._get_selected_project()
        if not project:
            return
        
        if DialogManager.confirm_dialog(
            self.frame, "Remove Project", 
            f"Are you sure you want to remove project '{project.name}'?"
        ):
            self.project_manager.delete_project(project.id)
            self.refresh()
            if self.on_project_changed:
                self.on_project_changed()
    
    def _on_double_click(self, event):
        """Handle double-click on tree item"""
        self._on_edit()
    
    def _get_selected_project(self) -> Optional[Project]:
        """Get currently selected project"""
        selected = self.tree.focus()
        if not selected:
            return None
        
        values = self.tree.item(selected, "values")
        if not values:
            return None
        
        project_id = int(values[0])
        projects = self.project_manager.load_projects()
        
        for project in projects:
            if project.id == project_id:
                return project
        
        return None
    
    def _save_json(self):
        """Save JSON text"""
        try:
            json_text = self.json_text.get("1.0", tk.END)
            data = json.loads(json_text)
            projects = [Project.from_dict(proj_data) for proj_data in data]
            self.project_manager.save_projects(projects)
            self.refresh()
            if self.on_project_changed:
                self.on_project_changed()
            messagebox.showinfo("Saved", "Project list saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")
    
    def refresh(self):
        """Refresh both visual and JSON views"""
        self._refresh_tree()
        self._refresh_json()
    
    def _refresh_tree(self):
        """Refresh tree view"""
        self.tree.delete(*self.tree.get_children())
        
        # Load groups for group name lookup
        groups = self.project_manager.load_groups()
        group_dict = {group.id: group.name for group in groups}
        
        # Sort projects by ID descending
        projects = sorted(self.project_manager.load_projects(), 
                         key=lambda p: p.id, reverse=True)
        
        for project in projects:
            # Get group name or "None" if no group assigned
            group_name = group_dict.get(project.group_id, "None") if project.group_id != 0 else "None"
            
            values = (
                project.id,
                project.name,
                project.description,
                group_name,
                project.status,
                project.start_date,
                project.end_date or ""  # Show empty string if no end date
            )
            
            if project.status == STATUS_INACTIVE:
                self.tree.insert("", tk.END, values=values, tags=("inactive",))
            else:
                self.tree.insert("", tk.END, values=values)
    
    def _refresh_json(self):
        """Refresh JSON view"""
        try:
            projects = self.project_manager.load_projects()
            data = [proj.to_dict() for proj in projects]
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            
            self.json_text.delete("1.0", tk.END)
            self.json_text.insert(tk.END, json_str)
        except Exception:
            self.json_text.delete("1.0", tk.END)
            self.json_text.insert(tk.END, "[]")
