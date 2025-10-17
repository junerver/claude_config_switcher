"""
PyInstaller build script for creating standalone executable.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(result.returncode)
    return result

def build_executable():
    """Build standalone executable using PyInstaller."""
    print("Building Claude Code Configuration Switcher executable...")

    # Get project root
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")

    # Ensure we're in project root
    os.chdir(project_root)

    # Clean previous builds
    print("Cleaning previous builds...")
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)

    # PyInstaller command
    cmd = [
        "uv", "run", "pyinstaller",
        "--name=ClaudeConfigSwitcher",
        "--onefile",
        "--windowed",  # No console window for GUI app
        "--add-data=src;src",
        "--hidden-import=customtkinter",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=tkinter.simpledialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "--icon=assets/icons/app.ico" if (project_root / "assets/icons/app.ico").exists() else "",
        "src/main.py"
    ]

    # Remove empty icon parameter
    cmd = [arg for arg in cmd if arg != ""]

    print(f"Build command: {' '.join(cmd)}")
    result = run_command(cmd)

    if result.returncode == 0:
        print("✓ Build completed successfully!")

        # Show output file info
        exe_file = dist_dir / "ClaudeConfigSwitcher.exe"
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"✓ Executable created: {exe_file}")
            print(f"✓ File size: {size_mb:.1f} MB")
        else:
            print("⚠️ Executable not found in dist directory")
    else:
        print("✗ Build failed")
        sys.exit(1)

def create_portable_package():
    """Create a portable package with executable and dependencies."""
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    portable_dir = project_root / "portable"

    exe_file = dist_dir / "ClaudeConfigSwitcher.exe"
    if not exe_file.exists():
        print("⚠️ Executable not found. Run build first.")
        return

    print("Creating portable package...")

    # Clean previous portable package
    if portable_dir.exists():
        shutil.rmtree(portable_dir)

    portable_dir.mkdir(parents=True)

    # Copy executable
    shutil.copy2(exe_file, portable_dir / "ClaudeConfigSwitcher.exe")

    # Create README for portable package
    readme_content = """# Claude Code Configuration Switcher - Portable Version

## About
A desktop GUI application for managing and switching between different Claude Code configuration profiles.

## Usage
1. Double-click `ClaudeConfigSwitcher.exe` to launch the application
2. The application will automatically detect your Claude Code configuration
3. Create, edit, and manage configuration profiles
4. Double-click profiles to apply them to Claude Code

## Configuration
- Application settings are stored in your user profile directory
- Backups are created automatically before profile changes
- Logs are written to your system's log directory

## Troubleshooting
- Ensure Claude Code is installed and configured
- Check that you have write permissions to your Claude Code settings file
- Run the executable with administrator privileges if needed

## Support
For issues and support, please visit the project repository.
"""

    with open(portable_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"✓ Portable package created: {portable_dir}")
    print(f"✓ Package size: {sum(f.stat().st_size for f in portable_dir.rglob('*') if f.is_file()) / (1024*1024):.1f} MB")

def main():
    """Main build function."""
    import argparse

    parser = argparse.ArgumentParser(description="Build Claude Code Configuration Switcher")
    parser.add_argument("--portable", action="store_true", help="Create portable package")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts only")

    args = parser.parse_args()

    if args.clean:
        # Clean build artifacts
        project_root = Path(__file__).parent.parent
        print("Cleaning build artifacts...")

        for dir_name in ["dist", "build", "__pycache__"]:
            dir_path = project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"✓ Removed {dir_name}")

        # Clean Python cache files
        for pycache in project_root.rglob("__pycache__"):
            if pycache.is_dir():
                shutil.rmtree(pycache)

        print("✓ Clean completed")
        return

    # Build executable
    build_executable()

    # Create portable package if requested
    if args.portable:
        create_portable_package()

if __name__ == "__main__":
    main()