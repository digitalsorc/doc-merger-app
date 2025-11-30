"""Tests for the merge engine."""

import pytest
import tempfile
from pathlib import Path

from src.core.merger import MergeEngine, MergeResult
from src.core.analyzer import FileAnalyzer, FileInfo
from src.utils.config import MergeConfig


class TestMergeEngine:
    """Test suite for MergeEngine."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory with test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test markdown files
            (tmpdir / "file1.md").write_text("# File 1\n\nContent of file 1.\n")
            (tmpdir / "file2.md").write_text("# File 2\n\nContent of file 2.\n")
            (tmpdir / "file3.md").write_text("# File 3\n\nContent of file 3.\n")
            
            yield tmpdir
    
    @pytest.fixture
    def config(self):
        """Create a default merge configuration."""
        return MergeConfig(
            header_style="## {name}",
            separator_style="---",
            generate_toc=True,
            add_metadata=True,
            add_semantic_markers=True,
        )
    
    def test_basic_merge(self, temp_dir, config):
        """Test basic merge of multiple files."""
        # Discover files
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        assert len(files) == 3
        
        # Perform merge
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        assert result.files_merged == 3
        assert output_path.exists()
        
        # Verify output content
        content = output_path.read_text()
        assert "## file1" in content
        assert "## file2" in content
        assert "## file3" in content
        assert "Content of file 1" in content
        assert "---" in content
    
    def test_merge_with_toc(self, temp_dir, config):
        """Test merge generates table of contents."""
        config.generate_toc = True
        config.toc_position = "top"
        
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        content = output_path.read_text()
        assert "# Table of Contents" in content
    
    def test_merge_with_metadata(self, temp_dir, config):
        """Test merge adds metadata comments."""
        config.add_metadata = True
        
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        content = output_path.read_text()
        assert "DOC_META" in content
    
    def test_merge_with_semantic_markers(self, temp_dir, config):
        """Test merge adds semantic markers."""
        config.add_semantic_markers = True
        
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        content = output_path.read_text()
        assert "<document" in content
        assert "</document>" in content
    
    def test_merge_without_toc(self, temp_dir, config):
        """Test merge without table of contents."""
        config.generate_toc = False
        
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path)
        
        assert result.success
        content = output_path.read_text()
        assert "# Table of Contents" not in content
    
    def test_dry_run(self, temp_dir, config):
        """Test dry run mode doesn't create output file."""
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge(files, output_path, dry_run=True)
        
        assert result.success
        assert not output_path.exists()
    
    def test_empty_files_list(self, temp_dir, config):
        """Test merge with empty files list."""
        output_path = temp_dir / "output.md"
        engine = MergeEngine(config)
        result = engine.merge([], output_path)
        
        # Should succeed with 0 files merged
        assert result.success
        assert result.files_merged == 0
    
    def test_preview_generation(self, temp_dir, config):
        """Test preview generation."""
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        engine = MergeEngine(config)
        preview = engine.generate_preview(files, max_lines=50)
        
        assert "file1" in preview
        assert "file2" in preview
        assert "file3" in preview


class TestFileAnalyzer:
    """Test suite for FileAnalyzer."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create files
            (tmpdir / "doc1.md").write_text("# Doc 1\n")
            (tmpdir / "doc2.markdown").write_text("# Doc 2\n")
            (tmpdir / "readme.txt").write_text("Not markdown")
            
            # Create subdirectory
            subdir = tmpdir / "subdir"
            subdir.mkdir()
            (subdir / "doc3.md").write_text("# Doc 3\n")
            
            yield tmpdir
    
    @pytest.fixture
    def config(self):
        return MergeConfig()
    
    def test_discover_files(self, temp_dir, config):
        """Test file discovery."""
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        # Should find .md and .markdown files, including in subdir
        assert len(files) == 3
        
        names = {f.path.name for f in files}
        assert "doc1.md" in names
        assert "doc2.markdown" in names
        assert "doc3.md" in names
        assert "readme.txt" not in names
    
    def test_non_recursive(self, temp_dir, config):
        """Test non-recursive scanning."""
        config.recursive = False
        
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        # Should only find files in top directory
        assert len(files) == 2
        names = {f.path.name for f in files}
        assert "doc3.md" not in names
    
    def test_exclude_patterns(self, temp_dir, config):
        """Test exclude patterns."""
        config.exclude_patterns = ["doc1*"]
        
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        names = {f.path.name for f in files}
        assert "doc1.md" not in names
        assert "doc2.markdown" in names
    
    def test_file_info(self, temp_dir, config):
        """Test FileInfo attributes."""
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        for f in files:
            assert f.path.exists()
            assert f.size > 0
            assert f.modified is not None
            assert f.size_formatted
            assert f.modified_formatted
    
    def test_sorting(self, temp_dir, config):
        """Test file sorting."""
        config.sort_order = "alphabetical"
        config.sort_ascending = True
        
        analyzer = FileAnalyzer(config)
        files = analyzer.discover_files([temp_dir])
        
        names = [f.path.name for f in files]
        assert names == sorted(names, key=str.lower)
