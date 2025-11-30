"""
File analyzer for Markdown Merger.
Handles file discovery, filtering, and analysis.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime

from ..utils.config import MergeConfig
from ..utils.helpers import (
    natural_sort_key,
    matches_patterns,
    calculate_file_hash,
    format_file_size,
)


@dataclass
class FileInfo:
    """Information about a markdown file."""
    path: Path
    size: int
    modified: datetime
    hash: Optional[str] = None
    preview: str = ""
    
    @property
    def size_formatted(self) -> str:
        return format_file_size(self.size)
    
    @property
    def modified_formatted(self) -> str:
        return self.modified.strftime("%Y-%m-%d %H:%M")


class FileAnalyzer:
    """Discovers and analyzes markdown files."""
    
    def __init__(self, config: MergeConfig):
        self.config = config
    
    def discover_files(
        self,
        paths: List[Path],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> List[FileInfo]:
        """
        Discover markdown files from given paths.
        
        Args:
            paths: List of files or directories to scan
            progress_callback: Optional callback for progress updates
        
        Returns:
            List of FileInfo objects
        """
        files = []
        
        for path in paths:
            if path.is_file():
                if self._matches_filters(path):
                    files.append(self._analyze_file(path))
                    if progress_callback:
                        progress_callback(f"Found: {path.name}")
            elif path.is_dir():
                files.extend(self._scan_directory(path, progress_callback))
        
        return self._sort_files(files)
    
    def _scan_directory(
        self,
        directory: Path,
        progress_callback: Optional[Callable[[str], None]] = None,
        current_depth: int = 0
    ) -> List[FileInfo]:
        """Recursively scan a directory for markdown files."""
        files = []
        
        # Check depth limit
        if self.config.max_depth >= 0 and current_depth > self.config.max_depth:
            return files
        
        try:
            for entry in directory.iterdir():
                if entry.is_file() and self._matches_filters(entry):
                    files.append(self._analyze_file(entry))
                    if progress_callback:
                        progress_callback(f"Found: {entry.name}")
                        
                elif entry.is_dir() and self.config.recursive:
                    # Skip hidden directories
                    if not entry.name.startswith('.'):
                        files.extend(self._scan_directory(
                            entry, progress_callback, current_depth + 1
                        ))
        except PermissionError:
            if progress_callback:
                progress_callback(f"⚠ Permission denied: {directory}")
        
        return files
    
    def _matches_filters(self, filepath: Path) -> bool:
        """Check if file matches include/exclude patterns."""
        filename = filepath.name
        
        # Check include patterns
        if not matches_patterns(filename, self.config.include_patterns):
            return False
        
        # Check exclude patterns
        if self.config.exclude_patterns:
            if matches_patterns(filename, self.config.exclude_patterns):
                return False
        
        return True
    
    def _analyze_file(self, filepath: Path) -> FileInfo:
        """Analyze a single file and return FileInfo."""
        stat = filepath.stat()
        
        # Read preview (first few lines)
        preview = ""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                preview = f.read(500)
                if len(preview) == 500:
                    preview = preview.rsplit('\n', 1)[0] + '...'
        except IOError:
            preview = "[Could not read file]"
        
        return FileInfo(
            path=filepath,
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
            preview=preview,
        )
    
    def _sort_files(self, files: List[FileInfo]) -> List[FileInfo]:
        """Sort files according to configuration."""
        reverse = not self.config.sort_ascending
        
        if self.config.sort_order == "alphabetical":
            files.sort(key=lambda f: str(f.path).lower(), reverse=reverse)
        elif self.config.sort_order == "natural":
            files.sort(key=lambda f: natural_sort_key(str(f.path)), reverse=reverse)
        elif self.config.sort_order == "date":
            files.sort(key=lambda f: f.modified, reverse=reverse)
        elif self.config.sort_order == "size":
            files.sort(key=lambda f: f.size, reverse=reverse)
        # "custom" order is preserved as-is
        
        return files
    
    def detect_duplicates(
        self,
        files: List[FileInfo],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, List[FileInfo]]:
        """
        Detect duplicate files by content hash.
        
        Returns:
            Dictionary mapping hash to list of files with that hash
        """
        if not self.config.detect_duplicates:
            return {}
        
        hash_map: Dict[str, List[FileInfo]] = {}
        
        for file_info in files:
            if progress_callback:
                progress_callback(f"Checking: {file_info.path.name}")
            
            file_hash = calculate_file_hash(file_info.path)
            file_info.hash = file_hash
            
            if file_hash not in hash_map:
                hash_map[file_hash] = []
            hash_map[file_hash].append(file_info)
        
        # Return only duplicates (more than one file with same hash)
        return {h: files for h, files in hash_map.items() if len(files) > 1}
    
    def get_statistics(self, files: List[FileInfo]) -> Dict[str, any]:
        """Calculate statistics for a set of files."""
        if not files:
            return {
                "count": 0,
                "total_size": 0,
                "total_size_formatted": "0 B",
                "avg_size": 0,
                "avg_size_formatted": "0 B",
                "oldest": None,
                "newest": None,
            }
        
        total_size = sum(f.size for f in files)
        avg_size = total_size // len(files)
        
        return {
            "count": len(files),
            "total_size": total_size,
            "total_size_formatted": format_file_size(total_size),
            "avg_size": avg_size,
            "avg_size_formatted": format_file_size(avg_size),
            "oldest": min(f.modified for f in files),
            "newest": max(f.modified for f in files),
        }
