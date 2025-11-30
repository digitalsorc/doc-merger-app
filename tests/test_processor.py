"""Tests for content processor."""

import pytest
from pathlib import Path
import tempfile

from src.core.processor import ContentProcessor, TOCGenerator, ProcessedDocument
from src.utils.config import MergeConfig
from src.utils.helpers import (
    extract_front_matter,
    adjust_header_levels,
    normalize_whitespace,
    extract_headers,
    natural_sort_key,
)


class TestContentProcessor:
    """Test suite for ContentProcessor."""
    
    @pytest.fixture
    def config(self):
        return MergeConfig()
    
    @pytest.fixture
    def processor(self, config):
        return ContentProcessor(config)
    
    @pytest.fixture
    def temp_file(self):
        """Create a temporary markdown file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test File\n\nSome content here.\n")
            f.flush()
            yield Path(f.name)
        Path(f.name).unlink()
    
    def test_process_document(self, processor, temp_file):
        """Test basic document processing."""
        content = temp_file.read_text()
        doc = processor.process_document(temp_file, content, 1, 5)
        
        assert doc.source_path == temp_file
        assert doc.index == 1
        assert doc.total_count == 5
        assert "Test File" in doc.processed_content or "Some content" in doc.processed_content
    
    def test_generate_document_header(self, processor, temp_file):
        """Test document header generation."""
        content = temp_file.read_text()
        doc = processor.process_document(temp_file, content, 2, 10)
        
        header = processor.generate_document_header(doc)
        assert "## " in header or "# " in header
        assert "2 of 10" in header  # Document index
    
    def test_generate_metadata_comment(self, config, temp_file):
        """Test metadata comment generation."""
        config.add_metadata = True
        processor = ContentProcessor(config)
        
        content = temp_file.read_text()
        doc = processor.process_document(temp_file, content, 1, 1)
        
        metadata = processor.generate_metadata_comment(doc)
        assert "DOC_META" in metadata
        assert '"index": 1' in metadata
    
    def test_generate_semantic_markers(self, config, temp_file):
        """Test semantic marker generation."""
        config.add_semantic_markers = True
        processor = ContentProcessor(config)
        
        content = temp_file.read_text()
        doc = processor.process_document(temp_file, content, 1, 1)
        
        start_marker = processor.generate_semantic_markers(doc, "start")
        end_marker = processor.generate_semantic_markers(doc, "end")
        
        assert "<document" in start_marker
        assert "id=" in start_marker
        assert "</document>" in end_marker


class TestHelperFunctions:
    """Test suite for helper functions."""
    
    def test_extract_front_matter(self):
        """Test YAML front matter extraction."""
        content = """---
title: Test
date: 2025-01-01
---

# Heading

Content here.
"""
        front_matter, remaining = extract_front_matter(content)
        
        assert front_matter is not None
        assert "title: Test" in front_matter
        assert "---" not in remaining
        assert "# Heading" in remaining
    
    def test_extract_front_matter_none(self):
        """Test content without front matter."""
        content = "# Just a heading\n\nSome content."
        front_matter, remaining = extract_front_matter(content)
        
        assert front_matter is None
        assert remaining == content
    
    def test_adjust_header_levels_increase(self):
        """Test increasing header levels."""
        content = """# H1
## H2
### H3
"""
        adjusted = adjust_header_levels(content, 1)
        
        assert "## H1" in adjusted
        assert "### H2" in adjusted
        assert "#### H3" in adjusted
    
    def test_adjust_header_levels_decrease(self):
        """Test decreasing header levels."""
        content = """### H3
#### H4
"""
        adjusted = adjust_header_levels(content, -1)
        
        assert "## H3" in adjusted
        assert "### H4" in adjusted
    
    def test_adjust_header_levels_bounds(self):
        """Test header level bounds (1-6)."""
        content = "# H1\n###### H6"
        
        # Can't go below 1
        adjusted = adjust_header_levels(content, -1)
        assert "# H1" in adjusted  # Still level 1
        assert "##### H6" in adjusted  # H6 - 1 = H5
        
        # Can't go above 6
        adjusted = adjust_header_levels(content, 5)
        assert "###### H1" in adjusted  # 1 + 5 = 6
        assert "###### H6" in adjusted  # Still level 6
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        content = "Line 1\n\n\n\n\nLine 2\n"
        
        normalized = normalize_whitespace(content, max_consecutive=1)
        assert normalized.count('\n\n\n') == 0
    
    def test_extract_headers(self):
        """Test header extraction."""
        content = """# Title
## Section 1
### Subsection 1.1
## Section 2
"""
        headers = extract_headers(content, max_depth=3)
        
        assert len(headers) == 4
        assert headers[0] == (1, "Title")
        assert headers[1] == (2, "Section 1")
        assert headers[2] == (3, "Subsection 1.1")
        assert headers[3] == (2, "Section 2")
    
    def test_natural_sort_key(self):
        """Test natural sorting."""
        files = ["file10.md", "file2.md", "file1.md", "file20.md"]
        sorted_files = sorted(files, key=natural_sort_key)
        
        assert sorted_files == ["file1.md", "file2.md", "file10.md", "file20.md"]


class TestTOCGenerator:
    """Test suite for TOC generator."""
    
    @pytest.fixture
    def config(self):
        return MergeConfig(generate_toc=True, toc_depth=2, toc_style="links")
    
    @pytest.fixture
    def generator(self, config):
        return TOCGenerator(config)
    
    def test_generate_toc_links(self, generator):
        """Test TOC generation with links."""
        # Create mock documents
        class MockDoc:
            def __init__(self, name, headers):
                self.source_path = Path(f"{name}.md")
                self.headers = headers
        
        docs = [
            MockDoc("intro", [(1, "Introduction"), (2, "Overview")]),
            MockDoc("chapter1", [(1, "Chapter 1"), (2, "Section A")]),
        ]
        
        toc = generator.generate(docs)
        
        assert "# Table of Contents" in toc
        assert "[intro]" in toc
        assert "[chapter1]" in toc
    
    def test_toc_disabled(self, config):
        """Test TOC is not generated when disabled."""
        config.generate_toc = False
        generator = TOCGenerator(config)
        
        toc = generator.generate([])
        assert toc == ""
