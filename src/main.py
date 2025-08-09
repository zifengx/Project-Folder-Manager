"""
Main application window and coordinator
"""
import tkinter as tk
from tkinter import messagebox
import os
import sys
import ctypes
import subprocess
from .config import *
from .models import ProjectManager, StructureManager
from .project_ui import ProjectListPanel
from .structure_ui import StructurePanel, ParentDirectoryPanel, SyncDirectoryPanel
from .ui_utils import ValidationHelper


def is_admin():
    """Check if running with administrator privileges on Windows"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    """Restart the application with administrator privileges"""
    try:
        if getattr(sys, 'frozen', False):
            # Running as executable
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, "", None, 1
            )
        else:
            # Running as script
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join([f'"{arg}"' for arg in sys.argv]), None, 1
            )
        return True
    except:
        return False


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
            # Check for admin privileges on Windows
            if sys.platform.startswith("win") and not is_admin():
                # Create a temporary window to show the prompt
                temp_root = tk.Tk()
                temp_root.withdraw()  # Hide the window
                
                result = messagebox.askyesno(
                    "Administrator Privileges Required",
                    "This application needs administrator privileges to create shortcuts/symlinks.\n\n"
                    "Would you like to restart with administrator privileges?\n\n"
                    "Click 'No' to continue without shortcuts (text files will be created instead).",
                    parent=temp_root
                )
                
                temp_root.destroy()
                
                if result:
                    if run_as_admin():
                        return  # Exit current instance
                    else:
                        messagebox.showerror("Error", "Failed to restart with administrator privileges.")
            
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
        """Create the main UI layout"""
        # Create a container frame for better control
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure container grid
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=0)
        container.grid_rowconfigure(0, weight=0)  # Project creation row
        container.grid_rowconfigure(1, weight=1)  # Main panels row
        
        # Project creation section (spans both columns)
        self._create_project_creation_section_in_container(container)
        
        # Left panel (config section)
        self._create_left_panel_in_container(container)
        
        # Right panel (project list)
        self._create_right_panel_in_container(container)
    
    def _create_project_creation_section_in_container(self, container):
        """Create project creation controls in container"""
        project_frame = tk.Frame(container)
        project_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Project name input
        tk.Label(project_frame, text="Project Name:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.project_name_var = tk.StringVar()
        tk.Entry(project_frame, textvariable=self.project_name_var, width=32).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(project_frame, text="Create Project", command=self._create_project).pack(side=tk.LEFT, padx=(0, 10))
        
        # Status/notice label
        self.notice_var = tk.StringVar(value=" ")
        self.notice_label = tk.Label(
            project_frame, textvariable=self.notice_var, 
            fg="green", width=24, anchor="w"
        )
        self.notice_label.pack(side=tk.LEFT)
    
    def _create_left_panel_in_container(self, container):
        """Create left panel (config) in container"""
        self.config_frame = tk.LabelFrame(
            container, text="Config", padx=5, pady=5
        )
        self.config_frame.grid(
            row=1, column=0, sticky="nsew", padx=(0, 5)
        )
        self.config_frame.columnconfigure(0, weight=1)
        self.config_frame.rowconfigure(2, weight=1)  # Give weight to structure panel (moved to row 2)
        
        # Parent directory panel
        self.parent_dir_panel = ParentDirectoryPanel(
            self.config_frame, self.structure_manager
        )
        
        # Sync directory panel
        self.sync_dir_panel = SyncDirectoryPanel(
            self.config_frame, self.structure_manager
        )
        
        # Structure panel
        self.structure_panel = StructurePanel(
            self.config_frame, self.structure_manager
        )
    
    def _create_right_panel_in_container(self, container):
        """Create right panel (project list) in container"""
        self.right_frame = tk.Frame(container, width=600)
        self.right_frame.grid(
            row=1, column=1, sticky="nsew", padx=(5, 0)
        )
        self.right_frame.grid_propagate(False)
        
        # Project list panel
        self.project_panel = ProjectListPanel(
            self.right_frame, self.project_manager
        )
    
    def _setup_event_handlers(self):
        """Setup event handlers"""
        # Connect project panel changes to refresh other panels
        if self.project_panel:
            self.project_panel.on_project_changed = self._on_project_changed
    
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
    
    def _on_project_changed(self):
        """Handle project list changes"""
        # Could add additional logic here if needed
        pass


def main():
    """Main entry point"""
    app = MainApplication()
    app.run()


if __name__ == "__main__":
    main()
