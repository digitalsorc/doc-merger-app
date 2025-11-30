"""
Utility helper functions for Markdown Merger application.
"""

import re
import hashlib
from pathlib import Path
from typing import List, Tuple, Optional
from fnmatch import fnmatch


def natural_sort_key(s: str) -> List:
    """
    Generate a key for natural sorting.
    Handles numbers within strings properly (file1, file2, file10).
    """
    return [int(text) if text.isdigit() else text.lower() 
            for text in re.split(r'(\d+)', str(s))]


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def calculate_file_hash(filepath: Path, chunk_size: int = 8192) -> str:
    """Calculate MD5 hash of file content for duplicate detection."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def matches_patterns(filename: str, patterns: List[str]) -> bool:
    """Check if filename matches any of the glob patterns."""
    return any(fnmatch(filename.lower(), pattern.lower()) for pattern in patterns)


def extract_front_matter(content: str) -> Tuple[Optional[str], str]:
    """
    Extract YAML front matter from markdown content.
    
    Returns:
        Tuple of (front_matter, content_without_front_matter)
    """
    if not content.startswith('---'):
        return None, content
    
    # Find closing ---
    lines = content.split('\n')
    end_index = None
    
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_index = i
            break
    
    if end_index is None:
        return None, content
    
    front_matter = '\n'.join(lines[1:end_index])
    remaining_content = '\n'.join(lines[end_index + 1:]).lstrip('\n')
    
    return front_matter, remaining_content


def adjust_header_levels(content: str, offset: int) -> str:
    """
    Adjust all markdown header levels by offset.
    
    Args:
        content: Markdown content
        offset: Number of levels to shift (positive = deeper, negative = shallower)
    
    Returns:
        Content with adjusted headers
    """
    if offset == 0:
        return content
    
    def adjust_header(match):
        current_level = len(match.group(1))
        new_level = max(1, min(6, current_level + offset))
        return '#' * new_level + match.group(2)
    
    # Match headers at start of line: # Header text
    pattern = r'^(#{1,6})(\s+.*)$'
    return re.sub(pattern, adjust_header, content, flags=re.MULTILINE)


def normalize_line_endings(content: str, style: str = "lf") -> str:
    """Normalize line endings to specified style."""
    # First normalize to LF
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    if style.lower() == "crlf":
        content = content.replace('\n', '\r\n')
    
    return content


def normalize_whitespace(content: str, max_consecutive: int = 2) -> str:
    """
    Normalize consecutive blank lines.
    
    Args:
        content: Content to normalize
        max_consecutive: Maximum consecutive blank lines to keep
    """
    # Replace multiple blank lines with specified maximum
    pattern = r'\n{' + str(max_consecutive + 2) + r',}'
    replacement = '\n' * (max_consecutive + 1)
    
    return re.sub(pattern, replacement, content).strip() + '\n'


def extract_headers(content: str, max_depth: int = 6) -> List[Tuple[int, str]]:
    """
    Extract markdown headers from content.
    
    Returns:
        List of (level, header_text) tuples
    """
    headers = []
    pattern = r'^(#{1,6})\s+(.+)$'
    
    for match in re.finditer(pattern, content, re.MULTILINE):
        level = len(match.group(1))
        if level <= max_depth:
            headers.append((level, match.group(2).strip()))
    
    return headers


def generate_anchor(text: str) -> str:
    """Generate a URL-safe anchor from header text."""
    # Remove special characters, convert to lowercase
    anchor = re.sub(r'[^\w\s-]', '', text.lower())
    anchor = re.sub(r'[\s]+', '-', anchor)
    return anchor


def detect_encoding(filepath: Path) -> str:
    """Detect file encoding using chardet if available."""
    try:
        import chardet
        with open(filepath, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB
        result = chardet.detect(raw_data)
        detected = result.get('encoding', 'utf-8') or 'utf-8'
        confidence = result.get('confidence', 0)
        
        # Prefer UTF-8 if confidence is low or if detected encoding is ASCII-compatible
        if confidence < 0.8 or detected.lower() in ('ascii', 'iso-8859-1', 'windows-1252'):
            return 'utf-8'
        return detected
    except ImportError:
        return 'utf-8'


def safe_read_file(filepath: Path, fallback_encoding: str = 'utf-8') -> str:
    """
    Safely read a file with encoding detection and fallback.
    """
    # Try UTF-8 first (most common for markdown files)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        pass
    
    # Try detected encoding
    encoding = detect_encoding(filepath)
    
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # Last resort: read with errors replaced
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()


def extract_keywords(content: str, max_keywords: int = 10) -> List[str]:
    """
    Extract potential keywords from markdown content.
    Simple extraction based on header text and emphasized words.
    """
    keywords = set()
    
    # Extract from headers
    headers = extract_headers(content)
    for _, text in headers:
        # Add significant words from headers
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        keywords.update(words)
    
    # Extract emphasized text (bold, italic)
    emphasized = re.findall(r'\*\*([^*]+)\*\*|\*([^*]+)\*|__([^_]+)__|_([^_]+)_', content)
    for groups in emphasized:
        for text in groups:
            if text and len(text) > 3:
                keywords.add(text.strip())
    
    # Filter and limit
    filtered = [k for k in keywords if len(k) > 2 and not k.isdigit()]
    return sorted(filtered)[:max_keywords]
