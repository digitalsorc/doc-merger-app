"""
Main window for Markdown Merger application.
"""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QGroupBox, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit,
    QProgressBar, QComboBox, QCheckBox, QFileDialog,
    QMessageBox, QMenuBar, QMenu, QStatusBar, QToolBar,
    QSpinBox, QDialog, QDialogButtonBox, QTabWidget,
    QFormLayout, QFrame, QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QMimeData, QUrl
from PyQt6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent, QFont

from ..core import (
    MergeEngine, FileAnalyzer, FileInfo,
    MergeProgress, MergeResult, MergeStatus
)
from ..utils import MergeConfig, AppConfig, PRESETS, get_preset, format_file_size


class MergeWorker(QThread):
    """Background worker for merge operations."""
    
    progress = pyqtSignal(MergeProgress)
    finished = pyqtSignal(MergeResult)
    log_message = pyqtSignal(str)
    
    def __init__(
        self,
        engine: MergeEngine,
        files: List[FileInfo],
        output_path: Path,
        dry_run: bool = False
    ):
        super().__init__()
        self.engine = engine
        self.files = files
        self.output_path = output_path
        self.dry_run = dry_run
    
    def run(self):
        def on_progress(progress: MergeProgress):
            self.progress.emit(progress)
            self.log_message.emit(
                f"Processing {progress.current_file} "
                f"({progress.current_index}/{progress.total_files})"
            )
        
        result = self.engine.merge(
            self.files,
            self.output_path,
            progress_callback=on_progress,
            dry_run=self.dry_run
        )
        self.finished.emit(result)


class FileListWidget(QListWidget):
    """Custom list widget with drag-and-drop support."""
    
    files_dropped = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setAlternatingRowColors(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
    
    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            paths = []
            for url in event.mimeData().urls():
                path = Path(url.toLocalFile())
                if path.exists():
                    paths.append(path)
            if paths:
                self.files_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class SettingsDialog(QDialog):
    """Advanced settings dialog."""
    
    def __init__(self, config: MergeConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Advanced Settings")
        self.setMinimumSize(600, 500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tab widget for categories
        tabs = QTabWidget()
        
        # Document Structure tab
        structure_tab = QWidget()
        structure_layout = QFormLayout(structure_tab)
        
        self.header_style = QLineEdit(self.config.header_style)
        structure_layout.addRow("Header Template:", self.header_style)
        
        self.include_path = QCheckBox()
        self.include_path.setChecked(self.config.include_file_path)
        structure_layout.addRow("Include File Path:", self.include_path)
        
        self.include_index = QCheckBox()
        self.include_index.setChecked(self.config.include_doc_index)
        structure_layout.addRow("Include Document Index:", self.include_index)
        
        self.separator_style = QLineEdit(self.config.separator_style)
        structure_layout.addRow("Separator Style:", self.separator_style)
        
        self.separator_blanks = QSpinBox()
        self.separator_blanks.setRange(0, 10)
        self.separator_blanks.setValue(self.config.separator_blank_lines)
        structure_layout.addRow("Blank Lines Around Separator:", self.separator_blanks)
        
        tabs.addTab(structure_tab, "Document Structure")
        
        # TOC tab
        toc_tab = QWidget()
        toc_layout = QFormLayout(toc_tab)
        
        self.generate_toc = QCheckBox()
        self.generate_toc.setChecked(self.config.generate_toc)
        toc_layout.addRow("Generate TOC:", self.generate_toc)
        
        self.toc_depth = QSpinBox()
        self.toc_depth.setRange(1, 6)
        self.toc_depth.setValue(self.config.toc_depth)
        toc_layout.addRow("TOC Depth:", self.toc_depth)
        
        self.toc_style = QComboBox()
        self.toc_style.addItems(["links", "plain", "numbered"])
        self.toc_style.setCurrentText(self.config.toc_style)
        toc_layout.addRow("TOC Style:", self.toc_style)
        
        self.toc_position = QComboBox()
        self.toc_position.addItems(["top", "bottom"])
        self.toc_position.setCurrentText(self.config.toc_position)
        toc_layout.addRow("TOC Position:", self.toc_position)
        
        tabs.addTab(toc_tab, "Table of Contents")
        
        # Content Processing tab
        content_tab = QWidget()
        content_layout = QFormLayout(content_tab)
        
        self.adjust_headers = QSpinBox()
        self.adjust_headers.setRange(-5, 5)
        self.adjust_headers.setValue(self.config.adjust_header_level)
        content_layout.addRow("Adjust Header Levels:", self.adjust_headers)
        
        self.strip_front_matter = QCheckBox()
        self.strip_front_matter.setChecked(self.config.strip_front_matter)
        content_layout.addRow("Strip Front Matter:", self.strip_front_matter)
        
        self.normalize_ws = QCheckBox()
        self.normalize_ws.setChecked(self.config.normalize_whitespace)
        content_layout.addRow("Normalize Whitespace:", self.normalize_ws)
        
        self.max_blanks = QSpinBox()
        self.max_blanks.setRange(1, 10)
        self.max_blanks.setValue(self.config.max_consecutive_blanks)
        content_layout.addRow("Max Consecutive Blank Lines:", self.max_blanks)
        
        self.detect_dupes = QCheckBox()
        self.detect_dupes.setChecked(self.config.detect_duplicates)
        content_layout.addRow("Detect Duplicates:", self.detect_dupes)
        
        tabs.addTab(content_tab, "Content Processing")
        
        # AI Optimization tab
        ai_tab = QWidget()
        ai_layout = QFormLayout(ai_tab)
        
        self.add_metadata = QCheckBox()
        self.add_metadata.setChecked(self.config.add_metadata)
        ai_layout.addRow("Add Document Metadata:", self.add_metadata)
        
        self.add_semantic = QCheckBox()
        self.add_semantic.setChecked(self.config.add_semantic_markers)
        ai_layout.addRow("Add Semantic Markers:", self.add_semantic)
        
        self.add_chunks = QCheckBox()
        self.add_chunks.setChecked(self.config.add_chunk_hints)
        ai_layout.addRow("Add Chunk Hints:", self.add_chunks)
        
        self.extract_kw = QCheckBox()
        self.extract_kw.setChecked(self.config.extract_keywords)
        ai_layout.addRow("Extract Keywords:", self.extract_kw)
        
        tabs.addTab(ai_tab, "AI Optimization")
        
        # Output tab
        output_tab = QWidget()
        output_layout = QFormLayout(output_tab)
        
        self.encoding = QComboBox()
        self.encoding.addItems(["utf-8", "ascii", "latin-1"])
        self.encoding.setCurrentText(self.config.output_encoding)
        output_layout.addRow("Encoding:", self.encoding)
        
        self.line_ending = QComboBox()
        self.line_ending.addItems(["lf", "crlf"])
        self.line_ending.setCurrentText(self.config.line_ending)
        output_layout.addRow("Line Endings:", self.line_ending)
        
        self.create_backup = QCheckBox()
        self.create_backup.setChecked(self.config.create_backup)
        output_layout.addRow("Create Backup:", self.create_backup)
        
        tabs.addTab(output_tab, "Output")
        
        layout.addWidget(tabs)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_config(self) -> MergeConfig:
        """Get updated configuration from dialog."""
        return MergeConfig(
            header_style=self.header_style.text(),
            include_file_path=self.include_path.isChecked(),
            include_doc_index=self.include_index.isChecked(),
            separator_style=self.separator_style.text(),
            separator_blank_lines=self.separator_blanks.value(),
            generate_toc=self.generate_toc.isChecked(),
            toc_depth=self.toc_depth.value(),
            toc_style=self.toc_style.currentText(),
            toc_position=self.toc_position.currentText(),
            adjust_header_level=self.adjust_headers.value(),
            strip_front_matter=self.strip_front_matter.isChecked(),
            normalize_whitespace=self.normalize_ws.isChecked(),
            max_consecutive_blanks=self.max_blanks.value(),
            detect_duplicates=self.detect_dupes.isChecked(),
            add_metadata=self.add_metadata.isChecked(),
            add_semantic_markers=self.add_semantic.isChecked(),
            add_chunk_hints=self.add_chunks.isChecked(),
            extract_keywords=self.extract_kw.isChecked(),
            output_encoding=self.encoding.currentText(),
            line_ending=self.line_ending.currentText(),
            create_backup=self.create_backup.isChecked(),
            include_patterns=self.config.include_patterns,
            exclude_patterns=self.config.exclude_patterns,
            recursive=self.config.recursive,
            max_depth=self.config.max_depth,
            sort_order=self.config.sort_order,
            sort_ascending=self.config.sort_ascending,
            fix_relative_links=self.config.fix_relative_links,
        )


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.config = get_preset("ai_knowledge_base")
        self.app_config = AppConfig.load()
        self.files: List[FileInfo] = []
        self.worker: Optional[MergeWorker] = None
        self.engine: Optional[MergeEngine] = None
        
        self.setup_ui()
        self.setup_menu()
        self.apply_theme()
    
    def setup_ui(self):
        """Set up the main UI."""
        self.setWindowTitle("Markdown Merger - AI Knowledge Base Builder")
        self.setMinimumSize(1000, 700)
        self.resize(
            self.app_config.window_width,
            self.app_config.window_height
        )
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Main splitter for file list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - File management
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # File list group
        file_group = QGroupBox("Input Files")
        file_layout = QVBoxLayout(file_group)
        
        # File action buttons
        btn_row = QHBoxLayout()
        self.btn_add_files = QPushButton("📄 Add Files")
        self.btn_add_files.clicked.connect(self.add_files)
        self.btn_add_folder = QPushButton("📁 Add Folder")
        self.btn_add_folder.clicked.connect(self.add_folder)
        self.btn_clear = QPushButton("Clear")
        self.btn_clear.clicked.connect(self.clear_files)
        self.btn_remove = QPushButton("Remove Selected")
        self.btn_remove.clicked.connect(self.remove_selected)
        
        btn_row.addWidget(self.btn_add_files)
        btn_row.addWidget(self.btn_add_folder)
        btn_row.addWidget(self.btn_clear)
        btn_row.addWidget(self.btn_remove)
        file_layout.addLayout(btn_row)
        
        # File list
        self.file_list = FileListWidget()
        self.file_list.files_dropped.connect(self.add_paths)
        self.file_list.itemSelectionChanged.connect(self.on_selection_changed)
        file_layout.addWidget(self.file_list)
        
        # File stats
        self.file_stats = QLabel("No files selected")
        file_layout.addWidget(self.file_stats)
        
        left_layout.addWidget(file_group)
        
        # Right panel - Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Consolas", 10))
        preview_layout.addWidget(self.preview_text)
        
        self.btn_refresh_preview = QPushButton("Refresh Preview")
        self.btn_refresh_preview.clicked.connect(self.refresh_preview)
        preview_layout.addWidget(self.btn_refresh_preview)
        
        right_layout.addWidget(preview_group)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 500])
        
        main_layout.addWidget(splitter, stretch=1)
        
        # Settings section
        settings_group = QGroupBox("Merge Settings")
        settings_layout = QHBoxLayout(settings_group)
        
        # Preset selector
        settings_layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(PRESETS.keys()))
        self.preset_combo.setCurrentText("ai_knowledge_base")
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        settings_layout.addWidget(self.preset_combo)
        
        # Quick settings
        settings_layout.addWidget(QLabel("Separator:"))
        self.separator_combo = QComboBox()
        self.separator_combo.addItems(["---", "***", "___", "None"])
        self.separator_combo.currentTextChanged.connect(self.on_separator_changed)
        settings_layout.addWidget(self.separator_combo)
        
        settings_layout.addWidget(QLabel("Header:"))
        self.header_combo = QComboBox()
        self.header_combo.addItems(["# {name}", "## {name}", "### {name}"])
        self.header_combo.setCurrentIndex(1)
        self.header_combo.currentTextChanged.connect(self.on_header_changed)
        settings_layout.addWidget(self.header_combo)
        
        self.toc_check = QCheckBox("Generate TOC")
        self.toc_check.setChecked(True)
        self.toc_check.stateChanged.connect(self.on_toc_changed)
        settings_layout.addWidget(self.toc_check)
        
        self.metadata_check = QCheckBox("Add Metadata")
        self.metadata_check.setChecked(True)
        self.metadata_check.stateChanged.connect(self.on_metadata_changed)
        settings_layout.addWidget(self.metadata_check)
        
        settings_layout.addStretch()
        
        self.btn_advanced = QPushButton("⚙ Advanced Settings...")
        self.btn_advanced.clicked.connect(self.show_advanced_settings)
        settings_layout.addWidget(self.btn_advanced)
        
        main_layout.addWidget(settings_group)
        
        # Output section
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output:"))
        
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output file...")
        output_layout.addWidget(self.output_path, stretch=1)
        
        self.btn_browse_output = QPushButton("📁 Browse")
        self.btn_browse_output.clicked.connect(self.browse_output)
        output_layout.addWidget(self.btn_browse_output)
        
        main_layout.addLayout(output_layout)
        
        # Action buttons and progress
        action_layout = QHBoxLayout()
        
        self.btn_merge = QPushButton("▶ Start Merge")
        self.btn_merge.setMinimumHeight(40)
        self.btn_merge.clicked.connect(self.start_merge)
        action_layout.addWidget(self.btn_merge)
        
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.toggle_pause)
        action_layout.addWidget(self.btn_pause)
        
        self.btn_cancel = QPushButton("⏹ Cancel")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self.cancel_merge)
        action_layout.addWidget(self.btn_cancel)
        
        action_layout.addStretch()
        
        self.status_label = QLabel("Ready")
        action_layout.addWidget(self.status_label)
        
        main_layout.addLayout(action_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        # Log area
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_group)
        
        # Status bar
        self.statusBar().showMessage("Ready - Drag and drop files or folders to begin")
    
    def setup_menu(self):
        """Set up menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        add_files_action = QAction("Add Files...", self)
        add_files_action.setShortcut("Ctrl+O")
        add_files_action.triggered.connect(self.add_files)
        file_menu.addAction(add_files_action)
        
        add_folder_action = QAction("Add Folder...", self)
        add_folder_action.setShortcut("Ctrl+Shift+O")
        add_folder_action.triggered.connect(self.add_folder)
        file_menu.addAction(add_folder_action)
        
        file_menu.addSeparator()
        
        save_config_action = QAction("Save Configuration...", self)
        save_config_action.triggered.connect(self.save_config)
        file_menu.addAction(save_config_action)
        
        load_config_action = QAction("Load Configuration...", self)
        load_config_action.triggered.connect(self.load_config)
        file_menu.addAction(load_config_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        clear_action = QAction("Clear All Files", self)
        clear_action.triggered.connect(self.clear_files)
        edit_menu.addAction(clear_action)
        
        settings_action = QAction("Advanced Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_advanced_settings)
        edit_menu.addAction(settings_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("Refresh Preview", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_preview)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        self.dark_mode_action = QAction("Dark Mode", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.app_config.theme == "dark")
        self.dark_mode_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.dark_mode_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_theme(self):
        """Apply current theme."""
        if self.app_config.theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    margin-top: 10px;
                    padding-top: 10px;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QListWidget, QTextEdit, QLineEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #2a2a2a;
                }
                QComboBox {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 3px;
                }
                QProgressBar {
                    border: 1px solid #555555;
                    background-color: #1e1e1e;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #0078d4;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar::item:selected {
                    background-color: #3c3c3c;
                }
                QMenu {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenu::item:selected {
                    background-color: #3c3c3c;
                }
            """)
        else:
            self.setStyleSheet("")
    
    def toggle_theme(self):
        """Toggle between dark and light theme."""
        self.app_config.theme = "dark" if self.app_config.theme == "light" else "light"
        self.apply_theme()
        self.app_config.save()
    
    def add_files(self):
        """Open file dialog to add markdown files."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Markdown Files",
            self.app_config.last_input_dir or "",
            "Markdown Files (*.md *.markdown);;All Files (*)"
        )
        if files:
            self.app_config.last_input_dir = str(Path(files[0]).parent)
            self.add_paths([Path(f) for f in files])
    
    def add_folder(self):
        """Open folder dialog to add markdown files from directory."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            self.app_config.last_input_dir or ""
        )
        if folder:
            self.app_config.last_input_dir = folder
            self.add_paths([Path(folder)])
    
    def add_paths(self, paths: List[Path]):
        """Add files from given paths."""
        analyzer = FileAnalyzer(self.config)
        
        self.log(f"Scanning {len(paths)} path(s)...")
        
        new_files = analyzer.discover_files(
            paths,
            progress_callback=lambda msg: self.statusBar().showMessage(msg)
        )
        
        # Add to existing files (avoiding duplicates)
        existing_paths = {f.path for f in self.files}
        for f in new_files:
            if f.path not in existing_paths:
                self.files.append(f)
        
        self.update_file_list()
        self.log(f"Added {len(new_files)} file(s). Total: {len(self.files)}")
    
    def update_file_list(self):
        """Update the file list widget."""
        self.file_list.clear()
        
        for f in self.files:
            item = QListWidgetItem(f"{f.path.name}  ({f.size_formatted})")
            item.setData(Qt.ItemDataRole.UserRole, f)
            item.setToolTip(str(f.path))
            self.file_list.addItem(item)
        
        # Update stats
        total_size = sum(f.size for f in self.files)
        self.file_stats.setText(
            f"Total: {len(self.files)} files, {format_file_size(total_size)}"
        )
    
    def clear_files(self):
        """Clear all files from the list."""
        self.files.clear()
        self.file_list.clear()
        self.file_stats.setText("No files selected")
        self.preview_text.clear()
        self.log("Cleared all files")
    
    def remove_selected(self):
        """Remove selected files from the list."""
        selected = self.file_list.selectedItems()
        for item in selected:
            file_info = item.data(Qt.ItemDataRole.UserRole)
            if file_info in self.files:
                self.files.remove(file_info)
        self.update_file_list()
        self.log(f"Removed {len(selected)} file(s)")
    
    def on_selection_changed(self):
        """Handle file selection change."""
        selected = self.file_list.selectedItems()
        if len(selected) == 1:
            file_info = selected[0].data(Qt.ItemDataRole.UserRole)
            self.preview_text.setPlainText(file_info.preview)
    
    def browse_output(self):
        """Browse for output file location."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Merged File",
            self.app_config.last_output_dir or "merged.md",
            "Markdown Files (*.md);;All Files (*)"
        )
        if file_path:
            self.output_path.setText(file_path)
            self.app_config.last_output_dir = str(Path(file_path).parent)
    
    def on_preset_changed(self, preset_name: str):
        """Handle preset selection change."""
        self.config = get_preset(preset_name)
        self.update_ui_from_config()
        self.log(f"Applied preset: {preset_name}")
    
    def on_separator_changed(self, separator: str):
        """Handle separator selection change."""
        if separator == "None":
            self.config.separator_style = ""
        else:
            self.config.separator_style = separator
    
    def on_header_changed(self, header: str):
        """Handle header style change."""
        self.config.header_style = header
    
    def on_toc_changed(self, state):
        """Handle TOC checkbox change."""
        self.config.generate_toc = state == Qt.CheckState.Checked.value
    
    def on_metadata_changed(self, state):
        """Handle metadata checkbox change."""
        self.config.add_metadata = state == Qt.CheckState.Checked.value
    
    def update_ui_from_config(self):
        """Update UI controls from current config."""
        self.toc_check.setChecked(self.config.generate_toc)
        self.metadata_check.setChecked(self.config.add_metadata)
        
        # Update separator combo
        if self.config.separator_style in ["---", "***", "___"]:
            self.separator_combo.setCurrentText(self.config.separator_style)
        elif not self.config.separator_style:
            self.separator_combo.setCurrentText("None")
        
        # Update header combo
        if self.config.header_style in ["# {name}", "## {name}", "### {name}"]:
            self.header_combo.setCurrentText(self.config.header_style)
    
    def show_advanced_settings(self):
        """Show advanced settings dialog."""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.config = dialog.get_config()
            self.update_ui_from_config()
            self.log("Settings updated")
    
    def refresh_preview(self):
        """Refresh the merge preview."""
        if not self.files:
            self.preview_text.setPlainText("No files to preview.")
            return
        
        engine = MergeEngine(self.config)
        preview = engine.generate_preview(self.files, max_lines=100)
        self.preview_text.setPlainText(preview)
    
    def start_merge(self):
        """Start the merge operation."""
        if not self.files:
            QMessageBox.warning(self, "No Files", "Please add files to merge.")
            return
        
        output = self.output_path.text().strip()
        if not output:
            QMessageBox.warning(self, "No Output", "Please specify an output file.")
            return
        
        output_path = Path(output)
        
        # Confirm overwrite
        if output_path.exists():
            reply = QMessageBox.question(
                self,
                "Overwrite File",
                f"{output_path.name} already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Prepare merge
        self.engine = MergeEngine(self.config)
        self.worker = MergeWorker(self.engine, self.files, output_path)
        self.worker.progress.connect(self.on_merge_progress)
        self.worker.finished.connect(self.on_merge_finished)
        self.worker.log_message.connect(self.log)
        
        # Update UI
        self.btn_merge.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_cancel.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Merging...")
        
        self.log(f"Starting merge of {len(self.files)} files...")
        self.worker.start()
    
    def on_merge_progress(self, progress: MergeProgress):
        """Handle merge progress update."""
        self.progress_bar.setValue(int(progress.percent))
        self.status_label.setText(
            f"Processing: {progress.current_file} "
            f"({progress.current_index}/{progress.total_files})"
        )
    
    def on_merge_finished(self, result: MergeResult):
        """Handle merge completion."""
        self.btn_merge.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        
        if result.success:
            self.progress_bar.setValue(100)
            self.status_label.setText("Merge completed!")
            self.log(f"✓ {result.summary}")
            
            # Show success message
            QMessageBox.information(
                self,
                "Merge Complete",
                f"Successfully merged {result.files_merged} files.\n\n"
                f"Output: {result.output_path}\n"
                f"Total size: {format_file_size(result.total_size)}\n"
                f"Time: {result.duration_seconds:.2f}s"
            )
        else:
            self.status_label.setText("Merge failed!")
            self.log(f"✗ {result.summary}")
            for error in result.errors:
                self.log(f"  Error: {error}")
            
            QMessageBox.critical(
                self,
                "Merge Failed",
                f"Merge failed with {len(result.errors)} error(s).\n\n"
                f"{result.errors[0] if result.errors else 'Unknown error'}"
            )
        
        for warning in result.warnings:
            self.log(f"  ⚠ {warning}")
    
    def toggle_pause(self):
        """Toggle pause/resume of merge operation."""
        if self.engine:
            if self.btn_pause.text() == "⏸ Pause":
                self.engine.pause()
                self.btn_pause.setText("▶ Resume")
                self.status_label.setText("Paused")
                self.log("Merge paused")
            else:
                self.engine.resume()
                self.btn_pause.setText("⏸ Pause")
                self.log("Merge resumed")
    
    def cancel_merge(self):
        """Cancel the merge operation."""
        if self.engine:
            reply = QMessageBox.question(
                self,
                "Cancel Merge",
                "Are you sure you want to cancel the merge?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.engine.cancel()
                self.log("Merge cancelled")
    
    def save_config(self):
        """Save current configuration to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            "merge_config.json",
            "JSON Files (*.json)"
        )
        if file_path:
            self.config.save(Path(file_path))
            self.log(f"Configuration saved to {file_path}")
    
    def load_config(self):
        """Load configuration from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            "",
            "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.config = MergeConfig.load(Path(file_path))
                self.update_ui_from_config()
                self.log(f"Configuration loaded from {file_path}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to load configuration: {e}"
                )
    
    def log(self, message: str):
        """Add message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Markdown Merger",
            "<h2>Markdown Merger</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A powerful tool for merging multiple markdown files "
            "into a single, well-structured document optimized for "
            "AI knowledge base ingestion.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Merge hundreds or thousands of .md files</li>"
            "<li>Auto-generate table of contents</li>"
            "<li>Add AI-friendly metadata and markers</li>"
            "<li>Configurable separators and headers</li>"
            "<li>Drag-and-drop file management</li>"
            "</ul>"
        )
    
    def closeEvent(self, event):
        """Handle window close."""
        # Save window size
        self.app_config.window_width = self.width()
        self.app_config.window_height = self.height()
        self.app_config.save()
        
        # Cancel any running merge
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "A merge is in progress. Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self.engine.cancel()
            self.worker.wait(2000)
        
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Merger")
    app.setApplicationVersion("1.0.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
