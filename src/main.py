"""
Main application window and coordinator
"""
import tkinter as tk
from tkinter import messagebox
import os
import sys
from .config import *
from .models import ProjectManager, StructureManager
from .project_ui import ProjectListPanel
from .structure_ui import StructurePanel, ParentDirectoryPanel, SyncDirectoryPanel
from .ui_utils import ValidationHelper


class MainApplication:
    """Main application class"""
    
    def __init__(self):
        self.root = None
        self.project_manager = None
        self.structure_manager = None
        self.project_panel = None
        self.structure_panel = None
        self.parent_dir_panel = None
        self.sync_dir_panel = None
        
    def run(self):
        """Run the application"""
        try:
            self._initialize()
            self._create_ui()
            self._setup_event_handlers()
            self.root.mainloop()
        except Exception as e:
            if self.root:
                self.root.withdraw()
            messagebox.showerror("Error", str(e))
    
    def _initialize(self):
        """Initialize managers and main window"""
        # Initialize managers
        self.project_manager = ProjectManager()
        self.structure_manager = StructureManager()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.resizable(True, True)
        
        # Center window
        self._center_window()
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
    
    def _center_window(self):
        """Center the main window on screen"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (WINDOW_WIDTH // 2)
        y = (screen_height // 2) - (WINDOW_HEIGHT // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    
    def _create_ui(self):
        """Create the main UI layout with config button and rearranged panels"""
        # Create a container frame for better control
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure container grid for new layout
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=0)  # Config button row
        container.grid_rowconfigure(1, weight=0)  # Project creation row
        container.grid_rowconfigure(2, weight=1)  # Main panels row
        
        # Config button section
        self._create_config_button_section(container)
        
        # Project creation section (spans both columns)
        self._create_project_creation_section_in_container(container)
        
        # Left panel (project list)
        self._create_left_panel_in_container(container)
        
        # Right panel (group list)
        self._create_right_panel_in_container(container)
    
    def _create_config_button_section(self, container):
        """Create config button section"""
        config_frame = tk.Frame(container)
        config_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        tk.Button(
            config_frame, 
            text="Config", 
            command=self._show_structure_config,
            font=("Arial", 9),
            relief="groove",
            padx=15,
            pady=3
        ).pack(side=tk.LEFT)
    
    def _show_structure_config(self):
        """Show Structure Config popup dialog"""
        from .structure_ui import StructureConfigDialog
        dialog = StructureConfigDialog(self.root, self.structure_manager)
        dialog.show()
    
    def _create_project_creation_section_in_container(self, container):
        """Create project creation controls in container"""
        # Project creation section (left side, in column 0)
        project_frame = tk.Frame(container)
        project_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10), padx=(0, 5))
        
        # Project name input
        tk.Label(project_frame, text="Project Name:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.project_name_var = tk.StringVar()
        tk.Entry(project_frame, textvariable=self.project_name_var, width=25).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(project_frame, text="Create Project", command=self._create_project).pack(side=tk.LEFT, padx=(0, 10))
        
        # Status/notice label for project
        self.notice_var = tk.StringVar(value=" ")
        self.notice_label = tk.Label(
            project_frame, textvariable=self.notice_var, 
            fg="green", width=20, anchor="w"
        )
        self.notice_label.pack(side=tk.LEFT)
        
        # Group creation section (right side, in column 1 - aligned with Project List)
        group_frame = tk.Frame(container)
        group_frame.grid(row=1, column=1, sticky="ew", pady=(0, 10), padx=(5, 0))
        
        # Group name input
        tk.Label(group_frame, text="Group Name:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.group_name_var = tk.StringVar()
        tk.Entry(group_frame, textvariable=self.group_name_var, width=25).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(group_frame, text="Create Group", command=self._create_group).pack(side=tk.LEFT, padx=(0, 10))
        
        # Status/notice label for group
        self.group_notice_var = tk.StringVar(value=" ")
        self.group_notice_label = tk.Label(
            group_frame, textvariable=self.group_notice_var, 
            fg="green", width=18, anchor="w"
        )
        self.group_notice_label.pack(side=tk.LEFT)
    
    def _create_left_panel_in_container(self, container):
        """Create left panel (Project List) in container"""
        self.left_frame = tk.Frame(container)
        self.left_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 5))
        
        # Project list panel
        self.project_panel = ProjectListPanel(
            self.left_frame, self.project_manager
        )
    
    def _create_right_panel_in_container(self, container):
        """Create right panel (Group List) in container"""
        self.right_frame = tk.Frame(container)
        self.right_frame.grid(row=2, column=1, sticky="nsew", padx=(5, 0))
        
        # Group list panel
        from .group_ui import GroupListPanel
        self.group_panel = GroupListPanel(
            self.right_frame, self.project_manager
        )
    
    def _setup_event_handlers(self):
        """Setup event handlers"""
        # Connect project panel changes to refresh other panels
        if self.project_panel:
            self.project_panel.on_project_changed = self._on_project_changed
        
        # Connect group panel changes  
        if hasattr(self, 'group_panel') and self.group_panel:
            self.group_panel.on_group_changed = self._on_group_changed
    
    def _create_project(self):
        """Create a new project"""
        project_name = self.project_name_var.get().strip()
        self.notice_var.set("")

        # Validate project name
        name_error = ValidationHelper.validate_required_field(project_name, "Project name")
        if name_error:
            messagebox.showerror("Error", name_error)
            return

        # Get parent and sync directories
        parent_dir = self.structure_manager.get_parent_directory()
        sync_dir = self.structure_manager.get_sync_directory()
        project_path = os.path.join(parent_dir, project_name)
        sync_project_path = os.path.join(sync_dir, project_name) if sync_dir else None

        # Check if project already exists
        if os.path.exists(project_path):
            messagebox.showerror("Error", f"Project '{project_name}' already exists.")
            return

        try:
            # Create project folders
            structure = self.structure_manager.load_structure()
            self.structure_manager.create_project_folders(project_path, structure, sync_project_path)

            # Add to project list
            project = self.project_manager.add_project(project_name)

            # Refresh UI
            self.project_panel.refresh()

            # Show success message
            self.notice_var.set(f"Project '{project_name}' Created!")
            self.project_name_var.set("")  # Clear input

        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _create_group(self):
        """Create a new project group"""
        from tkinter import messagebox
        
        group_name = self.group_name_var.get().strip()
        self.group_notice_var.set("")
        
        # Validate group name
        name_error = ValidationHelper.validate_required_field(group_name, "Group name")
        if name_error:
            messagebox.showerror("Error", name_error)
            return
        
        try:
            # Create the group
            group = self.project_manager.add_group(group_name)
            
            # Show success message
            self.group_notice_var.set(f"Group '{group_name}' Created!")
            self.group_name_var.set("")  # Clear input
            
            # Refresh project panel if needed
            if hasattr(self, 'project_panel') and self.project_panel:
                self.project_panel.refresh()
                
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create group: {e}")
    
    def _on_project_changed(self):
        """Handle project list changes"""
        # Could add additional logic here if needed
        pass
    
    def _on_group_changed(self):
        """Handle group list changes"""
        # Refresh project panel to update group names in dropdowns
        if hasattr(self, 'project_panel') and self.project_panel:
            self.project_panel.refresh()


def main():
    """Main entry point"""
    app = MainApplication()
    app.run()


if __name__ == "__main__":
    main()
