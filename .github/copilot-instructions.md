# Project Folder Manager - AI Coding Instructions

## Architecture Overview

This is a **Tkinter-based desktop application** that creates standardized project folder structures and manages a persistent project list. The app uses JSON files for both configuration and data persistence.

### Core Components
- **`main.py`**: Single-file application containing all GUI logic and project management
- **`project_folder_structure.json`**: Template defining the folder/file structure for new projects
- **`project_lists.json`**: Persistent storage for project metadata (ID, name, description, status, dates)

## Key Data Flow Patterns

### Project Creation Workflow
1. User inputs project name → `create_project_gui()`
2. Loads structure from `project_folder_structure.json` → `load_structure()`
3. Creates folders recursively → `create_items()`
4. Auto-adds project to list with today's date → `save_project_list()`

### Dual Editor Pattern
The app consistently uses **Visual Editor + Raw JSON** tabs for:
- Project List management (`proj_tree` + `proj_text`)
- Structure configuration (`tree` + `text`)

Both editors sync bidirectionally - changes in visual editor update JSON, and vice versa.

## Critical File Handling

### PyInstaller Bundle Logic
```python
# Files are bundled into executable and copied to program directory on first run
if getattr(sys, 'frozen', False):
    bundled_json = os.path.join(sys._MEIPASS, STRUCTURE_FILENAME)
```

**Always use this pattern** when adding new config files - bundle them in `.spec` files and implement fallback copying.

## UI Convention Patterns

### Dialog Centering
All dialogs use this exact centering logic:
```python
parent_x = parent.winfo_rootx()
parent_y = parent.winfo_rooty()
parent_w = parent.winfo_width()
parent_h = parent.winfo_height()
x = parent_x + (parent_w // 2) - (dialog_w // 2)
y = parent_y + (parent_h // 2) - (dialog_h // 2)
dialog.geometry(f"+{x}+{y}")
```

### Status Management
Projects have `"active"` or `"deprecated"` status. Deprecated projects:
- Show with strikethrough styling: `font=("Arial", 10, "overstrike")`
- Auto-populate `end_date` when status changes to deprecated
- Clear `end_date` when status changes back to active

## Build System

### Version Management
- `APP_NAME` and `VERSION` constants in `main.py` drive the build process
- `build.py` automatically updates spec files with current version
- Use `py build.py` instead of manual PyInstaller commands

### Critical Build Files
- `main_win.spec` / `main_mac.spec`: Platform-specific PyInstaller configs
- Must include: `datas=[('project_folder_structure.json', '.'), ('project_lists.json', '.')]`

## Development Workflows

### Adding New Config Files
1. Add to `datas=` in both `.spec` files
2. Implement bundle extraction logic following `ensure_structure_json()` pattern
3. Test both script and frozen executable modes

### UI Modifications
- Use `grid()` for main layout, `pack()` for buttons within frames
- Always set `dialog.transient(parent)` and `dialog.grab_set()` for modal dialogs
- Follow the two-tab pattern (Visual Editor + Raw JSON) for complex data editing

### Testing Changes
Run both ways to ensure compatibility:
```bash
python main.py                    # Script mode
py build.py && .\dist\*.exe      # Executable mode
```

## Layout Structure

Top Section (Two Columns):
┌─────────────────────────────────┬─────────────────────────────────┐
│ Project Name: [input] [Create]  │ Project Group: [input] [Create] │ 
└─────────────────────────────────┼─────────────────────────────────┘
┌─────────────────────────────────┼─────────────────────────────────┐
│ Left Panel: Structure Config    │ Right Panel: Project List       │
└─────────────────────────────────┴─────────────────────────────────┘
---
## Additional Notes
1. Update this instructions if needed when we we update this project files. 


