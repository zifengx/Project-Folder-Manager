# Project Folder Manager

A user-friendly GUI tool to manage project folder structures and maintain a persistent, editable project list.

## Features

- **Create new project folders** with a single click, using a configurable template.
- **Persistent Project List**: Manage a list of projects (ID, name, description, status) in a dedicated panel.
- **Visual and Raw JSON Editors**: Edit project details visually or directly in JSON.
- **Status Management**: Mark projects as Active or Deprecated (with strikethrough for deprecated projects).
- **Dialogs and Dropdowns**: All dialogs are centered and status is selected via dropdown.
- **Configurable Structure**: Edit the folder/file structure template via a visual or JSON editor.
- **Standalone Executable**: Build for Windows or Mac with all data files bundled.

## Usage

### As Python Script

1. Install Python 3.x.
2. Run:

   ```
   python main.py
   ```

### As Windows Executable

1. Build the executable (see below) or use a prebuilt one.
2. Double-click the `.exe` in the `dist` folder.

### As Mac Executable

1. Build using the provided `main_mac.spec` (see below).
2. Run the app from the `dist` folder.

## Building the Executable

1. Install [PyInstaller](https://pyinstaller.org/):
   ```
   pip install pyinstaller
   ```
2. Build using the provided spec file:
   ```
   pyinstaller main.spec
   ```
   or for Mac:
   ```
   pyinstaller main_mac.spec
   ```
   The executable will be in the `dist` folder.

   Or use the command:
   ```
   pyinstaller --noconsole --onefile --add-data "project_folder_structure.json;." --add-data "project_lists.json;." main.py
   ```

3. The files `project_folder_structure.json` and `project_lists.json` are bundled and used as defaults on first run.

## Project List Management

- The right panel shows all projects in a persistent list (`project_lists.json`).
- Edit, add, or remove projects visually or via raw JSON.
- Status can be set to Active or Deprecated (deprecated projects are shown with strikethrough).
- All changes are saved to `project_lists.json`.

## Customizing the Structure

- Use the "Config" section to edit the folder/file template.
- Set the default parent directory for new projects.

## Project Structure

- `main.py` - Main application logic and GUI.
- `project_folder_structure.json` - Folder/file template and default parent directory.
- `project_lists.json` - Persistent project list (bundled and used as default).
- `main.spec`, `main_mac.spec` - PyInstaller build configs for Windows and Mac.
- `build_win_instructions.txt` - Build instructions for Windows.
- `README.md` - This file.

## License

MIT License (add your own if needed).
