"""GUI theme helpers."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QApplication

FALLBACK_STYLESHEET = """
QWidget { background: #f5f7fa; color: #0f172a; font-size: 13px; }
QMainWindow { background: #f5f7fa; }
QLabel { color: #1f2937; }
QLabel[role="heroTitle"] { font-size: 34px; font-weight: 800; color: #0b1220; letter-spacing: 0.2px; }
QLabel[role="heroSubtitle"] { font-size: 15px; color: #475569; }
QLabel[role="viewTitle"] { font-size: 27px; font-weight: 700; color: #0f172a; }
QLabel[role="viewSubtitle"] { font-size: 14px; color: #64748b; }
QLabel#fieldLabel { color: #475569; font-size: 12px; font-weight: 600; }
QFrame#heroCard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    min-width: 760px;
    max-width: 860px;
}
QLabel#heroBadge {
    background: #f8fafc;
    border: 1px solid #dbe3ee;
    color: #475569;
    border-radius: 999px;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 600;
}
QGroupBox {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 8px;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #64748b; font-weight: 600; }
QLineEdit, QComboBox, QSpinBox, QDateEdit {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 9px 12px;
    selection-background-color: #bfdbfe;
}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDateEdit:hover {
    border: 1px solid #94a3b8;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {
    border: 1px solid #2563eb;
    background: #ffffff;
}
QLineEdit::placeholder {
    color: #94a3b8;
}
QPushButton {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 10px;
    padding: 10px 14px;
    font-weight: 600;
    color: #1f2937;
}
QPushButton:hover { background: #f1f5f9; border-color: #94a3b8; }
QPushButton:pressed { background: #e2e8f0; }
QPushButton:disabled { color: #9ca3af; border-color: #e5e7eb; background: #f9fafb; }
QPushButton#primaryBtn {
    background: #2563eb;
    color: #ffffff;
    border: 1px solid #1d4ed8;
    padding: 11px 16px;
    font-weight: 700;
}
QPushButton#primaryBtn:hover { background: #1d4ed8; border-color: #1e40af; }
QPushButton#primaryBtn:pressed { background: #1e40af; border-color: #1e3a8a; }
QPushButton#primaryBtn:disabled { background: #93c5fd; border-color: #93c5fd; color: #eff6ff; }
QPushButton#secondaryBtn {
    background: #ffffff;
    color: #1f2937;
    border: 1px solid #cbd5e1;
}
QPushButton#secondaryBtn:hover { background: #f8fafc; border-color: #94a3b8; }
QPushButton#secondaryBtn:pressed { background: #eef2f7; }
QPushButton#tertiaryBtn {
    background: transparent;
    color: #334155;
    border: 1px solid transparent;
    padding: 6px 8px;
}
QPushButton#tertiaryBtn:hover { background: #eef2ff; color: #1d4ed8; }
QPushButton#tertiaryBtn:pressed { background: #dbeafe; color: #1e3a8a; }
QPushButton#dangerBtn { background: #fff5f5; color: #b91c1c; border: 1px solid #fecaca; }
QPushButton#dangerBtn:hover { background: #fee2e2; border-color: #fca5a5; }
QPushButton#dangerBtn:pressed { background: #fecaca; }
QCheckBox {
    spacing: 8px;
    color: #1f2937;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #94a3b8;
    border-radius: 4px;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background: #2563eb;
    border-color: #1d4ed8;
}

QProgressBar {
    background: #eef2f7;
    border: 1px solid #dbe3ee;
    border-radius: 10px;
    text-align: center;
    height: 20px;
    color: #334155;
    font-weight: 600;
}
QProgressBar::chunk {
    background: #2563eb;
    border-radius: 10px;
}

QTabWidget::pane { border: 1px solid #dfe6ef; border-radius: 12px; background: #ffffff; top: -1px; }
QTabBar::tab {
    background: #f1f5f9;
    border: 1px solid #dfe6ef;
    border-bottom: none;
    padding: 10px 16px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    color: #475569;
    margin-right: 4px;
    font-weight: 600;
}
QTabBar::tab:selected { background: #ffffff; color: #0f172a; }
QTabBar::tab:hover { color: #1e3a8a; }

QHeaderView::section {
    background: #f9fafb;
    border: 1px solid #e2e8f0;
    padding: 8px 10px;
    color: #334155;
    font-weight: 600;
}
QTableWidget {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    gridline-color: #f1f5f9;
    selection-background-color: #dbeafe;
    selection-color: #111827;
    alternate-background-color: #fbfdff;
}
QTextEdit {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 10px;
}
QFrame#statCard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}
QLabel#statTitle { color: #64748b; font-size: 12px; font-weight: 600; }
QLabel#statValue { color: #0f172a; font-size: 24px; font-weight: 800; }
QLabel#infoBanner {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    color: #475569;
    padding: 10px 12px;
}
QLabel#emptyState {
    color: #94a3b8;
    font-size: 13px;
    border: 1px dashed #cbd5e1;
    border-radius: 10px;
    padding: 12px;
    background: #f8fafc;
}
QLabel#dialogTitle { font-weight: 700; color: #0f172a; }
QLabel#dialogHint { color: #64748b; }
"""

BRAND_OVERRIDES = """
QPushButton#primaryBtn { background: #2563eb; color: #ffffff; border: 1px solid #1d4ed8; font-weight: 700; }
QPushButton#primaryBtn:hover { background: #1d4ed8; }
QPushButton#primaryBtn:pressed { background: #1e40af; }
QPushButton#secondaryBtn { background: #ffffff; border: 1px solid #cbd5e1; color: #1f2937; }
QPushButton#secondaryBtn:hover { background: #f8fafc; border-color: #94a3b8; }
QPushButton#tertiaryBtn { background: transparent; color: #334155; border: 1px solid transparent; }
QPushButton#tertiaryBtn:hover { background: #eef2ff; color: #1d4ed8; }
QPushButton#dangerBtn { background: #fff5f5; color: #b91c1c; border: 1px solid #fecaca; }
QPushButton#dangerBtn:hover { background: #fee2e2; border-color: #fca5a5; }
QLabel#fieldLabel { color: #475569; font-size: 12px; font-weight: 600; }
QFrame#heroCard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    min-width: 760px;
    max-width: 860px;
}
QLabel#heroBadge {
    background: #f8fafc;
    border: 1px solid #dbe3ee;
    color: #475569;
    border-radius: 999px;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 600;
}
QFrame#statCard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}
QLabel#statTitle { color: #64748b; font-size: 12px; font-weight: 600; }
QLabel#statValue { color: #0f172a; font-size: 24px; font-weight: 800; }
QLabel#infoBanner {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    color: #475569;
    padding: 10px 12px;
}
QLabel#emptyState {
    color: #94a3b8;
    font-size: 13px;
    border: 1px dashed #cbd5e1;
    border-radius: 10px;
    padding: 12px;
    background: #f8fafc;
}
QLabel[role="heroTitle"] { font-size: 34px; font-weight: 800; color: #0b1220; }
QLabel[role="heroSubtitle"] { font-size: 15px; color: #475569; }
QLabel[role="viewTitle"] { font-size: 27px; font-weight: 700; color: #0f172a; }
QLabel[role="viewSubtitle"] { font-size: 14px; color: #64748b; }
"""


def apply_gui_theme(app: QApplication, qdarktheme_module: Any | None) -> None:
    """Apply the best available light theme to the Qt application.

    Args:
        app: Qt application instance.
        qdarktheme_module: Imported `qdarktheme` module or ``None``.

    Returns:
        None

    Example:
        >>> # apply_gui_theme(app, qdarktheme)
        >>> # Uses qdarktheme when available, otherwise fallback stylesheet.
    """
    themed = False
    if qdarktheme_module is not None:
        for fn_name in ("setup_theme", "load_stylesheet"):
            fn = getattr(qdarktheme_module, fn_name, None)
            if callable(fn):
                try:
                    if fn_name == "setup_theme":
                        fn("light")
                    else:
                        css = fn(theme="light") if "theme" in fn.__code__.co_varnames else fn()
                        if isinstance(css, str) and css.strip():
                            app.setStyleSheet(css)
                    themed = True
                    break
                except (AttributeError, TypeError, ValueError):
                    pass

    if not themed:
        app.setStyleSheet(FALLBACK_STYLESHEET)
    else:
        app.setStyleSheet((app.styleSheet() or "") + BRAND_OVERRIDES)
