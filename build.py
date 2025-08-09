import re
import os
import subprocess
import sys

# Update paths for refactored structure
config_py = os.path.join("src", "config.py")
main_py = os.path.join("src", "main.py")
spec_files = ["main_win.spec", "main_mac.spec"]

def get_app_name_and_version():
    """Extract APP_NAME and VERSION from src/config.py"""
    app_name = None
    version = None
    
    if not os.path.exists(config_py):
        print(f"Error: {config_py} not found")
        return None, None
        
    with open(config_py, encoding="utf-8") as f:
        for line in f:
            m_name = re.match(r'\s*APP_NAME\s*=\s*"([^"]+)"', line)
            m_ver = re.match(r'\s*VERSION\s*=\s*"([^"]+)"', line)
            if m_name:
                app_name = m_name.group(1)
            if m_ver:
                version = m_ver.group(1)
            if app_name and version:
                break
    return app_name, version

def update_version_in_config_py(new_version):
    """Update VERSION in src/config.py"""
    with open(config_py, encoding="utf-8") as f:
        lines = f.readlines()
    with open(config_py, "w", encoding="utf-8") as f:
        for line in lines:
            if re.match(r'\s*VERSION\s*=\s*"[^"]*"', line):
                f.write(f'VERSION = "{new_version}"\n')
            else:
                f.write(line)

def update_name_in_spec(specfile, app_name, new_version):
    """Update the executable name in spec files"""
    if not os.path.exists(specfile):
        print(f"Warning: {specfile} not found")
        return
        
    with open(specfile, encoding="utf-8") as f:
        lines = f.readlines()
    
    new_name = f"{app_name} v{new_version}"
    new_name_app = f"{new_name}.app"
    
    with open(specfile, "w", encoding="utf-8") as f:
        for line in lines:
            # Keep main.py as entry point since it imports from src.main
            # No need to change the path anymore
                
            # Update all name='...' fields
            if "BUNDLE(" in line:
                # Next lines may contain name= for the BUNDLE
                f.write(line)
                continue
            if re.search(r"name='[^']*\.app'", line):
                # For BUNDLE, ensure .app suffix
                f.write(re.sub(r"name='[^']*\.app'", f"name='{new_name_app}'", line))
            else:
                # For other name fields
                f.write(re.sub(r"name='[^']*'", f"name='{new_name}'", line))

def validate_refactored_structure():
    """Ensure the refactored structure is complete"""
    required_files = [
        "src/main.py",
        "src/config.py", 
        "src/models.py",
        "src/ui_utils.py",
        "src/project_ui.py",
        "src/structure_ui.py",
        "project_folder_structure.json",
        "project_lists.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("Error: Missing required files for refactored structure:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    return True

def ensure_pywin32():
    """Ensure pywin32 is installed"""
    try:
        import win32com.shell
        import pythoncom
        print("✅ pywin32 is available")
        return True
    except ImportError:
        print("⚠️  pywin32 not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"], check=True)
            print("✅ pywin32 installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install pywin32")
            return False

def main():
    """Main build process"""
    print("=== Project Folder Manager Build Script ===")
    print("Building refactored version with modular structure")
    print()
    
    # Ensure pywin32 is installed on Windows
    if sys.platform == "win32":
        if not ensure_pywin32():
            print("Build aborted due to pywin32 installation failure.")
            return False
    
    # Validate refactored structure
    if not validate_refactored_structure():
        print("Build aborted due to missing files.")
        return False
    
    # Get current version info
    app_name, current_version = get_app_name_and_version()
    if not app_name or not current_version:
        print("Could not find APP_NAME or VERSION in src/config.py")
        return False
    
    print(f"Current app name: {app_name}")
    print(f"Current version: {current_version}")
    print()
    
    # Get new version from user
    new_version = input("Enter new version number (or press Enter to keep current): ").strip()
    if not new_version:
        new_version = current_version
        print(f"Using current version: {new_version}")
    else:
        if not re.match(r'^\d+\.\d+\.\d+$', new_version):
            print("Invalid version format. Please use Semantic Versioning (MAJOR.MINOR.PATCH), e.g., '2.1.5'. Aborting.")
            return False
        
        # Update version in config
        update_version_in_config_py(new_version)
        print(f"Updated VERSION to: {new_version}")
    
    # Update spec files
    for specfile in spec_files:
        update_name_in_spec(specfile, app_name, new_version)
        if os.path.exists(specfile):
            print(f"Updated {specfile}")
    
    print()
    print("=== Starting PyInstaller Build ===")
    return True

if __name__ == "__main__":
    result = main()
    if not result:
        sys.exit(1)
    
    # Build with PyInstaller after updating version
    try:
        if sys.platform == "win32":
            print("Building for Windows...")
            subprocess.run(["pyinstaller", "main_win.spec"], check=True)
            print("✅ Windows build completed successfully!")
        elif sys.platform == "darwin":
            print("Building for macOS...")
            subprocess.run(["pyinstaller", "main_mac.spec"], check=True)
            print("✅ macOS build completed successfully!")
        else:
            print("⚠️  Unsupported OS for automatic build. Please run PyInstaller manually.")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it with: pip install pyinstaller")
        sys.exit(1)