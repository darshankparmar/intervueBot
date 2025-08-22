#!/usr/bin/env python3
"""
Development setup script for IntervueBot backend.

This script helps set up the development environment with proper
configuration and dependencies.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: str, cwd: Path = None) -> bool:
    """Run a shell command and return success status."""
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Error: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up IntervueBot Backend Development Environment")
    print("=" * 60)
    
    # Get the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 11):
        print(f"❌ Python 3.11+ required, found {python_version.major}.{python_version.minor}")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Create virtual environment if it doesn't exist
    venv_path = project_root / "venv"
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        if not run_command("python -m venv venv"):
            sys.exit(1)
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    if not run_command("pip install -e ."):
        sys.exit(1)
    print("✅ Dependencies installed")
    
    # Create .env file if it doesn't exist
    env_file = project_root / ".env"
    env_example = project_root / "env.example"
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ .env file created (please configure it)")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No env.example found, please create .env manually")
    
    # Run tests
    print("🧪 Running tests...")
    if run_command("python -m pytest tests/ -v"):
        print("✅ Tests passed")
    else:
        print("⚠️  Some tests failed (this is expected for initial setup)")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Configure your .env file with API keys and database settings")
    print("2. Start the application: python -m src.main")
    print("3. Visit http://localhost:8000/docs for API documentation")
    print("4. Begin implementing AI agents and business logic")


if __name__ == "__main__":
    main() 