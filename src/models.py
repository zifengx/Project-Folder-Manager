"""
Project data model and business logic
"""
import os
import json
import datetime
from typing import List, Dict, Optional
from .config import STRUCTURE_JSON, PROJECT_LISTS_FILE, STATUS_ACTIVE, PROGRAM_ROOT
import sys
import shutil
import tempfile


class Project:
    """Represents a project with metadata"""
    
    def __init__(self, id: int, name: str, description: str = "", 
                 status: str = STATUS_ACTIVE, start_date: str = "", end_date: str = ""):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.start_date = start_date or datetime.date.today().isoformat()
        self.end_date = end_date
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "start_date": self.start_date,
            "end_date": self.end_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=data.get("status", STATUS_ACTIVE),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", "")
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
    
    def add_project(self, name: str, description: str = "", status: str = STATUS_ACTIVE) -> Project:
        """Add a new project"""
        projects = self.load_projects()
        
        # Check for duplicate names
        if any(proj.name == name for proj in projects):
            raise ValueError(f"Project '{name}' already exists")
        
        new_project = Project(
            id=self.get_next_id(projects),
            name=name,
            description=description,
            status=status
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
    
    def create_project_folders(self, project_path: str, structure: Dict):
        """Create project folder structure"""
        os.makedirs(project_path)
        self._create_items(project_path, structure.get("folders", []))
        
        # Create files
        for file_item in structure.get("files", []):
            file_path = os.path.join(project_path, file_item["name"])
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("")
    
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
            return structure.get("parent_directory", PROGRAM_ROOT).strip() or PROGRAM_ROOT
        except Exception:
            return PROGRAM_ROOT
    
    def set_parent_directory(self, path: str):
        """Set parent directory"""
        structure = self.load_structure()
        structure["parent_directory"] = path
        self.save_structure(structure)
    
    def get_sync_directory(self) -> str:
        """Get configured sync directory"""
        try:
            structure = self.load_structure()
            sync_dir = structure.get("sync_directory", "").strip()
            return sync_dir if sync_dir else PROGRAM_ROOT
        except Exception:
            return PROGRAM_ROOT
    
    def set_sync_directory(self, path: str):
        """Set sync directory"""
        structure = self.load_structure()
        structure["sync_directory"] = path
        self.save_structure(structure)
