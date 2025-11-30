"""
Core merge engine for Markdown Merger.
Handles the complete merge workflow with streaming support.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Callable, Generator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from ..utils.config import MergeConfig
from ..utils.helpers import safe_read_file, normalize_line_endings
from .processor import ContentProcessor, TOCGenerator, ProcessedDocument
from .analyzer import FileInfo, FileAnalyzer


class MergeStatus(Enum):
    """Status of merge operation."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class MergeProgress:
    """Progress information for merge operation."""
    status: MergeStatus
    current_file: str
    current_index: int
    total_files: int
    bytes_processed: int
    total_bytes: int
    elapsed_seconds: float
    errors: List[str]
    warnings: List[str]
    
    @property
    def percent(self) -> float:
        if self.total_files == 0:
            return 0.0
        return (self.current_index / self.total_files) * 100
    
    @property
    def files_per_second(self) -> float:
        if self.elapsed_seconds == 0:
            return 0.0
        return self.current_index / self.elapsed_seconds
    
    @property
    def eta_seconds(self) -> float:
        if self.files_per_second == 0:
            return 0.0
        remaining = self.total_files - self.current_index
        return remaining / self.files_per_second


@dataclass
class MergeResult:
    """Result of a merge operation."""
    success: bool
    output_path: Optional[Path]
    files_merged: int
    total_size: int
    duration_seconds: float
    errors: List[str]
    warnings: List[str]
    
    @property
    def summary(self) -> str:
        if self.success:
            return (f"Successfully merged {self.files_merged} files "
                    f"in {self.duration_seconds:.2f}s")
        else:
            return f"Merge failed: {'; '.join(self.errors)}"


class MergeEngine:
    """
    Core merge engine.
    
    Handles file merging with streaming processing,
    progress tracking, and cancellation support.
    """
    
    def __init__(self, config: MergeConfig):
        self.config = config
        self.processor = ContentProcessor(config)
        self.toc_generator = TOCGenerator(config)
        self._cancelled = False
        self._paused = False
    
    def merge(
        self,
        files: List[FileInfo],
        output_path: Path,
        progress_callback: Optional[Callable[[MergeProgress], None]] = None,
        dry_run: bool = False
    ) -> MergeResult:
        """
        Merge multiple files into a single output file.
        
        Args:
            files: List of FileInfo objects to merge
            output_path: Path for output file
            progress_callback: Optional callback for progress updates
            dry_run: If True, don't write output file
        
        Returns:
            MergeResult with operation details
        """
        self._cancelled = False
        self._paused = False
        
        start_time = datetime.now()
        errors: List[str] = []
        warnings: List[str] = []
        bytes_processed = 0
        total_bytes = sum(f.size for f in files)
        
        # Create progress tracker
        def update_progress(index: int, current_file: str):
            if progress_callback:
                elapsed = (datetime.now() - start_time).total_seconds()
                progress_callback(MergeProgress(
                    status=MergeStatus.RUNNING,
                    current_file=current_file,
                    current_index=index,
                    total_files=len(files),
                    bytes_processed=bytes_processed,
                    total_bytes=total_bytes,
                    elapsed_seconds=elapsed,
                    errors=errors.copy(),
                    warnings=warnings.copy(),
                ))
        
        # Backup existing file if configured
        if not dry_run and self.config.create_backup and output_path.exists():
            backup_path = output_path.with_suffix(
                f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            )
            try:
                shutil.copy2(output_path, backup_path)
            except IOError as e:
                warnings.append(f"Could not create backup: {e}")
        
        try:
            # Phase 1: Process all documents
            processed_docs: List[ProcessedDocument] = []
            
            for index, file_info in enumerate(files, 1):
                # Check for cancellation
                if self._cancelled:
                    return MergeResult(
                        success=False,
                        output_path=None,
                        files_merged=index - 1,
                        total_size=bytes_processed,
                        duration_seconds=(datetime.now() - start_time).total_seconds(),
                        errors=["Merge cancelled by user"],
                        warnings=warnings,
                    )
                
                # Wait while paused
                while self._paused:
                    import time
                    time.sleep(0.1)
                    if self._cancelled:
                        break
                
                update_progress(index, file_info.path.name)
                
                try:
                    content = safe_read_file(file_info.path)
                    doc = self.processor.process_document(
                        file_info.path, content, index, len(files)
                    )
                    processed_docs.append(doc)
                    bytes_processed += file_info.size
                    
                except Exception as e:
                    error_msg = f"Error processing {file_info.path.name}: {e}"
                    errors.append(error_msg)
                    # Continue with other files
            
            # Phase 2: Generate output
            if not dry_run:
                self._write_output(output_path, processed_docs)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return MergeResult(
                success=len(errors) == 0,
                output_path=output_path if not dry_run else None,
                files_merged=len(processed_docs),
                total_size=bytes_processed,
                duration_seconds=duration,
                errors=errors,
                warnings=warnings,
            )
            
        except Exception as e:
            return MergeResult(
                success=False,
                output_path=None,
                files_merged=0,
                total_size=bytes_processed,
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                errors=[f"Merge failed: {e}"],
                warnings=warnings,
            )
    
    def _write_output(
        self,
        output_path: Path,
        documents: List[ProcessedDocument]
    ) -> None:
        """Write merged output to file."""
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding=self.config.output_encoding) as f:
            # Write TOC if configured
            if self.config.generate_toc and self.config.toc_position == "top":
                toc = self.toc_generator.generate(documents)
                f.write(toc)
            
            # Write each document
            for i, doc in enumerate(documents):
                # Metadata comment
                metadata = self.processor.generate_metadata_comment(doc)
                if metadata:
                    f.write(metadata + '\n')
                
                # Semantic start marker
                start_marker = self.processor.generate_semantic_markers(doc, "start")
                if start_marker:
                    f.write(start_marker + '\n')
                
                # Chunk hint
                chunk_hint = self.processor.generate_chunk_hint(doc)
                if chunk_hint:
                    f.write(chunk_hint + '\n')
                
                # Document header
                header = self.processor.generate_document_header(doc)
                f.write(header + '\n\n')
                
                # Document content
                f.write(doc.processed_content)
                
                # Semantic end marker
                end_marker = self.processor.generate_semantic_markers(doc, "end")
                if end_marker:
                    f.write('\n' + end_marker)
                
                # Add separator between documents (not after last one)
                if i < len(documents) - 1:
                    separator = self.processor.generate_separator()
                    f.write(separator)
            
            # Write TOC at bottom if configured
            if self.config.generate_toc and self.config.toc_position == "bottom":
                f.write('\n\n')
                toc = self.toc_generator.generate(documents)
                f.write(toc)
    
    def cancel(self) -> None:
        """Cancel the current merge operation."""
        self._cancelled = True
    
    def pause(self) -> None:
        """Pause the current merge operation."""
        self._paused = True
    
    def resume(self) -> None:
        """Resume a paused merge operation."""
        self._paused = False
    
    def generate_preview(
        self,
        files: List[FileInfo],
        max_lines: int = 50
    ) -> str:
        """
        Generate a preview of the merge output.
        
        Args:
            files: Files to preview
            max_lines: Maximum lines to include in preview
        
        Returns:
            Preview string
        """
        if not files:
            return "No files to preview."
        
        # Process first few files
        preview_files = files[:3]  # Preview first 3 files
        lines = []
        
        # Add TOC preview
        if self.config.generate_toc:
            lines.append("# Table of Contents")
            lines.append("")
            for i, f in enumerate(files[:10], 1):
                lines.append(f"- {f.path.stem}")
            if len(files) > 10:
                lines.append(f"... and {len(files) - 10} more")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        for i, file_info in enumerate(preview_files, 1):
            try:
                content = safe_read_file(file_info.path)
                doc = self.processor.process_document(
                    file_info.path, content, i, len(files)
                )
                
                # Add document header
                header = self.processor.generate_document_header(doc)
                lines.append(header)
                lines.append("")
                
                # Add content preview (first N lines)
                content_lines = doc.processed_content.split('\n')[:20]
                lines.extend(content_lines)
                
                if len(files) > len(preview_files) or i < len(preview_files):
                    separator = self.processor.generate_separator()
                    lines.append(separator)
                    
            except Exception as e:
                lines.append(f"[Error previewing {file_info.path.name}: {e}]")
        
        if len(files) > len(preview_files):
            lines.append(f"... {len(files) - len(preview_files)} more files ...")
        
        # Limit total lines
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines.append("")
            lines.append("... (preview truncated) ...")
        
        return '\n'.join(lines)
