# Project Folder Manager

A simple GUI tool to create project folder structures based on a configurable template.

## Features

- Create a new project folder structure with one click.
- Configure the folder and txt file structure via a user-friendly GUI (no need to edit JSON).
- GUI for selecting parent directory and project name.
- Edit the structure and parent directory from the app (top menu).
- All configuration and structure data are stored in a local SQLite database (`settings.db`).
- Packaged as a standalone Windows executable.

## Usage

### As Python Script

1. Install Python 3.x.
2. Install dependencies (if any).
3. Run:
   ```
   python main.py
   ```

### As Windows Executable

1. Download or build the `.exe` (see below).
2. Double-click `ProjectFolderManager_v1.0.0.exe` in the `dist` folder.

## Building the Executable

1. Install [PyInstaller](https://pyinstaller.org/):
   ```
   pip install pyinstaller
   ```
2. Build using the provided spec file:
   ```
   pyinstaller main.spec
   ```
   The executable will be in the `dist` folder.

   Or use the command:
   ```
   pyinstaller --noconsole --onefile main.py
   ```

3. No extra data files are needed.  
   All configuration and structure data are stored in `settings.db` automatically when you run the program.

## Customizing the Structure

- Use the "Config" menu in the app to edit folders and txt files.
- Use the "Parent Directory" menu to set the default parent directory for new projects.

## Project Structure

- `main.py` - Entry point.
- `gui.py` - GUI logic and settings/structure database.
- `core.py` - Core logic for structure creation.
- `main.spec` - PyInstaller build config.
- `.gitignore` - Ignore Python/IDE/build files.

## License

MIT License (add your own if needed).
