"""
Content processor for Markdown Merger.
Handles all content transformation operations.
"""

import re
from typing import Optional, List, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

from ..utils.config import MergeConfig
from ..utils.helpers import (
    extract_front_matter,
    adjust_header_levels,
    normalize_whitespace,
    normalize_line_endings,
    extract_headers,
    generate_anchor,
    extract_keywords,
)


@dataclass
class ProcessedDocument:
    """Represents a processed markdown document."""
    source_path: Path
    original_content: str
    processed_content: str
    headers: List[Tuple[int, str]]
    keywords: List[str]
    front_matter: Optional[str]
    file_size: int
    modified_time: datetime
    index: int
    total_count: int


class ContentProcessor:
    """Processes markdown content according to configuration."""
    
    def __init__(self, config: MergeConfig):
        self.config = config
    
    def process_document(
        self,
        filepath: Path,
        content: str,
        index: int,
        total_count: int
    ) -> ProcessedDocument:
        """
        Process a single markdown document.
        
        Args:
            filepath: Path to the source file
            content: Raw file content
            index: Document index (1-based)
            total_count: Total number of documents being merged
        
        Returns:
            ProcessedDocument with all transformations applied
        """
        original_content = content
        front_matter = None
        
        # Step 1: Handle front matter
        if self.config.strip_front_matter:
            front_matter, content = extract_front_matter(content)
        
        # Step 2: Adjust header levels
        if self.config.adjust_header_level != 0:
            content = adjust_header_levels(content, self.config.adjust_header_level)
        
        # Step 3: Normalize whitespace
        if self.config.normalize_whitespace:
            content = normalize_whitespace(content, self.config.max_consecutive_blanks)
        
        # Step 4: Normalize line endings
        content = normalize_line_endings(content, self.config.line_ending)
        
        # Extract headers for TOC
        headers = extract_headers(content, self.config.toc_depth)
        
        # Extract keywords if enabled
        keywords = []
        if self.config.extract_keywords:
            keywords = extract_keywords(content)
        
        # Get file metadata
        stat = filepath.stat()
        
        return ProcessedDocument(
            source_path=filepath,
            original_content=original_content,
            processed_content=content,
            headers=headers,
            keywords=keywords,
            front_matter=front_matter,
            file_size=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            index=index,
            total_count=total_count,
        )
    
    def generate_document_header(self, doc: ProcessedDocument) -> str:
        """Generate header section for a document."""
        name = doc.source_path.stem
        
        # Build header from template
        header = self.config.header_style.format(name=name)
        
        # Add file path if configured
        if self.config.include_file_path:
            header += f"\n*Source: `{doc.source_path}`*"
        
        # Add document index if configured
        if self.config.include_doc_index:
            header += f"\n*Document {doc.index} of {doc.total_count}*"
        
        return header
    
    def generate_metadata_comment(self, doc: ProcessedDocument) -> str:
        """Generate metadata comment for AI parsing."""
        if not self.config.add_metadata:
            return ""
        
        metadata = {
            "source": str(doc.source_path),
            "index": doc.index,
            "size": doc.file_size,
            "modified": doc.modified_time.strftime("%Y-%m-%d"),
        }
        
        if doc.keywords:
            metadata["keywords"] = doc.keywords
        
        import json
        return f"<!-- DOC_META: {json.dumps(metadata)} -->"
    
    def generate_semantic_markers(
        self,
        doc: ProcessedDocument,
        position: str  # "start" or "end"
    ) -> str:
        """Generate XML-style semantic markers."""
        if not self.config.add_semantic_markers:
            return ""
        
        doc_id = f"doc_{doc.index:04d}"
        source = doc.source_path.name
        
        if position == "start":
            return f'<document id="{doc_id}" source="{source}">'
        else:
            return '</document>'
    
    def generate_chunk_hint(self, doc: ProcessedDocument) -> str:
        """Generate chunk boundary hint for RAG systems."""
        if not self.config.add_chunk_hints:
            return ""
        
        return f"<!-- CHUNK_BOUNDARY: doc_{doc.index:04d} -->"
    
    def generate_separator(self) -> str:
        """Generate separator between documents."""
        separator = self.config.separator_style
        blank_lines = '\n' * self.config.separator_blank_lines
        return f"{blank_lines}{separator}{blank_lines}"


class TOCGenerator:
    """Generates table of contents from documents."""
    
    def __init__(self, config: MergeConfig):
        self.config = config
    
    def generate(self, documents: List[ProcessedDocument]) -> str:
        """Generate table of contents for all documents."""
        if not self.config.generate_toc:
            return ""
        
        lines = ["# Table of Contents", ""]
        
        for doc in documents:
            # Add document entry
            doc_name = doc.source_path.stem
            anchor = generate_anchor(doc_name)
            
            if self.config.toc_style == "links":
                lines.append(f"- [{doc_name}](#{anchor})")
            elif self.config.toc_style == "numbered":
                lines.append(f"{doc.index}. [{doc_name}](#{anchor})")
            else:  # plain
                lines.append(f"- {doc_name}")
            
            # Add headers within document if depth allows
            if self.config.toc_depth > 1:
                for level, header_text in doc.headers:
                    if level <= self.config.toc_depth:
                        indent = "  " * (level - 1)
                        header_anchor = f"{anchor}--{generate_anchor(header_text)}"
                        
                        if self.config.toc_style == "links":
                            lines.append(f"{indent}- [{header_text}](#{header_anchor})")
                        else:
                            lines.append(f"{indent}- {header_text}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return '\n'.join(lines)
