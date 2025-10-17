"""
Development environment setup script.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def check_prerequisites():
    """Check if prerequisites are installed."""
    print("Checking prerequisites...")

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 13):
        print(f"[WARN] Python {python_version.major}.{python_version.minor} detected.")
        print("   Python 3.13+ is recommended.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    else:
        print(f"[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Check uv
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] uv {result.stdout.strip()}")
        else:
            print("[ERROR] uv not found")
            return False
    except FileNotFoundError:
        print("[ERROR] uv not found. Please install uv first.")
        print("   Visit: https://github.com/astral-sh/uv")
        return False

    # Check git
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] {result.stdout.strip()}")
        else:
            print("[WARN] git not found - version control features will be limited")
    except FileNotFoundError:
        print("[WARN] git not found - version control features will be limited")

    return True

def setup_environment():
    """Set up the development environment."""
    print("\nSetting up development environment...")

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Install dependencies
    print("Installing dependencies...")
    if not run_command(["uv", "sync"]):
        print("✗ Failed to install dependencies")
        return False

    # Install development dependencies
    print("Installing development dependencies...")
    if not run_command(["uv", "sync", "--dev"]):
        print("✗ Failed to install development dependencies")
        return False

    print("✓ Dependencies installed successfully")
    return True

def create_directories():
    """Create necessary directories."""
    print("\nCreating directories...")

    project_root = Path(__file__).parent.parent
    directories = [
        "data",
        "logs",
        "assets/icons",
        "docs",
        "tests/fixtures"
    ]

    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {directory}")

def setup_git_hooks():
    """Set up git hooks for development."""
    print("\nSetting up git hooks...")

    project_root = Path(__file__).parent.parent
    hooks_dir = project_root / ".git" / "hooks"

    if not hooks_dir.exists():
        print("⚠️ Not a git repository - skipping git hooks")
        return

    # Pre-commit hook
    pre_commit_hook = """#!/bin/bash
# Pre-commit hook for Claude Code Configuration Switcher

echo "Running pre-commit checks..."

# Run tests
echo "Running tests..."
uv run pytest tests/ -q
if [ $? -ne 0 ]; then
    echo "✗ Tests failed"
    exit 1
fi

echo "✓ All checks passed"
"""

    hook_file = hooks_dir / "pre-commit"
    with open(hook_file, "w") as f:
        f.write(pre_commit_hook)

    # Make hook executable
    os.chmod(hook_file, 0o755)

    print("✓ Pre-commit hook installed")

def run_tests():
    """Run the test suite to verify setup."""
    print("\nRunning tests to verify setup...")

    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    if not run_command(["uv", "run", "pytest", "tests/", "-v"]):
        print("✗ Tests failed - setup may be incomplete")
        return False

    print("✓ All tests passed")
    return True

def create_dev_scripts():
    """Create development convenience scripts."""
    print("\nCreating development scripts...")

    project_root = Path(__file__).parent.parent

    # Run script
    run_script = f"""#!/bin/bash
# Development run script
cd "{project_root}"
uv run python src/main.py "$@"
"""
    run_script_file = project_root / "run.sh"
    with open(run_script_file, "w") as f:
        f.write(run_script)
    os.chmod(run_script_file, 0o755)
    print("✓ Created run.sh")

    # Test script
    test_script = f"""#!/bin/bash
# Test runner script
cd "{project_root}"
uv run pytest tests/ -v "$@"
"""
    test_script_file = project_root / "test.sh"
    with open(test_script_file, "w") as f:
        f.write(test_script)
    os.chmod(test_script_file, 0o755)
    print("✓ Created test.sh")

def show_next_steps():
    """Show next steps for development."""
    print("\n" + "="*60)
    print("Development setup completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run the application:")
    print("   uv run python src/main.py")
    print("   or: ./run.sh")
    print("\n2. Run tests:")
    print("   uv run pytest")
    print("   or: ./test.sh")
    print("\n3. Build executable:")
    print("   uv run python scripts/build.py")
    print("\n4. Create portable package:")
    print("   uv run python scripts/build.py --portable")
    print("\n5. Clean build artifacts:")
    print("   uv run python scripts/build.py --clean")
    print("\nUseful commands:")
    print("- uv add <package>: Add new dependency")
    print("- uv add --dev <package>: Add dev dependency")
    print("- uv run python -m pytest: Run tests")
    print("- uv sync: Sync dependencies")

def main():
    """Main setup function."""
    print("Claude Code Configuration Switcher - Development Setup")
    print("="*60)

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Setup environment
    if not setup_environment():
        sys.exit(1)

    # Create directories
    create_directories()

    # Setup git hooks
    setup_git_hooks()

    # Create dev scripts
    create_dev_scripts()

    # Run tests to verify setup
    if not run_tests():
        print("\n⚠️ Setup completed but tests failed")
        print("   Check the test output above for issues")
    else:
        # Show next steps
        show_next_steps()

if __name__ == "__main__":
    main()