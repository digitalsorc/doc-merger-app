# Markdown Merger User Guide

Welcome to Markdown Merger! This comprehensive guide will help you understand and use all features of the application.

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Interface Overview](#user-interface-overview)
3. [Adding Files](#adding-files)
4. [Configuring the Merge](#configuring-the-merge)
5. [Running a Merge](#running-a-merge)
6. [Understanding Output](#understanding-output)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **Python**: 3.9 or higher (if running from source)
- **Memory**: Minimum 4GB RAM (8GB recommended for large file sets)
- **Disk Space**: 100MB for application + space for output files

### Installation

#### Option 1: Run from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/markdown-merger.git
cd markdown-merger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

#### Option 2: Use Pre-built Executable

1. Download `MarkdownMerger.exe` (Windows) or `MarkdownMerger.app` (macOS) from the releases page
2. Double-click to run - no installation required!

---

## User Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│  File  Edit  View  Help                    [- □ X]      │
├─────────────────────────────────────────────────────────┤
│ ┌─ Input Files ────────────────────┐ ┌─ Preview ──────┐ │
│ │ [📄 Add Files] [📁 Add Folder]   │ │                │ │
│ │ [Clear] [Remove Selected]        │ │  Preview of    │ │
│ │                                   │ │  merged output │ │
│ │ □ intro.md              2.3 KB   │ │                │ │
│ │ □ chapter1.md          15.7 KB   │ │                │ │
│ │ □ chapter2.md          12.1 KB   │ │                │ │
│ │                                   │ │                │ │
│ │ Total: 150 files, 2.4 MB         │ │                │ │
│ └───────────────────────────────────┘ └────────────────┘ │
│                                                           │
│ ┌─ Merge Settings ──────────────────────────────────────┐│
│ │ Preset: [AI Knowledge Base ▼]                        ││
│ │ Separator: [─── ▼] Header: [## {name} ▼]             ││
│ │ ☑ Generate TOC  ☑ Add Metadata                       ││
│ │ [⚙ Advanced Settings...]                             ││
│ └───────────────────────────────────────────────────────┘│
│                                                           │
│ Output: [C:\output\merged.md        ] [📁 Browse]        │
│                                                           │
│ [▶ Start Merge] [⏸ Pause] [⏹ Cancel]  Status: Ready    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 0%       │
│                                                           │
│ ┌─ Log ─────────────────────────────────────────────────┐│
│ │ [14:23:01] Ready to merge                            ││
│ └───────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Main Areas

1. **Menu Bar**: Access to all features and settings
2. **Input Files Panel**: List of files to merge with file management buttons
3. **Preview Panel**: Shows preview of merged output or selected file
4. **Merge Settings**: Quick access to common settings
5. **Output Path**: Where the merged file will be saved
6. **Action Buttons**: Start, pause, or cancel the merge
7. **Progress Bar**: Shows merge progress
8. **Log Panel**: Detailed messages about the merge process

---

## Adding Files

### Method 1: Add Individual Files

1. Click **📄 Add Files** button
2. Navigate to your markdown files
3. Select one or more files (hold Ctrl/Cmd for multiple)
4. Click **Open**

### Method 2: Add Entire Folder

1. Click **📁 Add Folder** button
2. Select a folder containing markdown files
3. Click **Select Folder**
4. All `.md` and `.markdown` files will be added (including subdirectories)

### Method 3: Drag and Drop

1. Open your file explorer/finder
2. Select files or folders
3. Drag them onto the file list area
4. Release to add them

### Managing Files

- **Remove Selected**: Select files in the list and click to remove them
- **Clear**: Remove all files from the list
- **Reorder**: Drag files within the list to change merge order

---

## Configuring the Merge

### Using Presets

The easiest way to configure is using presets:

| Preset | Best For |
|--------|----------|
| **basic** | Simple concatenation without extras |
| **ai_knowledge_base** | RAG systems, AI training data, knowledge bases |
| **documentation** | Technical docs, manuals, wikis |
| **archive** | Backup, preserving original formatting |

### Quick Settings

- **Separator**: Visual divider between documents
  - `---` (horizontal rule)
  - `***` (alternative horizontal rule)
  - `___` (underline style)
  - `None` (no separator)

- **Header**: How each document is labeled
  - `# {name}` (H1 header)
  - `## {name}` (H2 header)
  - `### {name}` (H3 header)

- **Generate TOC**: Create table of contents
- **Add Metadata**: Include machine-readable metadata

### Advanced Settings

Click **⚙ Advanced Settings** for the full options dialog:

#### Document Structure Tab
- **Header Template**: Custom template for document headers
- **Include File Path**: Show source file path
- **Include Document Index**: Show "Document X of Y"
- **Separator Style**: Custom separator markdown
- **Blank Lines**: Lines around separators

#### Table of Contents Tab
- **Generate TOC**: Enable/disable
- **TOC Depth**: 1-6 (how deep to go)
- **TOC Style**: Links, plain, or numbered
- **TOC Position**: Top or bottom

#### Content Processing Tab
- **Adjust Header Levels**: Shift all headers +/- N levels
- **Strip Front Matter**: Remove YAML/TOML metadata
- **Normalize Whitespace**: Clean up blank lines
- **Max Consecutive Blanks**: Limit blank lines
- **Detect Duplicates**: Warn about duplicate files

#### AI Optimization Tab
- **Add Document Metadata**: JSON comments for parsing
- **Add Semantic Markers**: XML-style document wrappers
- **Add Chunk Hints**: RAG boundary markers
- **Extract Keywords**: Auto-extract keywords

#### Output Tab
- **Encoding**: UTF-8, ASCII, Latin-1
- **Line Endings**: LF (Unix) or CRLF (Windows)
- **Create Backup**: Backup existing output file

---

## Running a Merge

### Step-by-Step

1. **Add your files** using any method above
2. **Configure settings** or select a preset
3. **Set output path**: Click Browse and choose location
4. **Click Start Merge**

### During the Merge

- **Progress Bar**: Shows overall completion percentage
- **Status**: Current file being processed
- **Log**: Detailed messages (expandable)

### Controls

- **Pause**: Temporarily stop processing (click again to resume)
- **Cancel**: Stop and discard partial output

### After Completion

A dialog will show:
- Number of files merged
- Total output size
- Processing time
- Any warnings or errors

---

## Understanding Output

### Basic Structure

```markdown
# Table of Contents
- [Document 1](#document-1)
- [Document 2](#document-2)

---

## Document 1
*Document 1 of 2*

[Content of document 1]

---

## Document 2
*Document 2 of 2*

[Content of document 2]
```

### With AI Optimization

```markdown
# Table of Contents
- [Document 1](#document-1)

---

<!-- DOC_META: {"source": "doc1.md", "index": 1, "size": 1024, "modified": "2025-11-30"} -->
<document id="doc_0001" source="doc1.md">
<!-- CHUNK_BOUNDARY: doc_0001 -->

## Document 1
*Source: `path/to/doc1.md`*
*Document 1 of 150*

[Content...]

</document>

---
```

### Metadata Fields

| Field | Description |
|-------|-------------|
| `source` | Original file path |
| `index` | Document number |
| `size` | File size in bytes |
| `modified` | Last modified date |
| `keywords` | Extracted keywords (if enabled) |

---

## Advanced Features

### Saving Configurations

1. Configure all settings as desired
2. Go to **File → Save Configuration**
3. Choose a filename and location
4. Settings are saved as JSON

### Loading Configurations

1. Go to **File → Load Configuration**
2. Select a saved `.json` file
3. All settings are restored

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Add Files |
| `Ctrl+Shift+O` | Add Folder |
| `Ctrl+,` | Advanced Settings |
| `F5` | Refresh Preview |
| `Ctrl+Q` | Exit |

### Theme Support

- Go to **View → Dark Mode** to toggle themes
- Setting is remembered between sessions

---

## Troubleshooting

### Common Issues

#### "No files found"
- Check that your files have `.md` or `.markdown` extension
- Verify the folder path is correct
- Check exclude patterns in settings

#### "Permission denied"
- Ensure you have read access to input files
- Ensure you have write access to output location
- Try running as administrator (Windows)

#### "Merge is slow"
- Large files take longer to process
- Close other applications to free memory
- Disable features you don't need (keywords, duplicate detection)

#### "Output file is too large"
- Consider splitting your input into batches
- Disable TOC for very large file counts
- Use minimal preset

### Error Messages

| Error | Solution |
|-------|----------|
| "File encoding error" | File may have unusual encoding; try converting to UTF-8 |
| "Memory error" | Too many files; try in batches |
| "Write error" | Check disk space and permissions |

### Getting Help

1. Check the log panel for detailed error messages
2. Review this user guide
3. Open an issue on GitHub with:
   - Error message
   - Number of files
   - Your configuration
   - Operating system

---

## Tips & Best Practices

1. **Start small**: Test with a few files before processing thousands
2. **Use presets**: They're optimized for common use cases
3. **Preview first**: Use the preview pane to check output format
4. **Backup important data**: Enable the backup option for safety
5. **Organize input**: Group related files in folders for easier management
6. **Monitor memory**: Close other apps when processing large file sets

---

*Thank you for using Markdown Merger! If you have feedback or suggestions, please open an issue on GitHub.*
