# Build Instructions for Markdown Merger

This document explains how to build the Markdown Merger executable.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Setup

1. **Create and activate virtual environment**:

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Building the Executable

### Windows

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Build single-file executable
pyinstaller --name MarkdownMerger --windowed --onefile main.py

# The executable will be at: dist/MarkdownMerger.exe
```

### macOS

```bash
# Install PyInstaller
pip install pyinstaller

# Build app bundle
pyinstaller --name MarkdownMerger --windowed --onefile main.py

# The app will be at: dist/MarkdownMerger.app
# For distribution, create a DMG:
# hdiutil create -volname MarkdownMerger -srcfolder dist/MarkdownMerger.app -ov -format UDZO MarkdownMerger.dmg
```

### Linux

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --name MarkdownMerger --windowed --onefile main.py

# The executable will be at: dist/MarkdownMerger
# Make it executable if needed:
chmod +x dist/MarkdownMerger
```

## Build Options

### Common PyInstaller Options

| Option | Description |
|--------|-------------|
| `--onefile` | Create a single executable file |
| `--windowed` | Don't show console window (GUI app) |
| `--name NAME` | Name of the output executable |
| `--icon=icon.ico` | Set application icon |
| `--add-data` | Include additional data files |

### Advanced Build

For more control, use a spec file:

```bash
# Generate spec file
pyinstaller --name MarkdownMerger main.py --specpath build

# Edit build/MarkdownMerger.spec as needed

# Build from spec
pyinstaller build/MarkdownMerger.spec
```

## Troubleshooting

### Missing Modules

If the build fails due to missing modules:

```bash
# Add hidden imports
pyinstaller --name MarkdownMerger --windowed --onefile \
  --hidden-import=PyQt6.QtCore \
  --hidden-import=PyQt6.QtWidgets \
  --hidden-import=PyQt6.QtGui \
  main.py
```

### Large File Size

To reduce executable size:

1. Use UPX compression:
   ```bash
   pip install pyinstaller[encryption]
   pyinstaller --name MarkdownMerger --windowed --onefile --upx-dir=/path/to/upx main.py
   ```

2. Exclude unused modules in spec file

### PyQt6 Issues

If you encounter Qt-related issues:

1. Ensure PyQt6 is installed correctly: `pip install PyQt6`
2. On Linux, install Qt dependencies: `sudo apt install libxcb-xinerama0`

## Testing the Build

After building, test the executable:

1. Navigate to `dist/` folder
2. Run `MarkdownMerger.exe` (Windows) or `./MarkdownMerger` (Linux/macOS)
3. Verify all features work:
   - File/folder selection
   - Settings dialogs
   - Merge operation
   - Output generation

## Distribution

### Windows

1. The `.exe` file can be distributed directly
2. Or create an installer using NSIS or Inno Setup

### macOS

1. Create a DMG for distribution
2. For App Store, you'll need code signing and notarization

### Linux

1. Distribute the executable directly
2. Or create packages for apt/yum/pacman

## Continuous Integration

For automated builds, use GitHub Actions:

```yaml
name: Build

on: [push]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install -r requirements.txt pyinstaller
    
    - name: Build
      run: pyinstaller --name MarkdownMerger --windowed --onefile main.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: MarkdownMerger-${{ matrix.os }}
        path: dist/
```

## Support

If you encounter build issues, please open an issue on GitHub with:
- Operating system
- Python version
- Full error output
- PyInstaller version
