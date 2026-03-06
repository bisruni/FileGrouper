"""PySide6 desktop interface for previewing and applying file operations."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Slot
from PySide6.QtGui import QAction, QCloseEvent, QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

try:
    import qdarktheme  # type: ignore
except ImportError:
    qdarktheme = None

from .config_service import AppConfig, AppConfigService
from .constants import quarantine_dir
from .gui_components import DuplicateGroupDialog, FiltersDialog, UiFilterDraft, Worker
from .gui_texts import DEDUPE_ITEMS, MODE_ITEMS, TR, WORKFLOW_ITEMS
from .gui_theme import apply_gui_theme
from .logger import configure_logging, get_logger
from .models import (
    DedupeMode,
    DuplicateGroup,
    ExecutionScope,
    OperationProfile,
    OperationProgress,
    OperationSummary,
    OrganizationMode,
    ScanFilterOptions,
)
from .pause_controller import PauseController
from .pipeline import FileGrouperEngine, RunOptions, RunResult
from .profile_service import ProfileService
from .utils import format_size


class MainWindow(QMainWindow):
    """Main desktop window coordinating user actions and pipeline runs."""

    def __init__(self) -> None:
        """Initialize main window state, widgets and signal wiring."""
        super().__init__()
        self.app_logger = get_logger("gui")
        self.config_service = AppConfigService()
        self.app_config: AppConfig = self.config_service.load_resolved_config()
        self.profile_service = ProfileService()
        self.profiles: list[OperationProfile] = self.profile_service.load_profiles()
        self.engine = FileGrouperEngine()
        self.similar_supported = self.engine.detector.is_similar_supported()

        self.setWindowTitle(TR["title"])
        self.setMinimumSize(1100, 720)

        self.filters_draft = UiFilterDraft()

        self.worker_thread: QThread | None = None
        self.worker: Worker | None = None
        self.cancel_event: threading.Event | None = None
        self.pause_controller = PauseController()
        self.paused = False
        self.last_result: RunResult | None = None
        self.preview_duplicate_groups: list[DuplicateGroup] = []
        self.protected_duplicate_paths: set[str] = set()
        self.last_run_scope: ExecutionScope = ExecutionScope.GROUP_AND_DEDUPE
        self.last_run_dedupe_mode: DedupeMode = DedupeMode.QUARANTINE
        self.last_run_apply_changes: bool = False
        self.preview_quarantine_estimate = 0
        self.preview_organize_estimate = 0
        self._last_progress_ui_update = 0.0
        self._progress_ui_min_interval_seconds = 0.05

        self._build_ui()
        self._load_profiles_into_ui()
        self._apply_startup_defaults()
        self._set_running(False)
        self._set_status(TR["ready"])

    # ---- UI construction ----

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout()
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(14)
        central.setLayout(root)

        # Top bar
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        title_col = QVBoxLayout()
        self.title_lbl = QLabel(TR["title"])
        self.title_lbl.setStyleSheet("font-weight:700; font-size:22px; letter-spacing:0.2px;")
        self.sub_lbl = QLabel(TR["subtitle"])
        self.sub_lbl.setStyleSheet("color: rgba(100,100,110,1);")
        title_col.addWidget(self.title_lbl)
        title_col.addWidget(self.sub_lbl)
        title_row.addLayout(title_col)
        title_row.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.profile_lbl = QLabel(TR["profile"])
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(180)
        self.profile_apply_btn = QPushButton(TR["profile_apply"])
        self.profile_apply_btn.clicked.connect(self._apply_selected_profile)
        title_row.addWidget(self.profile_lbl)
        title_row.addWidget(self.profile_combo)
        title_row.addWidget(self.profile_apply_btn)

        self.dry_check = QCheckBox(TR["dry_run"])
        self.dry_check.setChecked(True)
        self.similar_check = QCheckBox(TR["similar"])
        if not self.similar_supported:
            self.similar_check.setChecked(False)
            self.similar_check.setEnabled(False)
            self.similar_check.setToolTip(TR["similar_unavailable"])
        title_row.addWidget(self.dry_check)
        title_row.addWidget(self.similar_check)

        root.addLayout(title_row)

        workflow_card = QGroupBox(TR["workflow"])
        workflow_layout = QVBoxLayout()
        workflow_layout.setContentsMargins(10, 8, 10, 8)
        workflow_layout.setSpacing(6)
        workflow_card.setLayout(workflow_layout)

        self.workflow_tabs = QTabWidget()
        for title, _scope, desc in WORKFLOW_ITEMS:
            page = QWidget()
            page_layout = QVBoxLayout()
            page_layout.setContentsMargins(10, 8, 10, 8)
            hint = QLabel(desc)
            hint.setStyleSheet("color: #6b7280;")
            page_layout.addWidget(hint)
            page_layout.addStretch(1)
            page.setLayout(page_layout)
            self.workflow_tabs.addTab(page, title)
        self.workflow_tabs.currentChanged.connect(self._on_workflow_changed)
        workflow_layout.addWidget(self.workflow_tabs)
        self.workflow_hint_lbl = QLabel(TR["workflow_hint"])
        self.workflow_hint_lbl.setStyleSheet("color: #6b7280; font-size: 11px;")
        workflow_layout.addWidget(self.workflow_hint_lbl)
        root.addWidget(workflow_card)

        # Card: inputs + options
        card = QGroupBox()
        card.setTitle("")
        card_layout = QGridLayout()
        card_layout.setHorizontalSpacing(10)
        card_layout.setVerticalSpacing(10)
        card.setLayout(card_layout)

        self.source_edit = QLineEdit()
        self.target_edit = QLineEdit()
        self.source_edit.setPlaceholderText("/Volumes/USB")
        self.target_edit.setPlaceholderText("/Volumes/USB_Organized")
        self.source_edit.setMinimumHeight(36)
        self.target_edit.setMinimumHeight(36)

        src_btn = QPushButton(TR["browse"])
        tgt_btn = QPushButton(TR["browse"])
        src_btn.setMinimumHeight(36)
        tgt_btn.setMinimumHeight(36)
        src_btn.clicked.connect(self._browse_source)
        tgt_btn.clicked.connect(self._browse_target)

        self.source_lbl = QLabel(TR["source"])
        card_layout.addWidget(self.source_lbl, 0, 0)
        card_layout.addWidget(self.source_edit, 0, 1)
        card_layout.addWidget(src_btn, 0, 2)

        self.target_lbl = QLabel(TR["target"])
        self.target_btn = tgt_btn
        card_layout.addWidget(self.target_lbl, 1, 0)
        card_layout.addWidget(self.target_edit, 1, 1)
        card_layout.addWidget(tgt_btn, 1, 2)

        # Options column
        opt_box = QVBoxLayout()
        self.mode_combo = QComboBox()
        for label, _ in MODE_ITEMS:
            self.mode_combo.addItem(label)
        self.mode_combo.setMinimumHeight(36)
        self.dedupe_combo = QComboBox()
        for label, _ in DEDUPE_ITEMS:
            self.dedupe_combo.addItem(label)
        self.dedupe_combo.setMinimumHeight(36)

        opt_grid = QGridLayout()
        self.mode_lbl = QLabel(TR["mode"])
        self.dedupe_lbl = QLabel(TR["dedupe"])
        opt_grid.addWidget(self.mode_lbl, 0, 0)
        opt_grid.addWidget(self.mode_combo, 0, 1)
        opt_grid.addWidget(self.dedupe_lbl, 1, 0)
        opt_grid.addWidget(self.dedupe_combo, 1, 1)

        opt_box.addLayout(opt_grid)

        self.filters_btn = QPushButton(TR["filters"])
        self.filters_btn.setMinimumHeight(36)
        self.filters_btn.clicked.connect(self._open_filters)
        opt_box.addWidget(self.filters_btn)

        card_layout.addLayout(opt_box, 0, 3, 2, 1)

        root.addWidget(card)

        # Actions
        actions = QHBoxLayout()
        self.preview_btn = QPushButton(TR["preview"])
        self.apply_btn = QPushButton(TR["apply"])
        self.pause_btn = QPushButton(TR["pause"])
        self.cancel_btn = QPushButton(TR["cancel"])

        self.preview_btn.clicked.connect(lambda: self._start_run(False))
        self.apply_btn.clicked.connect(lambda: self._start_run(True))
        self.pause_btn.clicked.connect(self._toggle_pause)
        self.cancel_btn.clicked.connect(self._cancel_run)
        self.preview_btn.setObjectName("primaryBtn")
        self.apply_btn.setObjectName("primaryBtn")
        self.cancel_btn.setObjectName("dangerBtn")

        self.preview_btn.setMinimumWidth(140)
        self.apply_btn.setMinimumWidth(140)
        self.preview_btn.setMinimumHeight(38)
        self.apply_btn.setMinimumHeight(38)
        self.pause_btn.setMinimumHeight(38)
        self.cancel_btn.setMinimumHeight(38)

        actions.addWidget(self.preview_btn)
        actions.addWidget(self.apply_btn)
        actions.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        actions.addWidget(self.pause_btn)
        actions.addWidget(self.cancel_btn)
        root.addLayout(actions)

        # Status + progress
        stat_row = QHBoxLayout()
        self.status_lbl = QLabel(TR["ready"])
        self.progress_lbl = QLabel("0%")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)

        stat_row.addWidget(self.status_lbl)
        stat_row.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        stat_row.addWidget(self.progress_lbl)

        root.addLayout(stat_row)
        root.addWidget(self.progress)

        # Metrics
        metrics = QHBoxLayout()
        self.m_total = QLabel("0")
        self.m_size = QLabel("0 B")
        self.m_dupes = QLabel("0")
        self.m_reclaim = QLabel("0 B")
        self.m_errors = QLabel("0")
        self.m_similar = QLabel("0")

        def metric(title: str, value_lbl: QLabel) -> QWidget:
            w = QWidget()
            v = QVBoxLayout()
            v.setContentsMargins(0, 0, 0, 0)
            t = QLabel(title)
            t.setStyleSheet("color: rgba(127,127,127,1);")
            value_lbl.setStyleSheet("font-weight:700; font-size:14px;")
            v.addWidget(t)
            v.addWidget(value_lbl)
            w.setLayout(v)
            return w

        metrics.addWidget(metric("Toplam", self.m_total))
        metrics.addWidget(metric("Boyut", self.m_size))
        metrics.addWidget(metric("Kopya", self.m_dupes))
        metrics.addWidget(metric("Kazanım", self.m_reclaim))
        metrics.addWidget(metric("Hata", self.m_errors))
        metrics.addWidget(metric("Benzer", self.m_similar))
        root.addLayout(metrics)

        # Preview summary (trust layer)
        preview_box = QGroupBox(TR["preview_summary"])
        preview_layout = QGridLayout()
        preview_layout.setHorizontalSpacing(14)
        preview_layout.setVerticalSpacing(6)
        preview_box.setLayout(preview_layout)
        self.p_total = QLabel("0")
        self.p_dupes = QLabel("0")
        self.p_dupe_groups = QLabel("0")
        self.p_reclaim = QLabel("0 B")
        self.p_quarantine = QLabel("0")
        self.p_organize = QLabel("0")
        self.p_errors = QLabel("0")
        self.p_skipped = QLabel("0")
        preview_layout.addWidget(QLabel(TR["sum_total"]), 0, 0)
        preview_layout.addWidget(self.p_total, 0, 1)
        preview_layout.addWidget(QLabel(TR["sum_dupes"]), 0, 2)
        preview_layout.addWidget(self.p_dupes, 0, 3)
        preview_layout.addWidget(QLabel(TR["sum_dupe_groups"]), 0, 4)
        preview_layout.addWidget(self.p_dupe_groups, 0, 5)
        preview_layout.addWidget(QLabel(TR["sum_reclaim"]), 0, 6)
        preview_layout.addWidget(self.p_reclaim, 0, 7)
        preview_layout.addWidget(QLabel(TR["sum_quarantine"]), 1, 0)
        preview_layout.addWidget(self.p_quarantine, 1, 1)
        preview_layout.addWidget(QLabel(TR["sum_organize"]), 1, 2)
        preview_layout.addWidget(self.p_organize, 1, 3)
        preview_layout.addWidget(QLabel(TR["sum_errors"]), 1, 4)
        preview_layout.addWidget(self.p_errors, 1, 5)
        preview_layout.addWidget(QLabel(TR["sum_skipped"]), 1, 6)
        preview_layout.addWidget(self.p_skipped, 1, 7)
        root.addWidget(preview_box)

        # Tabs
        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        # Duplicates table
        dupes_wrap = QWidget()
        dupes_layout = QVBoxLayout()
        dupes_layout.setContentsMargins(0, 0, 0, 0)
        dupes_wrap.setLayout(dupes_layout)

        dupes_toolbar = QHBoxLayout()
        self.dupe_detail_btn = QPushButton(TR["dupe_detail"])
        self.dupe_detail_btn.clicked.connect(self._open_selected_duplicate_group_dialog)
        dupes_toolbar.addWidget(self.dupe_detail_btn)
        dupes_toolbar.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        dupes_layout.addLayout(dupes_toolbar)

        self.dupes_table = QTableWidget(0, 4)
        self.dupes_table.setHorizontalHeaderLabels(["Hash", "Kaldır", "Boyut", "Koru/Kalacak"])
        self.dupes_table.horizontalHeader().setStretchLastSection(True)
        self.dupes_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.dupes_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.dupes_table.setAlternatingRowColors(True)
        self.dupes_table.setToolTip("Cift tiklayinca dosya konumu acilir.")
        self.dupes_table.cellDoubleClicked.connect(self._open_duplicate_location_from_table)
        dupes_layout.addWidget(self.dupes_table)
        self.tabs.addTab(dupes_wrap, TR["tab_dupes"])

        # Logs
        logs_wrap = QWidget()
        logs_layout = QVBoxLayout()
        logs_wrap.setLayout(logs_layout)

        toolbar = QHBoxLayout()
        self.clear_logs_btn = QPushButton("Log temizle")
        self.open_quarantine_btn = QPushButton(TR["open_quarantine"])
        self.undo_btn = QPushButton(TR["undo"])
        self.export_btn = QPushButton(TR["export"])
        self.clear_logs_btn.clicked.connect(self._clear_logs)
        self.open_quarantine_btn.clicked.connect(self._open_quarantine_folder)
        self.undo_btn.clicked.connect(self._undo_last)
        self.export_btn.clicked.connect(self._export_report)

        toolbar.addWidget(self.clear_logs_btn)
        toolbar.addWidget(self.open_quarantine_btn)
        toolbar.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        toolbar.addWidget(self.undo_btn)
        toolbar.addWidget(self.export_btn)
        logs_layout.addLayout(toolbar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        logs_layout.addWidget(self.log_text)

        self.tabs.addTab(logs_wrap, TR["tab_logs"])

        # Menu (tiny)
        m = self.menuBar().addMenu("Dosya")
        act_quit = QAction("Çıkış", self)
        act_quit.triggered.connect(self.close)
        m.addAction(act_quit)

        self._on_workflow_changed(self.workflow_tabs.currentIndex())
        self.setStyleSheet(self.styleSheet() + """
QPushButton#primaryBtn { background: #2563eb; color: #ffffff; border: 1px solid #1d4ed8; font-weight: 600; }
QPushButton#primaryBtn:hover { background: #1d4ed8; }
QPushButton#primaryBtn:pressed { background: #1e40af; }
QPushButton#dangerBtn { background: #fff5f5; color: #b91c1c; border: 1px solid #fecaca; }
QPushButton#dangerBtn:hover { background: #fee2e2; }
""")

    # ---- actions ----

    def _browse_source(self) -> None:
        path = QFileDialog.getExistingDirectory(self, TR["source"])
        if path:
            self.source_edit.setText(path)
            if not self.target_edit.text().strip():
                p = Path(path)
                self.target_edit.setText(str(p.parent / f"{p.name}_Organized"))

    def _browse_target(self) -> None:
        path = QFileDialog.getExistingDirectory(self, TR["target"])
        if path:
            self.target_edit.setText(path)

    def _open_filters(self) -> None:
        dlg = FiltersDialog(self, self.filters_draft)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.filter_result is not None:
            self.filters_draft = dlg.filter_result
            self._log("Filtreler güncellendi.")

    def _open_quarantine_folder(self) -> None:
        source_text = self.source_edit.text().strip()
        target_text = self.target_edit.text().strip()
        base: Path | None
        if self.last_result is not None:
            base = self.last_result.target_path
        else:
            base = Path(target_text) if target_text else (Path(source_text) if source_text else None)
        if base is None:
            QMessageBox.information(self, TR["open_quarantine"], TR["quarantine_missing"])
            return
        folder = quarantine_dir(base)
        if not folder.exists():
            QMessageBox.information(self, TR["open_quarantine"], TR["quarantine_missing"])
            return
        self._open_path_in_file_manager(folder)

    def _toggle_pause(self) -> None:
        if not self._is_running():
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_controller.pause()
            self._set_status(TR["paused"])
            self.pause_btn.setText(TR["resume"])
        else:
            self.pause_controller.resume()
            self._set_status(TR["running"])
            self.pause_btn.setText(TR["pause"])

    def _cancel_run(self) -> None:
        if not self._is_running():
            return
        if self.cancel_event is not None:
            self.cancel_event.set()
        # If user cancels while paused, unblock worker immediately.
        self.pause_controller.resume()
        self.paused = False
        self.pause_btn.setText(TR["pause"])
        self._set_status(TR["cancelled"])

    def _open_selected_duplicate_group_dialog(self) -> None:
        row = self.dupes_table.currentRow()
        if row < 0:
            return
        self._open_duplicate_group_dialog(row, 0)

    @Slot(int)
    def _on_workflow_changed(self, index: int) -> None:
        if index < 0 or index >= len(WORKFLOW_ITEMS):
            return
        scope = WORKFLOW_ITEMS[index][1]
        includes_grouping = scope.includes_grouping
        includes_dedupe = scope.includes_dedupe

        self.mode_lbl.setEnabled(includes_grouping)
        self.mode_combo.setEnabled(includes_grouping and not self._is_running())

        self.dedupe_lbl.setEnabled(includes_dedupe)
        self.dedupe_combo.setEnabled(includes_dedupe and not self._is_running())

        self.target_lbl.setEnabled(includes_grouping)
        self.target_edit.setEnabled(includes_grouping and not self._is_running())
        self.target_btn.setEnabled(includes_grouping and not self._is_running())
        if includes_grouping:
            self.target_edit.setPlaceholderText("")
        else:
            self.target_edit.setPlaceholderText(TR["target_not_needed"])

        if includes_dedupe:
            self.similar_check.setEnabled(self.similar_supported and not self._is_running())
        else:
            self.similar_check.setChecked(False)
            self.similar_check.setEnabled(False)

    def _load_profiles_into_ui(self) -> None:
        """Populate profile combo from persisted profile storage."""
        self.profiles = self.profile_service.load_profiles()
        self.profile_combo.clear()
        for profile in self.profiles:
            self.profile_combo.addItem(profile.name)
        has_profiles = bool(self.profiles)
        self.profile_combo.setEnabled(has_profiles)
        self.profile_apply_btn.setEnabled(has_profiles)

    def _apply_startup_defaults(self) -> None:
        """Apply resolved config defaults and optional default profile."""
        self._set_scope_combo(self.app_config.default_scope)
        self._set_mode_combo(self.app_config.default_mode)
        self._set_dedupe_combo(self.app_config.default_dedupe)
        self.dry_check.setChecked(self.app_config.default_dry_run)
        self.similar_check.setChecked(self.similar_supported and self.app_config.default_similar_images)
        if self.app_config.default_profile:
            index = self.profile_combo.findText(self.app_config.default_profile, Qt.MatchFlag.MatchFixedString)
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)
                self._apply_selected_profile()

    def _set_scope_combo(self, scope: ExecutionScope) -> None:
        for index, (_title, item_scope, _desc) in enumerate(WORKFLOW_ITEMS):
            if item_scope is scope:
                self.workflow_tabs.setCurrentIndex(index)
                return

    def _set_mode_combo(self, mode: OrganizationMode) -> None:
        for label, item_mode in MODE_ITEMS:
            if item_mode is mode:
                self.mode_combo.setCurrentText(label)
                return

    def _set_dedupe_combo(self, dedupe_mode: DedupeMode) -> None:
        for label, item_mode in DEDUPE_ITEMS:
            if item_mode is dedupe_mode:
                self.dedupe_combo.setCurrentText(label)
                return

    @Slot()
    def _apply_selected_profile(self) -> None:
        """Apply selected profile values to current GUI controls."""
        if not self.profiles:
            return
        index = self.profile_combo.currentIndex()
        if index < 0 or index >= len(self.profiles):
            return
        profile = self.profiles[index]
        self._set_scope_combo(profile.execution_scope)
        self._set_mode_combo(profile.organization_mode)
        self._set_dedupe_combo(profile.dedupe_mode)
        self.dry_check.setChecked(profile.is_dry_run)
        self.similar_check.setChecked(self.similar_supported and profile.detect_similar_images)
        self.filters_draft = self._draft_from_filter_options(profile.filter_options)
        self._log(f"{TR['profile_loaded']}: {profile.name}")

    @staticmethod
    def _draft_from_filter_options(options: ScanFilterOptions) -> UiFilterDraft:
        """Convert scan filter options into editable draft strings."""
        return UiFilterDraft(
            include_ext=",".join(options.include_extensions),
            exclude_ext=",".join(options.exclude_extensions),
            min_mb=(f"{options.min_size_bytes / (1024 * 1024):.2f}" if options.min_size_bytes else ""),
            max_mb=(f"{options.max_size_bytes / (1024 * 1024):.2f}" if options.max_size_bytes else ""),
            from_date=(options.from_utc.date().isoformat() if options.from_utc else ""),
            to_date=(options.to_utc.date().isoformat() if options.to_utc else ""),
        )

    def _undo_last(self) -> None:
        target_text = self.target_edit.text().strip()
        if not target_text:
            QMessageBox.warning(self, TR["err"], TR["need_target_undo"])
            return
        try:
            summary = self.engine.transaction_service.undo_last_transaction(Path(target_text))
        except (RuntimeError, OSError, IOError, ValueError) as exc:
            QMessageBox.critical(self, TR["err"], str(exc))
            return

        self._set_metrics_from_summary(summary, similar_count=int(self.m_similar.text() or "0"))
        self._set_status("Geri alındı")
        self._log("Undo tamamlandı.")

    def _export_report(self) -> None:
        if self.last_result is None:
            QMessageBox.warning(self, TR["err"], TR["need_preview"])
            return
        directory = QFileDialog.getExistingDirectory(self, "Rapor klasörü seç")
        if not directory:
            return
        report = self.engine.build_report(self.last_result)
        json_path, csv_path, pdf_path = self.engine.report_exporter.export(report, Path(directory))
        QMessageBox.information(self, "Rapor", f"{json_path.name}\n{csv_path.name}\n{pdf_path.name}")

    # ---- run pipeline ----

    def _start_run(self, apply_changes: bool) -> None:
        if self._is_running():
            return

        source_text = self.source_edit.text().strip()
        target_text = self.target_edit.text().strip()

        if not source_text:
            QMessageBox.warning(self, TR["err"], TR["need_source"])
            return

        source = Path(source_text)
        target = Path(target_text) if target_text else None
        scope = self._scope_enum()

        error = self.engine.validate_paths(source, target, scope)
        if error and apply_changes:
            QMessageBox.critical(self, TR["err"], self._friendly_error_message(error))
            return

        if apply_changes and not self._confirm_apply(scope):
            return

        # “Sil” seçildiyse ekstra uyarı (satılacak ürün: kazaya izin yok)
        if self._dedupe_enum() == DedupeMode.DELETE and apply_changes and not self.dry_check.isChecked():
            ok = QMessageBox.question(
                self,
                "Tehlikeli İşlem",
                "Kopya modu 'Sil' ve test modu kapalı.\nBu işlem geri alınamaz.\nEmin misin?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if ok != QMessageBox.StandardButton.Yes:
                return

        # reset ui
        self._clear_logs()
        self._clear_dupes_table()
        self.last_result = None
        if not apply_changes:
            self.preview_duplicate_groups = []
            self.protected_duplicate_paths = set()
            self.preview_quarantine_estimate = 0
            self.preview_organize_estimate = 0
        self.progress.setValue(0)
        self.progress_lbl.setText("0%")
        self.progress.setRange(0, 100)
        self._set_status(TR["running"])
        self._set_preview_summary(None)
        self._last_progress_ui_update = 0.0

        # thread init
        self.cancel_event = threading.Event()
        self.pause_controller = PauseController()
        self.paused = False
        self.pause_btn.setText(TR["pause"])

        options = RunOptions(
            source_path=source,
            target_path=target,
            organization_mode=self._mode_enum(),
            dedupe_mode=self._dedupe_enum(),
            execution_scope=scope,
            dry_run=self.dry_check.isChecked(),
            detect_similar_images=self.similar_check.isChecked(),
            apply_changes=apply_changes,
            filter_options=self._build_filter_options(),
            duplicate_protected_paths=set(self.protected_duplicate_paths),
        )
        self.last_run_scope = scope
        self.last_run_dedupe_mode = self._dedupe_enum()
        self.last_run_apply_changes = apply_changes
        self._log(
            f"Calisma basladi | akis={scope.value} | mode={self.mode_combo.currentText()} | "
            f"dedupe={self.dedupe_combo.currentText()} | dry_run={self.dry_check.isChecked()}"
        )

        self.worker_thread = QThread()
        self.worker = Worker(self.engine, options, self.cancel_event, self.pause_controller)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.log.connect(self._log)
        self.worker.progress.connect(self._on_progress)
        self.worker.completed.connect(self._on_complete)
        self.worker.cancelled.connect(self._on_cancelled)
        self.worker.failed.connect(self._on_failed)

        # cleanup
        self.worker.completed.connect(self.worker_thread.quit)
        self.worker.cancelled.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self._thread_finished)

        self._set_running(True)
        self.worker_thread.start()

    @Slot()
    def _thread_finished(self) -> None:
        thread = self.worker_thread
        worker = self.worker
        self._set_running(False)
        self.cancel_event = None
        self.worker_thread = None
        self.worker = None
        if worker is not None:
            worker.deleteLater()
        if thread is not None:
            thread.deleteLater()

    # ---- signals from worker ----

    @Slot(object)
    def _on_progress(self, p: OperationProgress) -> None:
        if self.cancel_event is not None and self.cancel_event.is_set():
            return
        now = time.monotonic()
        if (now - self._last_progress_ui_update) < self._progress_ui_min_interval_seconds:
            return
        self._last_progress_ui_update = now

        if p.total_files > 0:
            if self.progress.maximum() == 0:
                self.progress.setRange(0, 100)
            percent = min(100, int((p.processed_files / p.total_files) * 100))
            self.progress.setValue(percent)
            self.progress_lbl.setText(f"{percent}%")
        else:
            # Unknown total (e.g., scanning): show indeterminate bar to avoid freeze perception.
            if self.progress.maximum() != 0:
                self.progress.setRange(0, 0)
            self.progress_lbl.setText(str(p.processed_files))
        if p.message and not self.paused:
            self._set_status(p.message)

    @Slot(object)
    def _on_complete(self, result: RunResult) -> None:
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.progress_lbl.setText("100%")
        self.last_result = result
        s = result.summary
        self.preview_duplicate_groups = result.duplicate_groups
        self.protected_duplicate_paths = {
            str(group.files[0].full_path).lower() for group in result.duplicate_groups if group.files
        }

        self._set_metrics_from_summary(s, similar_count=len(result.similar_image_groups))
        quarantine_est = s.duplicates_quarantined
        organize_est = s.files_copied + s.files_moved
        if not self.last_run_apply_changes:
            if self.last_run_scope.includes_dedupe and self.last_run_dedupe_mode is not DedupeMode.OFF:
                quarantine_est = s.duplicate_files_found
            if self.last_run_scope.includes_grouping:
                organize_est = max(0, s.total_files_scanned - quarantine_est)
            else:
                organize_est = 0
        self.preview_quarantine_estimate = quarantine_est
        self.preview_organize_estimate = organize_est
        self._set_preview_summary(s, quarantine_est, organize_est)

        # fill dupes table (cap for performance)
        visible_limit = 600
        for group_index, group in enumerate(result.duplicate_groups[:visible_limit]):
            self._add_dupe_row(group_index)
        if len(result.duplicate_groups) > visible_limit:
            self._log(
                f"Not: {len(result.duplicate_groups) - visible_limit} kopya grup performans icin tabloda gosterilmedi."
            )

        for err in s.errors:
            self._log(f"ERROR: {err}")

        self._set_status(TR["done"])
        if not self.last_run_apply_changes:
            self._show_summary_dialog(
                title=TR["preview_summary"],
                intro_text=TR["summary_preview_done"],
                summary=s,
                quarantine_count=self.preview_quarantine_estimate,
                organize_count=self.preview_organize_estimate,
                include_quarantine=True,
            )
        else:
            self._show_summary_dialog(
                title=TR["summary_dialog_title"],
                intro_text=TR["summary_apply_done"],
                summary=s,
                quarantine_count=s.duplicates_quarantined,
                organize_count=s.files_copied + s.files_moved,
                include_quarantine=True,
            )

    @Slot()
    def _on_cancelled(self) -> None:
        self.progress.setRange(0, 100)
        self._set_status(TR["cancelled"])
        self._log("Islem iptal edildi. Tamamlanmayan adimlar uygulanmadi.")

    @Slot(str)
    def _on_failed(self, msg: str) -> None:
        self.progress.setRange(0, 100)
        self._set_status(TR["err"])
        self._log("ERROR: " + msg)
        self.app_logger.error(msg, extra={"transaction_id": ""})
        friendly = self._friendly_error_message(msg)
        QMessageBox.critical(self, TR["err"], f"{friendly}\n{TR['error_details_hint']}")

    # ---- helpers ----

    def _scope_enum(self) -> ExecutionScope:
        index = self.workflow_tabs.currentIndex()
        if index < 0 or index >= len(WORKFLOW_ITEMS):
            return ExecutionScope.GROUP_AND_DEDUPE
        return WORKFLOW_ITEMS[index][1]

    def _mode_enum(self) -> OrganizationMode:
        return dict(MODE_ITEMS)[self.mode_combo.currentText()]

    def _dedupe_enum(self) -> DedupeMode:
        return dict(DEDUPE_ITEMS)[self.dedupe_combo.currentText()]

    def _build_filter_options(self) -> ScanFilterOptions:
        d = self.filters_draft

        def parse_ext(raw: str) -> list[str]:
            parts = [x.strip() for x in raw.replace(";", ",").split(",")]
            return [x for x in parts if x]

        def parse_mb(raw: str) -> int | None:
            t = raw.strip()
            if not t:
                return None
            try:
                return int(float(t) * 1024 * 1024)
            except ValueError:
                return None

        def parse_date(raw: str) -> datetime | None:
            t = raw.strip()
            if not t:
                return None
            try:
                return datetime.fromisoformat(t).astimezone()
            except ValueError:
                return None

        return ScanFilterOptions(
            include_extensions=parse_ext(d.include_ext),
            exclude_extensions=parse_ext(d.exclude_ext),
            min_size_bytes=parse_mb(d.min_mb),
            max_size_bytes=parse_mb(d.max_mb),
            from_utc=parse_date(d.from_date),
            to_utc=parse_date(d.to_date),
            exclude_hidden=True,
            exclude_system=True,
        )

    def _set_running(self, running: bool) -> None:
        self.preview_btn.setEnabled(not running)
        self.apply_btn.setEnabled(not running)
        self.filters_btn.setEnabled(not running)
        self.profile_combo.setEnabled(not running and bool(self.profiles))
        self.profile_apply_btn.setEnabled(not running and bool(self.profiles))
        self.pause_btn.setEnabled(running)
        self.cancel_btn.setEnabled(running)
        self.workflow_tabs.setEnabled(not running)
        self.mode_combo.setEnabled(not running)
        self.dedupe_combo.setEnabled(not running)
        self.dry_check.setEnabled(not running)
        self.dupe_detail_btn.setEnabled(not running)
        self.open_quarantine_btn.setEnabled(not running)

        if not running:
            self.paused = False
            self.pause_btn.setText(TR["pause"])
        self._on_workflow_changed(self.workflow_tabs.currentIndex())

    def _is_running(self) -> bool:
        return self.worker_thread is not None and self.worker_thread.isRunning()

    def _set_status(self, text: str) -> None:
        self.status_lbl.setText(text)

    @staticmethod
    def _friendly_error_message(message: str) -> str:
        lowered = message.lower()
        if "source folder not found" in lowered or "kaynak klasör bulunamadı" in lowered:
            return "Kaynak klasor bulunamadi. Disk baglantisini ve klasor yolunu kontrol edin."
        if "source and target cannot be the same" in lowered or "kaynak ve hedef klasör aynı olamaz" in lowered:
            return "Kaynak ve hedef klasor ayni olamaz. Farkli bir hedef secin."
        if (
            "target folder cannot be inside source" in lowered
            or "hedef klasör kaynak klasörün içinde olamaz" in lowered
        ):
            return "Hedef klasor, kaynak klasorun icinde olamaz. Disarida bir hedef secin."
        if "permission" in lowered or "izin" in lowered:
            return "Klasore erisim izni yetersiz. Farkli klasor secin veya izinleri kontrol edin."
        return message

    def _log(self, msg: str) -> None:
        self.log_text.append(msg)
        self.app_logger.info(msg, extra={"transaction_id": ""})

    def _clear_logs(self) -> None:
        self.log_text.clear()

    def _clear_dupes_table(self) -> None:
        self.dupes_table.setRowCount(0)

    def _open_duplicate_location_from_table(self, row: int, _column: int) -> None:
        first = self.dupes_table.item(row, 0)
        if first is None:
            return
        open_path = first.data(int(Qt.ItemDataRole.UserRole) + 1)
        if isinstance(open_path, str) and open_path.strip():
            self._open_path_in_file_manager(Path(open_path))
            return
        group_index = first.data(Qt.ItemDataRole.UserRole)
        if not isinstance(group_index, int):
            return
        if group_index < 0 or group_index >= len(self.preview_duplicate_groups):
            return
        group = self.preview_duplicate_groups[group_index]
        if not group.files:
            return
        self._open_path_in_file_manager(group.files[0].full_path)

    def _open_duplicate_group_dialog(self, row: int, _column: int) -> None:
        first = self.dupes_table.item(row, 0)
        if first is None:
            return
        group_index = first.data(Qt.ItemDataRole.UserRole)
        if not isinstance(group_index, int):
            return
        if group_index < 0 or group_index >= len(self.preview_duplicate_groups):
            return

        group = self.preview_duplicate_groups[group_index]
        dlg = DuplicateGroupDialog(self, group, self.protected_duplicate_paths)
        if dlg.exec() != QDialog.DialogCode.Accepted or dlg.selected_paths is None:
            return

        group_paths = {str(item.full_path).lower() for item in group.files}
        self.protected_duplicate_paths -= group_paths
        self.protected_duplicate_paths |= dlg.selected_paths
        self._refresh_dupe_row(row, group_index)
        self._log(f"Kopya grubu secimi guncellendi: {group.sha256_hash[:12]}..")

    def _refresh_dupe_row(self, row: int, group_index: int) -> None:
        if group_index < 0 or group_index >= len(self.preview_duplicate_groups):
            return
        group = self.preview_duplicate_groups[group_index]
        protected_files = [
            item for item in group.files if str(item.full_path).lower() in self.protected_duplicate_paths
        ]
        keep_count = len(protected_files)
        if keep_count <= 0 and group.files:
            keep_count = 1
            protected_files = [group.files[0]]
        remove_count = max(0, len(group.files) - keep_count)
        selected_file = protected_files[0] if protected_files else (group.files[0] if group.files else None)
        keep_text = (
            str(selected_file.full_path)
            if keep_count <= 1 and selected_file is not None
            else f"{keep_count} dosya korunuyor"
        )
        values = [group.sha256_hash[:12] + "..", f"x{remove_count}", format_size(group.size_bytes), keep_text]
        for c, val in enumerate(values):
            item = self.dupes_table.item(row, c) or QTableWidgetItem()
            item.setText(val)
            if c == 0:
                item.setData(Qt.ItemDataRole.UserRole, group_index)
                item.setData(
                    int(Qt.ItemDataRole.UserRole) + 1, str(selected_file.full_path) if selected_file is not None else ""
                )
            if c in (0, 1, 2):
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter
                    | (Qt.AlignmentFlag.AlignRight if c == 2 else Qt.AlignmentFlag.AlignLeft)
                )
            self.dupes_table.setItem(row, c, item)

    def _add_dupe_row(self, group_index: int) -> None:
        if group_index < 0 or group_index >= len(self.preview_duplicate_groups):
            return
        r = self.dupes_table.rowCount()
        self.dupes_table.insertRow(r)
        self._refresh_dupe_row(r, group_index)

    def _set_metrics_from_summary(self, summary: OperationSummary, similar_count: int) -> None:
        self.m_total.setText(str(summary.total_files_scanned))
        self.m_size.setText(format_size(summary.total_bytes_scanned))
        self.m_dupes.setText(str(summary.duplicate_files_found))
        self.m_reclaim.setText(format_size(summary.duplicate_bytes_reclaimable))
        self.m_errors.setText(str(len(summary.errors)))
        self.m_similar.setText(str(similar_count))

    def _set_preview_summary(
        self,
        summary: OperationSummary | None,
        quarantine_count: int = 0,
        organize_count: int = 0,
    ) -> None:
        if summary is None:
            self.p_total.setText("0")
            self.p_dupes.setText("0")
            self.p_dupe_groups.setText("0")
            self.p_reclaim.setText("0 B")
            self.p_quarantine.setText("0")
            self.p_organize.setText("0")
            self.p_errors.setText("0")
            self.p_skipped.setText("0")
            return
        self.p_total.setText(str(summary.total_files_scanned))
        self.p_dupes.setText(str(summary.duplicate_files_found))
        self.p_dupe_groups.setText(str(summary.duplicate_group_count))
        self.p_reclaim.setText(format_size(summary.duplicate_bytes_reclaimable))
        self.p_quarantine.setText(str(quarantine_count))
        self.p_organize.setText(str(organize_count))
        self.p_errors.setText(str(len(summary.errors)))
        self.p_skipped.setText(str(len(summary.skipped_files)))

    def _summary_text(
        self,
        summary: OperationSummary,
        *,
        quarantine_count: int | None,
        organize_count: int | None,
    ) -> str:
        lines = []
        lines.append(f"{TR['sum_total']}: {summary.total_files_scanned}")
        lines.append(f"{TR['sum_dupe_groups']}: {summary.duplicate_group_count}")
        lines.append(f"{TR['sum_dupes']}: {summary.duplicate_files_found}")
        lines.append(f"{TR['sum_reclaim']}: {format_size(summary.duplicate_bytes_reclaimable)}")
        if quarantine_count is not None:
            lines.append(f"{TR['sum_quarantine']}: {quarantine_count}")
        if organize_count is not None:
            lines.append(f"{TR['sum_organize']}: {organize_count}")
        lines.append(f"{TR['sum_errors']}: {len(summary.errors)}")
        lines.append(f"{TR['sum_skipped']}: {len(summary.skipped_files)}")
        return "\n".join(lines)

    def _show_summary_dialog(
        self,
        *,
        title: str,
        intro_text: str,
        summary: OperationSummary,
        quarantine_count: int | None,
        organize_count: int | None,
        include_quarantine: bool,
    ) -> None:
        text = self._summary_text(
            summary,
            quarantine_count=(quarantine_count if include_quarantine else None),
            organize_count=organize_count,
        )
        QMessageBox.information(
            self,
            title or TR["summary_dialog_title"],
            f"{intro_text}\n\n{text}",
        )

    def _confirm_apply(self, scope: ExecutionScope) -> bool:
        lines = [TR["confirm_apply_text"], ""]
        lines.append(f"- Is akis: {scope.value}")
        lines.append(f"- Test modu: {'Acik' if self.dry_check.isChecked() else 'Kapali'}")
        lines.append(f"- Kopya modu: {self.dedupe_combo.currentText()}")
        lines.append(f"- Gruplama modu: {self.mode_combo.currentText()}")
        if self.last_result is not None:
            s = self.last_result.summary
            lines.append("")
            lines.append("Son onizleme ozeti:")
            lines.append(
                self._summary_text(
                    s,
                    quarantine_count=self.preview_quarantine_estimate,
                    organize_count=self.preview_organize_estimate,
                )
            )
        else:
            lines.append("")
            lines.append("Onizleme sonucu bulunamadi.")

        ok = QMessageBox.question(
            self,
            TR["confirm_apply_title"],
            "\n".join(lines),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        return bool(ok == QMessageBox.StandardButton.Yes)

    def _open_path_in_file_manager(self, path: Path) -> None:
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", "-R", str(path)], check=False)
            elif os.name == "nt":
                subprocess.run(["explorer", f"/select,{path}"], check=False)
            else:
                target = path if path.is_dir() else path.parent
                subprocess.run(["xdg-open", str(target)], check=False)
        except (OSError, subprocess.SubprocessError):
            QMessageBox.warning(self, TR["err"], TR["open_file_location_failed"])

    def closeEvent(self, event: QCloseEvent) -> None:
        """Intercept close to cancel active run safely before exit."""
        if not self._is_running():
            super().closeEvent(event)
            return

        self._set_status("Kapatiliyor...")
        self._cancel_run()

        if self.worker_thread is not None:
            self.worker_thread.wait(3000)
            if self.worker_thread.isRunning():
                QMessageBox.warning(
                    self,
                    TR["err"],
                    "Islem hala devam ediyor. Lutfen once Iptal ile durdurun.",
                )
                event.ignore()
                return

        super().closeEvent(event)


def launch_gui() -> None:
    """Create Qt application, apply theme and start event loop.

    Example:
        >>> # launch_gui()
        >>> # Starts the desktop app event loop.
    """
    config_service = AppConfigService()
    app_config = config_service.load_resolved_config()
    if app_config.console_log_level and not os.environ.get("ARCHIFLOW_CONSOLE_LOG_LEVEL"):
        os.environ["ARCHIFLOW_CONSOLE_LOG_LEVEL"] = app_config.console_log_level
    log_path = configure_logging(log_dir=app_config.log_dir, level=app_config.log_level or None)
    app_logger = get_logger("gui")
    app = QApplication(sys.argv)
    app_logger.info(f"GUI started. log_file={log_path}", extra={"transaction_id": ""})

    # Better fonts on macOS/Win
    app.setFont(QFont("SF Pro Text", 11))

    apply_gui_theme(app, qdarktheme)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch_gui()
