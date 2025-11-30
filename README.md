# Markdown Merger

A powerful desktop application for merging multiple markdown files into a single, well-structured document optimized for AI knowledge base ingestion.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## Features

- **Merge Hundreds of Files**: Process 1000+ markdown files efficiently
- **Auto-Generate Table of Contents**: Create a navigable TOC for your merged document
- **AI-Optimized Output**: Add metadata and semantic markers for knowledge base ingestion
- **Configurable Separators & Headers**: Customize how documents are combined
- **Drag-and-Drop Interface**: Easy file management with intuitive GUI
- **Preset Configurations**: Quick setup for common use cases
- **Dark/Light Theme**: Choose your preferred appearance
- **Progress Tracking**: Real-time feedback during processing

## Installation

### From Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/markdown-merger.git
   cd markdown-merger
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

### Building an Executable

To create a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --name MarkdownMerger --windowed --onefile main.py

# The executable will be in the dist/ folder
```

Alternatively, use the build script:

```bash
python scripts/build.py
```

## Quick Start

1. **Launch the application** by running `python main.py` or double-clicking the executable

2. **Add files** using one of these methods:
   - Click "📄 Add Files" to select individual markdown files
   - Click "📁 Add Folder" to add all markdown files from a directory
   - Drag and drop files or folders directly into the file list

3. **Configure settings**:
   - Select a preset (e.g., "ai_knowledge_base" for full AI optimization)
   - Adjust separator style, header format, and other options
   - Click "⚙ Advanced Settings" for more options

4. **Choose output location**:
   - Click "📁 Browse" next to the output field
   - Select where to save the merged file

5. **Start the merge**:
   - Click "▶ Start Merge"
   - Watch the progress bar and log for updates
   - The merged file will be created at your specified location

## Configuration Options

### Presets

| Preset | Description |
|--------|-------------|
| `basic` | Minimal processing, simple merge |
| `ai_knowledge_base` | Full AI optimization with metadata and semantic markers |
| `documentation` | Preserves structure, includes TOC |
| `archive` | Preserves everything as-is |

### Document Structure

- **Header Style**: Template for section headers (e.g., `## {name}`)
- **Include File Path**: Show source file path in header
- **Include Document Index**: Add "Document X of Y" indicator
- **Separator Style**: Visual separator between documents (`---`, `***`, `___`)

### Table of Contents

- **Generate TOC**: Enable/disable automatic TOC
- **TOC Depth**: How many header levels to include (1-6)
- **TOC Style**: Links, plain text, or numbered list
- **TOC Position**: Top or bottom of document

### AI Optimization

- **Add Metadata**: Insert JSON metadata comments for each document
- **Add Semantic Markers**: Wrap documents in XML-style tags
- **Add Chunk Hints**: Insert RAG chunk boundary markers
- **Extract Keywords**: Generate keyword lists per document

### Content Processing

- **Strip Front Matter**: Remove YAML/TOML front matter
- **Adjust Header Levels**: Shift all headers up or down
- **Normalize Whitespace**: Clean up excessive blank lines
- **Detect Duplicates**: Warn about duplicate content

## Output Format

The merged output includes:

```markdown
# Table of Contents
- [Document 1](#document-1)
- [Document 2](#document-2)
...

---

<!-- DOC_META: {"source": "doc1.md", "index": 1, ...} -->
<document id="doc_0001" source="doc1.md">

## Document 1
*Source: `path/to/doc1.md`*
*Document 1 of 150*

[Original document content...]

</document>

---

[More documents...]
```

## Project Structure

```
markdown-merger/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── src/
│   ├── gui/
│   │   └── main_window.py   # Main window and dialogs
│   ├── core/
│   │   ├── merger.py        # Core merge engine
│   │   ├── processor.py     # Content processing
│   │   └── analyzer.py      # File analysis
│   └── utils/
│       ├── config.py        # Configuration management
│       ├── logger.py        # Logging setup
│       └── helpers.py       # Utility functions
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/                 # Build scripts
└── sample_files/            # Example files
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_merger.py
```

### Code Style

This project follows PEP 8 guidelines. Type hints are used throughout.

## Requirements

- Python 3.9 or higher
- PyQt6 6.4.0 or higher
- See `requirements.txt` for full list

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything works
5. Submit a pull request

## Acknowledgments

- PyQt6 for the GUI framework
- The Python community for excellent tools and libraries
