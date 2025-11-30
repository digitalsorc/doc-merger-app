#!/usr/bin/env python3
"""
Build script for Markdown Merger application.
Creates a standalone executable using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build():
    """Remove previous build artifacts."""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_remove:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"Removing {dir_path}...")
            shutil.rmtree(dir_path)
    
    # Remove spec file
    spec_file = Path('MarkdownMerger.spec')
    if spec_file.exists():
        spec_file.unlink()
        print(f"Removed {spec_file}")


def build_executable():
    """Build the executable using PyInstaller."""
    print("\n" + "=" * 50)
    print("Building Markdown Merger Executable")
    print("=" * 50 + "\n")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name', 'MarkdownMerger',
        '--windowed',           # No console window
        '--onefile',            # Single executable
        '--clean',              # Clean PyInstaller cache
        # Hidden imports for PyQt6
        '--hidden-import', 'PyQt6.QtCore',
        '--hidden-import', 'PyQt6.QtWidgets', 
        '--hidden-import', 'PyQt6.QtGui',
        'main.py'
    ]
    
    print(f"Running: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, check=False)
    
    if result.returncode != 0:
        print("\n❌ Build failed!")
        return False
    
    # Check if executable was created
    if sys.platform == 'win32':
        exe_path = project_root / 'dist' / 'MarkdownMerger.exe'
    elif sys.platform == 'darwin':
        exe_path = project_root / 'dist' / 'MarkdownMerger.app'
    else:
        exe_path = project_root / 'dist' / 'MarkdownMerger'
    
    if exe_path.exists():
        print(f"\n✅ Build successful!")
        print(f"   Executable: {exe_path}")
        
        if exe_path.is_file():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"   Size: {size_mb:.1f} MB")
        
        return True
    else:
        print("\n❌ Executable not found!")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build Markdown Merger executable')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts only')
    parser.add_argument('--no-clean', action='store_true', help='Skip cleaning before build')
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
        print("\n✅ Clean complete!")
        return
    
    if not args.no_clean:
        clean_build()
    
    success = build_executable()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
