"""
Main application window and coordinator
"""
import tkinter as tk
from tkinter import messagebox
import os
from .config import *
from .models import ProjectManager, StructureManager
from .project_ui import ProjectListPanel
from .structure_ui import StructurePanel, ParentDirectoryPanel
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
        """Create the main UI layout"""
        # Left panel (main controls)
        self._create_left_panel()
        
        # Right panel (project list)
        self._create_right_panel()
    
    def _create_left_panel(self):
        """Create left panel with project creation and configuration"""
        self.main_frame = tk.Frame(self.root, width=400)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Project creation section
        self._create_project_creation_section()
        
        # Add some spacing
        self.main_frame.grid_rowconfigure(1, minsize=10)
        
        # Configuration section
        self._create_config_section()
    
    def _create_project_creation_section(self):
        """Create project creation controls"""
        # Project name input
        tk.Label(self.main_frame, text="Project Name:").grid(
            row=0, column=0, padx=(10, 0), pady=10, sticky="e"
        )
        
        self.project_name_var = tk.StringVar()
        tk.Entry(self.main_frame, textvariable=self.project_name_var, width=32).grid(
            row=0, column=1, padx=(0, 0), pady=10, sticky="w"
        )
        
        tk.Button(self.main_frame, text="Create Project", command=self._create_project).grid(
            row=0, column=2, padx=(4, 0), pady=10, sticky="w"
        )
        
        # Status/notice label
        self.notice_var = tk.StringVar(value=" ")
        self.notice_label = tk.Label(
            self.main_frame, textvariable=self.notice_var, 
            fg="green", width=24, anchor="w"
        )
        self.notice_label.grid(row=0, column=3, padx=(10, 10), pady=10, sticky="w")
    
    def _create_config_section(self):
        """Create configuration section"""
        self.config_frame = tk.LabelFrame(
            self.main_frame, text="Config", padx=5, pady=5
        )
        self.config_frame.grid(
            row=2, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="nsew"
        )
        self.config_frame.columnconfigure(0, weight=1)
        self.config_frame.rowconfigure(0, weight=1)
        
        # Parent directory panel
        self.parent_dir_panel = ParentDirectoryPanel(
            self.config_frame, self.structure_manager
        )
        
        # Structure panel
        self.structure_panel = StructurePanel(
            self.config_frame, self.structure_manager
        )
    
    def _create_right_panel(self):
        """Create right panel with project list"""
        self.right_frame = tk.Frame(self.root, width=600)
        self.right_frame.grid(
            row=0, column=1, rowspan=10, sticky="nswe", 
            padx=(10, 10), pady=10
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
        
        # Get parent directory
        parent_dir = self.structure_manager.get_parent_directory()
        project_path = os.path.join(parent_dir, project_name)
        
        # Check if project already exists
        if os.path.exists(project_path):
            messagebox.showerror("Error", f"Project '{project_name}' already exists.")
            return
        
        try:
            # Create project folders
            structure = self.structure_manager.load_structure()
            self.structure_manager.create_project_folders(project_path, structure)
            
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
