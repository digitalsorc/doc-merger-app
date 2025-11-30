"""Utility modules for Markdown Merger."""

from .config import MergeConfig, AppConfig, PRESETS, get_preset
from .logger import setup_logging, get_logger
from .helpers import (
    natural_sort_key,
    format_file_size,
    format_duration,
    calculate_file_hash,
    matches_patterns,
    extract_front_matter,
    adjust_header_levels,
    normalize_line_endings,
    normalize_whitespace,
    extract_headers,
    generate_anchor,
    detect_encoding,
    safe_read_file,
    extract_keywords,
)

__all__ = [
    'MergeConfig',
    'AppConfig',
    'PRESETS',
    'get_preset',
    'setup_logging',
    'get_logger',
    'natural_sort_key',
    'format_file_size',
    'format_duration',
    'calculate_file_hash',
    'matches_patterns',
    'extract_front_matter',
    'adjust_header_levels',
    'normalize_line_endings',
    'normalize_whitespace',
    'extract_headers',
    'generate_anchor',
    'detect_encoding',
    'safe_read_file',
    'extract_keywords',
]
