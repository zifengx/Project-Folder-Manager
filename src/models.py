"""
Project data model and business logic
"""
import os
import json
import datetime
from typing import List, Dict, Optional
from .config import STRUCTURE_JSON, PROJECT_LISTS_FILE, STATUS_ACTIVE, PROGRAM_ROOT, PROJECT_GROUPS_FILE
import sys
import shutil
import tempfile


class ProjectGroup:
    """Represents a project group"""
    
    def __init__(self, id: int, name: str, description: str = ""):
        self.id = id
        self.name = name
        self.description = description
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProjectGroup':
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            description=data.get("description", "")
        )


class Project:
    """Represents a project with metadata"""
    
    def __init__(self, id: int, name: str, description: str = "", 
                 status: str = STATUS_ACTIVE, start_date: str = "", end_date: str = "", group_id: int = 0):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.start_date = start_date or datetime.date.today().isoformat()
        self.end_date = end_date
        self.group_id = group_id
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "group_id": self.group_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=data.get("status", STATUS_ACTIVE),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            group_id=data.get("group_id", 0)
        )


class ProjectManager:
    """Manages project data and operations"""
    
    def __init__(self):
        self._ensure_project_lists_file()
    
    def _ensure_project_lists_file(self):
        """Ensure project lists file exists, copy from bundle if needed"""
        if not os.path.exists(PROJECT_LISTS_FILE):
            try:
                if getattr(sys, 'frozen', False):
                    src = os.path.join(sys._MEIPASS, "project_lists.json")
                    if os.path.exists(src):
                        shutil.copyfile(src, PROJECT_LISTS_FILE)
                else:
                    default_file = os.path.join(os.path.dirname(PROGRAM_ROOT), "project_lists.json")
                    if os.path.exists(default_file):
                        shutil.copyfile(default_file, PROJECT_LISTS_FILE)
            except Exception:
                pass
    
    def load_projects(self) -> List[Project]:
        """Load all projects from file"""
        if os.path.exists(PROJECT_LISTS_FILE):
            try:
                with open(PROJECT_LISTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [Project.from_dict(proj_data) for proj_data in data]
            except Exception:
                pass
        return []
    
    def save_projects(self, projects: List[Project]):
        """Save projects to file"""
        data = [proj.to_dict() for proj in projects]
        with open(PROJECT_LISTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_next_id(self, projects: List[Project]) -> int:
        """Get next available project ID"""
        if not projects:
            return 1
        return max(proj.id for proj in projects) + 1
    
    def add_project(self, name: str, description: str = "", status: str = STATUS_ACTIVE, group_id: int = 0) -> Project:
        """Add a new project"""
        projects = self.load_projects()
        
        # Check for duplicate names
        if any(proj.name == name for proj in projects):
            raise ValueError(f"Project '{name}' already exists")
        
        new_project = Project(
            id=self.get_next_id(projects),
            name=name,
            description=description,
            status=status,
            group_id=group_id
        )
        
        projects.append(new_project)
        self.save_projects(projects)
        return new_project
    
    def update_project(self, project: Project):
        """Update an existing project"""
        projects = self.load_projects()
        for i, proj in enumerate(projects):
            if proj.id == project.id:
                projects[i] = project
                self.save_projects(projects)
                return
        raise ValueError(f"Project with ID {project.id} not found")
    
    def delete_project(self, project_id: int):
        """Delete a project"""
        projects = self.load_projects()
        projects = [proj for proj in projects if proj.id != project_id]
        self.save_projects(projects)
    
    def load_groups(self) -> List[ProjectGroup]:
        """Load all project groups from file"""
        if os.path.exists(PROJECT_GROUPS_FILE):
            try:
                with open(PROJECT_GROUPS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [ProjectGroup.from_dict(group_data) for group_data in data]
            except Exception:
                pass
        return []
    
    def save_groups(self, groups: List[ProjectGroup]):
        """Save project groups to file"""
        data = [group.to_dict() for group in groups]
        with open(PROJECT_GROUPS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_next_group_id(self, groups: List[ProjectGroup]) -> int:
        """Get next available group ID"""
        if not groups:
            return 1
        return max(group.id for group in groups) + 1
    
    def add_group(self, name: str, description: str = "") -> ProjectGroup:
        """Add a new project group"""
        groups = self.load_groups()
        
        # Check for duplicate names
        if any(group.name == name for group in groups):
            raise ValueError(f"Group '{name}' already exists")
        
        new_group = ProjectGroup(
            id=self.get_next_group_id(groups),
            name=name,
            description=description
        )
        
        groups.append(new_group)
        self.save_groups(groups)
        return new_group
    
    def get_group_by_id(self, group_id: int) -> Optional[ProjectGroup]:
        """Get a group by its ID"""
        groups = self.load_groups()
        for group in groups:
            if group.id == group_id:
                return group
        return None


class StructureManager:
    """Manages folder structure templates"""
    
    def __init__(self):
        self._ensure_structure_file()
    
    def _ensure_structure_file(self):
        """Ensure structure file exists, copy from bundle if needed"""
        temp_json = os.path.join(tempfile.gettempdir(), "project_folder_structure.json")
        bundled_json = None
        
        if getattr(sys, 'frozen', False):
            bundled_json = os.path.join(sys._MEIPASS, "project_folder_structure.json")

        def try_copy(src_path, dst_path):
            with open(src_path, "r", encoding="utf-8") as src, open(dst_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())

        if not os.path.exists(STRUCTURE_JSON):
            if bundled_json and os.path.exists(bundled_json):
                try_copy(bundled_json, STRUCTURE_JSON)
                return
            if os.path.exists(temp_json):
                try_copy(temp_json, STRUCTURE_JSON)
                return
            raise FileNotFoundError(f"Structure file '{STRUCTURE_JSON}' not found")
        
        if os.path.getsize(STRUCTURE_JSON) == 0:
            if bundled_json and os.path.exists(bundled_json):
                try_copy(bundled_json, STRUCTURE_JSON)
                return
            if os.path.exists(temp_json):
                try_copy(temp_json, STRUCTURE_JSON)
                return
            raise ValueError(f"Structure file '{STRUCTURE_JSON}' is empty")
    
    def load_structure(self) -> Dict:
        """Load folder structure template"""
        with open(STRUCTURE_JSON, encoding="utf-8") as f:
            return json.load(f)
    
    def save_structure(self, structure: Dict):
        """Save folder structure template"""
        with open(STRUCTURE_JSON, "w", encoding="utf-8") as f:
            json.dump(structure, f, indent=4, ensure_ascii=False)
    
    def create_project_folders(self, parent_path: str, structure: Dict, sync_path: str = None):
        """Create project folder structure with sync/manual/auto logic"""
        
        if not sync_path or os.path.normpath(sync_path) == os.path.normpath(parent_path):
            # Legacy behavior: create everything in parent_path
            os.makedirs(parent_path, exist_ok=True)
            self._create_items(parent_path, structure.get("folders", []))
            for file_item in structure.get("files", []):
                file_path = os.path.join(parent_path, file_item["name"])
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("")
            return

        # Check if there are any auto items
        has_auto_items = self._has_auto_items(structure)
        
        # Always create parent directory
        os.makedirs(parent_path, exist_ok=True)
        
        # Only create sync directory if there are auto items
        if has_auto_items:
            os.makedirs(sync_path, exist_ok=True)
        
        # Place auto items in sync_path, manual items in parent_path
        self._create_items_sync(parent_path, sync_path if has_auto_items else None, structure.get("folders", []))
        self._create_files_sync(parent_path, sync_path if has_auto_items else None, structure.get("files", []))

    def _has_auto_items(self, structure: Dict) -> bool:
        """Check if structure contains any auto items (folders or files)"""
        # Check files
        for file_item in structure.get("files", []):
            if file_item.get("attribute", "manual") == "auto":
                return True
        
        # Check folders recursively
        def check_folders(folders):
            for folder in folders:
                if folder.get("attribute", "manual") == "auto":
                    return True
                if "folders" in folder and check_folders(folder["folders"]):
                    return True
            return False
        
        return check_folders(structure.get("folders", []))

    def _create_items_sync(self, parent_path, sync_path, items):
        for item in items:
            sync_mode = item.get("attribute", "manual")
            folder_name = item["name"]
            if sync_mode == "auto" and sync_path:
                # Create folder in sync directory
                sync_folder = os.path.join(sync_path, folder_name)
                os.makedirs(sync_folder, exist_ok=True)
                # Create shortcut/symlink in parent directory
                link_path = os.path.join(parent_path, folder_name)
                self._create_shortcut(link_path, sync_folder)
                # Recurse into subfolders (create subfolders in sync directory)
                if "folders" in item:
                    self._create_items_sync(sync_folder, sync_folder, item["folders"])
            else:
                # Create folder in parent directory (for manual items or when no sync_path)
                manual_folder = os.path.join(parent_path, folder_name)
                os.makedirs(manual_folder, exist_ok=True)
                # Recurse into subfolders (keep using sync_path for potential auto subfolders)
                if "folders" in item:
                    self._create_items_sync(manual_folder, sync_path, item["folders"])

    def _create_files_sync(self, parent_path, sync_path, files):
        for file_item in files:
            sync_mode = file_item.get("attribute", "manual")
            file_name = file_item["name"]
            if sync_mode == "auto" and sync_path:
                # Create file in sync directory
                sync_file = os.path.join(sync_path, file_name)
                with open(sync_file, "w", encoding="utf-8") as f:
                    f.write("")
                # Create shortcut/symlink in parent directory
                link_path = os.path.join(parent_path, file_name)
                self._create_shortcut(link_path, sync_file)
            else:
                # Create file in parent directory (for manual items or when no sync_path)
                manual_file = os.path.join(parent_path, file_name)
                with open(manual_file, "w", encoding="utf-8") as f:
                    f.write("")

    def _create_shortcut(self, link_path, target_path):
        """Create a shortcut (.lnk on Windows, symlink on other platforms)"""
        import sys
        import os
        is_windows = sys.platform.startswith("win")
        try:
            if is_windows:
                # Use pywin32 to create Windows .lnk shortcut (works for both files and folders)
                try:
                    import win32com.client
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortcut(link_path + ".lnk")
                    shortcut.TargetPath = target_path
                    # Set working directory to parent directory of target for better behavior
                    shortcut.WorkingDirectory = os.path.dirname(target_path)
                    shortcut.Save()
                except Exception:
                    # Fallback: create symlink (may work without admin on newer Windows)
                    if os.path.isdir(target_path):
                        os.symlink(target_path, link_path, target_is_directory=True)
                    else:
                        os.symlink(target_path, link_path)
            else:
                # Create symlink on non-Windows platforms
                if os.path.isdir(target_path):
                    os.symlink(target_path, link_path, target_is_directory=True)
                else:
                    os.symlink(target_path, link_path)
        except Exception as e:
            # Fallback: Create a text file indicating the link
            try:
                with open(link_path + "_link.txt", "w") as f:
                    f.write(f"Link to: {target_path}\n")
                    f.write(f"Error creating shortcut: {str(e)}\n")
                    if is_windows:
                        f.write("Try installing pywin32: pip install pywin32\n")
                    else:
                        f.write("Check file permissions and try again.\n")
            except:
                pass
    
    def _create_items(self, base_path: str, items: List[Dict]):
        """Recursively create folder items"""
        for item in items:
            folder_path = os.path.join(base_path, item["name"])
            os.makedirs(folder_path, exist_ok=True)
            if "folders" in item:
                self._create_items(folder_path, item["folders"])
    
    def get_parent_directory(self) -> str:
        """Get configured parent directory"""
        try:
            structure = self.load_structure()
            path = structure.get("parent_directory", PROGRAM_ROOT).strip() or PROGRAM_ROOT
            return os.path.normpath(path)
        except Exception:
            return PROGRAM_ROOT
    
    def set_parent_directory(self, path: str):
        """Set parent directory"""
        structure = self.load_structure()
        structure["parent_directory"] = os.path.normpath(path)
        self.save_structure(structure)
    
    def get_sync_directory(self) -> str:
        """Get configured sync directory"""
        try:
            structure = self.load_structure()
            sync_dir = structure.get("sync_directory", "").strip()
            path = sync_dir if sync_dir else PROGRAM_ROOT
            return os.path.normpath(path)
        except Exception:
            return PROGRAM_ROOT
    
    def set_sync_directory(self, path: str):
        """Set sync directory"""
        structure = self.load_structure()
        structure["sync_directory"] = os.path.normpath(path)
        self.save_structure(structure)
