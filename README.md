# Project Folder Manager

A simple GUI tool to create project folder structures based on a configurable template.

## Features

- Create a new project folder structure with one click.
- Configure the folder and txt file structure via a user-friendly GUI (no need to edit JSON).
- GUI for selecting parent directory and project name.
- Edit the structure and parent directory from the app (top menu).
- All configuration and structure data are stored in `structure.json`.
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
2. Double-click `main.exe` in the `dist` folder.

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
   pyinstaller --noconsole --onefile --add-data "structure.json;." main.py
   ```

3. No extra data files are needed.  
   All configuration and structure data are stored in `structure.json` automatically when you run the program.

## Customizing the Structure

- Use the "Config" section in the app to edit folders and txt files.
- Use the "Parent Directory" setting to set the default parent directory for new projects.

## Project Structure

- `main.py` - All logic and GUI.
- `structure.json` - Folder/file template and default parent directory.
- `main.spec` - PyInstaller build config.
- `.gitignore` - Ignore Python/IDE/build files.

## License

MIT License (add your own if needed).
