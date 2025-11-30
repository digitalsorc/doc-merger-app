"""
Configuration management for Markdown Merger application.
Provides centralized configuration handling with validation.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class MergeConfig:
    """Configuration for merge operations."""
    
    # Document Structure
    header_style: str = "## {name}"  # Template for section headers
    include_file_path: bool = False  # Include source path in header
    include_doc_index: bool = True   # Add document index (1 of N)
    separator_style: str = "---"     # Separator between documents
    separator_blank_lines: int = 2   # Blank lines around separator
    
    # Table of Contents
    generate_toc: bool = True        # Generate table of contents
    toc_depth: int = 2               # Max header depth for TOC (1-6)
    toc_style: str = "links"         # links, plain, numbered
    toc_position: str = "top"        # top, bottom
    
    # Content Processing
    adjust_header_level: int = 0     # Shift headers by N levels
    fix_relative_links: bool = False # Convert relative links
    strip_front_matter: bool = True  # Remove YAML/TOML front matter
    normalize_whitespace: bool = True # Normalize blank lines
    max_consecutive_blanks: int = 2  # Max consecutive blank lines
    detect_duplicates: bool = True   # Warn about duplicate content
    
    # AI Optimization
    add_metadata: bool = True        # Add document metadata comments
    add_semantic_markers: bool = True # Add XML-style document markers
    add_chunk_hints: bool = False    # Add RAG chunk boundary hints
    extract_keywords: bool = False   # Extract keywords per document
    
    # Filtering
    include_patterns: List[str] = field(default_factory=lambda: ["*.md", "*.markdown"])
    exclude_patterns: List[str] = field(default_factory=list)
    recursive: bool = True           # Scan subdirectories
    max_depth: int = -1              # Max recursion depth (-1 = unlimited)
    
    # Sorting
    sort_order: str = "alphabetical"  # alphabetical, natural, date, size, custom
    sort_ascending: bool = True
    
    # Output
    output_encoding: str = "utf-8"
    line_ending: str = "lf"          # lf, crlf
    create_backup: bool = True       # Backup existing output
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MergeConfig":
        """Create config from dictionary."""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def save(self, filepath: Path) -> None:
        """Save configuration to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: Path) -> "MergeConfig":
        """Load configuration from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


@dataclass  
class AppConfig:
    """Application-level configuration."""
    
    theme: str = "light"              # light, dark
    window_width: int = 1200
    window_height: int = 800
    recent_projects: List[str] = field(default_factory=list)
    max_recent: int = 10
    last_input_dir: str = ""
    last_output_dir: str = ""
    show_preview: bool = True
    preview_lines: int = 50
    log_level: str = "INFO"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """Create config from dictionary."""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def add_recent_project(self, project_path: str) -> None:
        """Add a project to recent list."""
        if project_path in self.recent_projects:
            self.recent_projects.remove(project_path)
        self.recent_projects.insert(0, project_path)
        self.recent_projects = self.recent_projects[:self.max_recent]
    
    @classmethod
    def get_config_dir(cls) -> Path:
        """Get application configuration directory."""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', '')) / 'MarkdownMerger'
        else:  # Linux/macOS
            config_dir = Path.home() / '.config' / 'markdown-merger'
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def save(self, filepath: Optional[Path] = None) -> None:
        """Save app configuration."""
        if filepath is None:
            filepath = self.get_config_dir() / 'app_config.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: Optional[Path] = None) -> "AppConfig":
        """Load app configuration."""
        if filepath is None:
            filepath = cls.get_config_dir() / 'app_config.json'
        if not filepath.exists():
            return cls()
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (json.JSONDecodeError, IOError):
            return cls()


# Built-in presets
PRESETS = {
    "basic": MergeConfig(
        header_style="## {name}",
        generate_toc=False,
        add_metadata=False,
        add_semantic_markers=False,
        strip_front_matter=True,
    ),
    "ai_knowledge_base": MergeConfig(
        header_style="## {name}",
        include_file_path=True,
        include_doc_index=True,
        generate_toc=True,
        toc_depth=2,
        add_metadata=True,
        add_semantic_markers=True,
        add_chunk_hints=True,
        extract_keywords=True,
        strip_front_matter=True,
        normalize_whitespace=True,
    ),
    "documentation": MergeConfig(
        header_style="# {name}",
        generate_toc=True,
        toc_depth=3,
        fix_relative_links=True,
        add_metadata=False,
        add_semantic_markers=False,
        strip_front_matter=False,
    ),
    "archive": MergeConfig(
        header_style="---\n# {name}",
        generate_toc=False,
        add_metadata=False,
        add_semantic_markers=False,
        strip_front_matter=False,
        normalize_whitespace=False,
        adjust_header_level=0,
    ),
}


def get_preset(name: str) -> MergeConfig:
    """Get a preset configuration by name."""
    if name not in PRESETS:
        raise ValueError(f"Unknown preset: {name}. Available: {list(PRESETS.keys())}")
    # Return a copy to avoid modifying the original
    return MergeConfig.from_dict(PRESETS[name].to_dict())
