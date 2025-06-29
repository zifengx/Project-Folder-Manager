import re
import os
import subprocess

main_py = "main.py"
spec_files = ["main.spec"]

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
    with open(specfile, "w", encoding="utf-8") as f:
        for line in lines:
            # Replace name='...' with new app name and version
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
    update_version_in_main_py(new_version)
    for specfile in spec_files:
        update_name_in_spec(specfile, app_name, new_version)
    print(f"Updated VERSION to: {new_version} and updated spec file names.")

if __name__ == "__main__":
    main()
    # Build with PyInstaller after updating version
    subprocess.run(["pyinstaller", "main.spec"])