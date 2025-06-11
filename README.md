# Project Folder Manager

A simple GUI tool to create project folder structures based on a configurable JSON template.

## Features

- Create a new project folder structure with one click.
- Configure the folder and file structure via a JSON file (`structure.json`).
- GUI for selecting parent directory and project name.
- Edit the structure JSON directly from the app (Config menu).
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

## Customizing the Structure

- Edit `structure.json` to define your folder and file template.
- Or use the "Config" menu in the app to edit the structure.

Example `structure.json`:
```json
{
    "folders": [
        {
            "name": "backup",
            "folders": [
                {"name": "database"},
                {"name": "images"}
            ]
        },
        {"name": "files"},
        {"name": "queries"}
    ],
    "files": [
        {"name": "code.txt"}
    ]
}
```

## Project Structure

- `main.py` - Entry point.
- `gui.py` - GUI logic.
- `core.py` - Core logic for structure creation.
- `structure.json` - Folder/file template.
- `main.spec` - PyInstaller build config.
- `.gitignore` - Ignore Python/IDE/build files.

## License

MIT License (add your own if needed).
