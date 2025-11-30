"""Integration tests for Markdown Merger."""

import pytest
import tempfile
from pathlib import Path
import time

from src.core.merger import MergeEngine
from src.core.analyzer import FileAnalyzer
from src.utils.config import MergeConfig, get_preset


class TestLargeScaleMerge:
    """Test merging large numbers of files."""
    
    @pytest.fixture
    def large_temp_dir(self):
        """Create a temporary directory with many test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create 100 test files
            for i in range(100):
                content = f"""# Document {i}

## Section A

This is the content of document {i}. It contains multiple paragraphs
to simulate real-world markdown files.

## Section B

More content here with **bold** and *italic* text.

### Subsection B.1

- List item 1
- List item 2
- List item 3

```python
def example_{i}():
    return {i}
```
"""
                (tmpdir / f"doc_{i:03d}.md").write_text(content)
            
            yield tmpdir
    
    def test_merge_100_files(self, large_temp_dir):
        """Test merging 100 files completes successfully."""
        config = get_preset("ai_knowledge_base")
        
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([large_temp_dir])
        
        assert len(files) == 100
        
        output_path = large_temp_dir / "merged.md"
        engine = MergeEngine(config)
        
        start_time = time.time()
        result = engine.merge(files, output_path)
        duration = time.time() - start_time
        
        assert result.success
        assert result.files_merged == 100
        assert output_path.exists()
        
        # Should complete in reasonable time (< 30 seconds)
        assert duration < 30, f"Merge took too long: {duration}s"
        
        # Verify output content
        content = output_path.read_text()
        
        # Should have TOC
        assert "# Table of Contents" in content
        
        # Should have all documents
        for i in range(100):
            assert f"Document {i}" in content or f"doc_{i:03d}" in content
        
        # Should have metadata
        assert "DOC_META" in content
        
        # Should have semantic markers
        assert "<document" in content
        assert "</document>" in content


class TestPresets:
    """Test preset configurations."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            (tmpdir / "test1.md").write_text("# Test 1\n\nContent.\n")
            (tmpdir / "test2.md").write_text("# Test 2\n\nMore content.\n")
            
            yield tmpdir
    
    def test_basic_preset(self, temp_dir):
        """Test basic preset merges without extras."""
        config = get_preset("basic")
        
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        content = output_path.read_text()
        
        # Basic preset should NOT have TOC or metadata
        assert "# Table of Contents" not in content
        assert "DOC_META" not in content
    
    def test_ai_knowledge_base_preset(self, temp_dir):
        """Test AI knowledge base preset has all features."""
        config = get_preset("ai_knowledge_base")
        
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        content = output_path.read_text()
        
        # AI preset should have all features
        assert "# Table of Contents" in content
        assert "DOC_META" in content
        assert "<document" in content
    
    def test_documentation_preset(self, temp_dir):
        """Test documentation preset."""
        config = get_preset("documentation")
        
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        content = output_path.read_text()
        
        # Documentation preset should have TOC but no metadata
        assert "# Table of Contents" in content
        assert "DOC_META" not in content


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_empty_file(self, temp_dir):
        """Test handling of empty files."""
        (temp_dir / "empty.md").write_text("")
        (temp_dir / "normal.md").write_text("# Normal\n\nContent.\n")
        
        config = MergeConfig()
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        assert result.files_merged == 2
    
    def test_special_characters_in_content(self, temp_dir):
        """Test handling of special characters."""
        content = """# Special Characters

Unicode: 你好世界 🎉 émojis αβγδ

HTML entities: &amp; &lt; &gt;

Markdown escapes: \\*not italic\\* \\`not code\\`
"""
        (temp_dir / "special.md").write_text(content, encoding='utf-8')
        
        config = MergeConfig()
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        output_content = output_path.read_text(encoding='utf-8')
        assert "你好世界" in output_content
        assert "🎉" in output_content
    
    def test_deeply_nested_headers(self, temp_dir):
        """Test handling of deeply nested headers."""
        content = """# H1
## H2
### H3
#### H4
##### H5
###### H6
"""
        (temp_dir / "headers.md").write_text(content)
        
        config = MergeConfig(adjust_header_level=1)
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        content = output_path.read_text()
        
        # All headers should be shifted, but H6 should stay at 6
        assert "## H1" in content
        assert "###### H6" in content  # Can't go beyond 6
    
    def test_front_matter_handling(self, temp_dir):
        """Test YAML front matter is stripped."""
        content = """---
title: Test Document
author: Test Author
date: 2025-01-01
---

# Actual Content

This is the real content.
"""
        (temp_dir / "frontmatter.md").write_text(content)
        
        config = MergeConfig(strip_front_matter=True)
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        output_content = output_path.read_text()
        
        # Front matter should be stripped
        assert "title: Test Document" not in output_content
        assert "author: Test Author" not in output_content
        # But content should remain
        assert "Actual Content" in output_content
