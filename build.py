import re
import os
import subprocess
import sys

main_py = "main.py"
spec_files = ["main_win.spec","main_mac.spec"]

def get_app_name_and_version():
    app_name = None
    version = None
    with open(main_py, encoding="utf-8") as f:
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

def update_version_in_main_py(new_version):
    with open(main_py, encoding="utf-8") as f:
        lines = f.readlines()
    with open(main_py, "w", encoding="utf-8") as f:
        for line in lines:
            if re.match(r'\s*VERSION\s*=\s*"[^"]*"', line):
                f.write(f'VERSION = "{new_version}"\n')
            else:
                f.write(line)

def update_name_in_spec(specfile, app_name, new_version):
    if not os.path.exists(specfile):
        return
    with open(specfile, encoding="utf-8") as f:
        lines = f.readlines()
    new_name = f"{app_name} v{new_version}"
    new_name_app = f"{new_name}.app"
    with open(specfile, "w", encoding="utf-8") as f:
        for line in lines:
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

def main():
    app_name, current_version = get_app_name_and_version()
    if not app_name or not current_version:
        print("Could not find APP_NAME or VERSION in main.py")
        return
    print(f"Current app name: {app_name}")
    print(f"Current version: {current_version}")
    new_version = input("Enter new version number: ").strip()
    if not new_version:
        print("No version entered. Aborting.")
        return
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print("Invalid version format. Please use Semantic Versioning (MAJOR.MINOR.PATCH), e.g., '2.1.2'. Aborting.")
        return
    update_version_in_main_py(new_version)
    for specfile in spec_files:
        update_name_in_spec(specfile, app_name, new_version)
    print(f"Updated VERSION to: {new_version} and updated spec file names.")

if __name__ == "__main__":
    main()
    # Build with PyInstaller after updating version
    if sys.platform == "win32":
        subprocess.run(["pyinstaller", "main_win.spec"])
    elif sys.platform == "darwin":
        subprocess.run(["pyinstaller", "main_mac.spec"])
    else:
        print("Unsupported OS for automatic build. Please run PyInstaller manually.")