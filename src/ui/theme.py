"""
Dark Neo Glass Theme for VideoWall
===================================
Cyberpunk dark dashboard with floating transparent panels, layered depth shadows,
teal accent lighting, and ambient gradient meshes.

All colors and styles centralized here. NO hardcoded colors elsewhere.
"""

# ── Color Palette ──────────────────────────────────────────────

# Backgrounds
BG_VOID = "#0a0b0e"
BG_SURFACE = "#111214"
BG_CARD = "#141518"
BG_CARD_HOVER = "#1a1b1f"
BG_SIDEBAR = "#0d0e10"
BG_TERTIARY = "#18191c"
BG_INPUT = "#18191c"
BG_TOOLTIP = "#222328"

# Typography Colors
TEXT_PRIMARY = "#e8e8ec"
TEXT_SECONDARY = "#9a9aa6"
TEXT_MUTED = "#5c5c6a"
TEXT_DIM = "#44444e"
TEXT_HEADING = "#f4f4f7"
TEXT_ACCENT = "#14b8a6"
TEXT_INVERSE = "#0a0b0e"

# Accent Colors
ACCENT_TEAL = "#14b8a6"
ACCENT_TEAL_DIM = "rgba(20, 184, 166, 0.12)"
ACCENT_TEAL_GLOW = "rgba(20, 184, 166, 0.25)"
ACCENT_TEAL_SELECTION = "{ACCENT_TEAL_SELECTION}"
ACCENT_TEAL_HOVER = "#0d9488"
ACCENT_BLUE = "#06b6d4"
ACCENT_BLUE_DIM = "rgba(6, 182, 212, 0.15)"
ACCENT_PURPLE = "#8b5cf6"
ACCENT_PURPLE_DIM = "rgba(139, 92, 246, 0.15)"

# Status Colors
SUCCESS = "#10b981"
WARNING = "#f59e0b"
ERROR = "#ef4444"
STATUS_OFFLINE = "#52525b"
STATUS_ONLINE = "#10b981"

# Borders
BORDER_SUBTLE = "#1e1e24"
BORDER_LIGHT = "#2a2a30"
BORDER_INPUT = "#2a2a30"
BORDER_FOCUS = "#14b8a6"

# Glass Effects
GLASS_BG = "rgba(255, 255, 255, 3)"  # 0.03 alpha -> ~8/255
GLASS_BORDER = "rgba(255, 255, 255, 13)"  # 0.05 alpha -> ~13/255
GLASS_HIGHLIGHT = "rgba(255, 255, 255, 15)"  # 0.06 alpha

# Border Radius
RADIUS_SM = "6px"
RADIUS_MD = "10px"
RADIUS_CARD = "14px"
RADIUS_BUTTON = "10px"
RADIUS_INPUT = "10px"
RADIUS_LG = "14px"
RADIUS_XL = "20px"

# Scrollbar
SCROLLBAR_THUMB = "#2a2a32"
SCROLLBAR_THUMB_HOVER = "#3a3a44"


# ── Global Application Stylesheet ──────────────────────────────


def get_app_stylesheet():
    """
    Returns the complete Dark Neo Glass QSS stylesheet for QApplication.
    Apply via: app.setStyleSheet(get_app_stylesheet())
    """
    return f"""
    /* ═══════════════════════════════════════════════════
       DARK NEO GLASS THEME - VideoWall
       ═══════════════════════════════════════════════════ */

    /* ── Global Defaults ── */
    * {{
        font-family: 'Inter', 'SF Pro Display', 'Segoe UI', 'Roboto', sans-serif;
        color: {TEXT_PRIMARY};
        outline: none;
    }}

    /* ── QMainWindow (Video Wall) ── */
    QMainWindow {{
        background-color: {BG_VOID};
        border: none;
    }}

    /* ── QWidget Defaults ── */
    QWidget {{
        background-color: transparent;
        color: {TEXT_PRIMARY};
    }}

    /* ── QDialog (Configuration Dialog) ── */
    QDialog {{
        background-color: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:1,
            stop:0 {BG_VOID},
            stop:1 #0f1012
        );
        border: 1px solid {BORDER_SUBTLE};
        border-radius: {RADIUS_XL};
    }}

    /* ── Labels ── */
    QLabel {{
        color: {TEXT_PRIMARY};
        background: transparent;
        padding: 2px;
    }}

    /* ── Buttons ── */
    QPushButton {{
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:1,
            stop:0 {ACCENT_TEAL},
            stop:1 {ACCENT_TEAL_HOVER}
        );
        color: {TEXT_INVERSE};
        border: none;
        padding: 12px 24px;
        border-radius: {RADIUS_BUTTON};
        font-weight: 600;
        font-size: 14px;
        min-height: 20px;
    }}

    QPushButton:hover {{
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:1,
            stop:0 {ACCENT_TEAL_HOVER},
            stop:1 {ACCENT_TEAL}
        );
    }}

    QPushButton:pressed {{
        background: {ACCENT_TEAL_HOVER};
    }}

    QPushButton:disabled {{
        background: {BG_TERTIARY};
        color: {TEXT_DIM};
        border: 1px solid {BORDER_SUBTLE};
    }}

    /* ── Secondary/Ghost Buttons ── */
    QPushButton[secondary="true"],
    QPushButton#select_folder_button {{
        background: rgba(255, 255, 255, 15);
        color: {TEXT_SECONDARY};
        border: 1px solid {BORDER_LIGHT};
        font-weight: 500;
    }}

    QPushButton[secondary="true"]:hover,
    QPushButton#select_folder_button:hover {{
        background: {BG_CARD_HOVER};
        color: {TEXT_PRIMARY};
        border-color: {BORDER_LIGHT};
    }}

    /* ── Checkbox ── */
    QCheckBox {{
        color: {TEXT_PRIMARY};
        spacing: 10px;
        font-size: 13px;
        padding: 6px 4px;
    }}

    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid {BORDER_LIGHT};
        background: {BG_INPUT};
    }}

    QCheckBox::indicator:checked {{
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:1,
            stop:0 {ACCENT_TEAL},
            stop:1 {ACCENT_BLUE}
        );
        border-color: {ACCENT_TEAL};
        image: none;
    }}

    QCheckBox::indicator:hover {{
        border-color: {ACCENT_TEAL};
    }}

    /* ── Input Fields ── */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background: {BG_INPUT};
        border: 1px solid {BORDER_INPUT};
        border-radius: {RADIUS_INPUT};
        padding: 10px 14px;
        color: {TEXT_PRIMARY};
        font-size: 14px;
        selection-background-color: {ACCENT_TEAL_SELECTION};
    }}

    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {BORDER_FOCUS};
    }}

    /* ── Combo Box / Select ── */
    QComboBox {{
        background: {BG_INPUT};
        border: 1px solid {BORDER_INPUT};
        border-radius: {RADIUS_INPUT};
        padding: 10px 14px;
        color: {TEXT_PRIMARY};
        font-size: 14px;
        min-height: 20px;
    }}

    QComboBox:hover {{
        border-color: {BORDER_LIGHT};
    }}

    QComboBox:focus {{
        border-color: {BORDER_FOCUS};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}

    QComboBox QAbstractItemView {{
        background: {BG_CARD};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: {RADIUS_SM};
        color: {TEXT_PRIMARY};
        selection-background-color: {ACCENT_TEAL_SELECTION};
        selection-color: {ACCENT_TEAL};
        padding: 4px;
    }}

    /* ── Scrollbar ── */
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {SCROLLBAR_THUMB};
        border-radius: 3px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {SCROLLBAR_THUMB_HOVER};
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: transparent;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 6px;
        margin: 0;
    }}

    QScrollBar::handle:horizontal {{
        background: {SCROLLBAR_THUMB};
        border-radius: 3px;
        min-width: 30px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background: {SCROLLBAR_THUMB_HOVER};
    }}

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {{
        background: transparent;
    }}

    /* ── Progress Bar ── */
    QProgressBar {{
        background-color: {BORDER_SUBTLE};
        border: none;
        border-radius: 4px;
        text-align: center;
        color: {TEXT_MUTED};
        font-size: 11px;
        min-height: 8px;
        max-height: 8px;
    }}

    QProgressBar::chunk {{
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 {ACCENT_TEAL},
            stop:1 {ACCENT_BLUE}
        );
        border-radius: 4px;
    }}

    /* ── Tooltip ── */
    QToolTip {{
        background: {BG_TOOLTIP};
        color: {TEXT_PRIMARY};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: {RADIUS_SM};
        padding: 8px 12px;
        font-size: 12px;
    }}

    /* ── Menu Bar ── */
    QMenuBar {{
        background: {BG_VOID};
        color: {TEXT_SECONDARY};
        border-bottom: 1px solid {BORDER_SUBTLE};
        padding: 4px 8px;
    }}

    QMenuBar::item {{
        padding: 6px 12px;
        border-radius: {RADIUS_SM};
        color: {TEXT_SECONDARY};
    }}

    QMenuBar::item:selected {{
        background: {ACCENT_TEAL_SELECTION};
        color: {ACCENT_TEAL};
    }}

    QMenu {{
        background: {BG_CARD};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: {RADIUS_MD};
        padding: 6px;
    }}

    QMenu::item {{
        padding: 8px 24px 8px 12px;
        border-radius: {RADIUS_SM};
        color: {TEXT_PRIMARY};
    }}

    QMenu::item:selected {{
        background: {ACCENT_TEAL_SELECTION};
        color: {ACCENT_TEAL};
    }}

    QMenu::separator {{
        height: 1px;
        background: {BORDER_SUBTLE};
        margin: 4px 8px;
    }}

    /* ── Tab Widget ── */
    QTabWidget::pane {{
        background: {BG_SURFACE};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: {RADIUS_MD};
    }}

    QTabBar::tab {{
        background: transparent;
        color: {TEXT_SECONDARY};
        padding: 10px 20px;
        border-bottom: 2px solid transparent;
        font-size: 13px;
    }}

    QTabBar::tab:hover {{
        color: {TEXT_PRIMARY};
        background: rgba(255, 255, 255, 8);
    }}

    QTabBar::tab:selected {{
        color: {ACCENT_TEAL};
        border-bottom-color: {ACCENT_TEAL};
    }}

    /* ── Group Box ── */
    QGroupBox {{
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:0.8, y2:1,
            stop:0 {BG_CARD},
            stop:1 {BG_TERTIARY}
        );
        border: 1px solid {BORDER_SUBTLE};
        border-radius: {RADIUS_CARD};
        margin-top: 12px;
        padding: 20px 16px 16px 16px;
        font-weight: 600;
    }}

    QGroupBox::title {{
        color: {TEXT_HEADING};
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 8px;
    }}

    /* ── Spin Box ── */
    QSpinBox, QDoubleSpinBox {{
        background: {BG_INPUT};
        border: 1px solid {BORDER_INPUT};
        border-radius: {RADIUS_INPUT};
        padding: 8px 12px;
        color: {TEXT_PRIMARY};
        font-size: 14px;
    }}

    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {BORDER_FOCUS};
    }}

    /* ── Status Bar ── */
    QStatusBar {{
        background: {BG_VOID};
        color: {TEXT_MUTED};
        border-top: 1px solid {BORDER_SUBTLE};
        font-size: 12px;
    }}

    /* ── File Dialog ── */
    QFileDialog {{
        background: {BG_SURFACE};
    }}

    /* ── Message Box ── */
    QMessageBox {{
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:1,
            stop:0 {BG_CARD},
            stop:1 {BG_TERTIARY}
        );
    }}

    QMessageBox QLabel {{
        color: {TEXT_PRIMARY};
    }}
    """


# ── Component-Specific Stylesheets ────────────────────────────


def get_video_tile_stylesheet():
    """Stylesheet for video tiles in the grid."""
    return f"""
        QVideoWidget {{
            background-color: {BG_VOID};
            border: none;
        }}
    """


def get_video_tile_fade_stylesheet():
    """Stylesheet for tile animation fade effect."""
    return """
        QVideoWidget {
            background-color: rgba(10, 11, 14, 200);
            border: none;
        }
    """


def get_status_label_stylesheet(is_error=False):
    """
    Stylesheet for status overlay labels on video tiles.

    Args:
        is_error (bool): True for error styling (red tint), False for normal.
    """
    if is_error:
        return f"""
            QLabel {{
                background-color: rgba(239, 68, 68, 180);
                color: {TEXT_HEADING};
                font-size: 10pt;
                font-weight: 500;
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid rgba(239, 68, 68, 100);
            }}
        """
    else:
        return f"""
            QLabel {{
                background-color: rgba(10, 11, 14, 200);
                color: {TEXT_PRIMARY};
                font-size: 10pt;
                font-weight: 500;
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid {BORDER_SUBTLE};
            }}
        """


def get_loading_progress_stylesheet():
    """Stylesheet for the loading progress bar on video tiles."""
    return f"""
        QProgressBar {{
            background-color: rgba(10, 11, 14, 200);
            border: none;
            border-radius: 4px;
            text-align: center;
            min-height: 6px;
            max-height: 6px;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:0,
                stop:0 {ACCENT_TEAL},
                stop:1 {ACCENT_BLUE}
            );
            border-radius: 4px;
        }}
    """


def get_central_widget_stylesheet():
    """Stylesheet for the central widget of the video wall."""
    return f"""
        QWidget {{
            background-color: {BG_VOID};
        }}
    """


def get_dialog_title_stylesheet():
    """Stylesheet for dialog title labels."""
    return f"""
        QLabel {{
            color: {TEXT_HEADING};
            font-size: 18pt;
            font-weight: 700;
            padding: 12px 0;
            background: transparent;
        }}
    """


def get_dialog_section_header_stylesheet():
    """Stylesheet for section header labels in dialogs."""
    return f"""
        QLabel {{
            color: {ACCENT_TEAL};
            font-size: 13pt;
            font-weight: 600;
            padding: 8px 0 4px 0;
            background: transparent;
        }}
    """


def get_dialog_description_stylesheet():
    """Stylesheet for descriptive text in dialogs."""
    return f"""
        QLabel {{
            color: {TEXT_SECONDARY};
            font-size: 11pt;
            padding: 4px 0;
            background: transparent;
        }}
    """


def get_warning_label_stylesheet():
    """Stylesheet for warning labels."""
    return f"""
        QLabel {{
            color: {WARNING};
            font-size: 10pt;
            padding: 8px 12px;
            background: rgba(245, 158, 11, 20);
            border: 1px solid rgba(245, 158, 11, 40);
            border-radius: 6px;
        }}
    """


def get_status_info_label_stylesheet():
    """Stylesheet for status information labels in dialogs."""
    return f"""
        QLabel {{
            color: {TEXT_MUTED};
            font-size: 10pt;
            padding: 6px 0;
            background: transparent;
        }}
    """


def get_start_button_stylesheet():
    """Stylesheet for the primary 'Start Video Wall' action button."""
    return f"""
        QPushButton {{
            background: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 {ACCENT_TEAL},
                stop:1 {ACCENT_BLUE}
            );
            color: {TEXT_INVERSE};
            border: none;
            padding: 14px 32px;
            border-radius: {RADIUS_BUTTON};
            font-weight: 700;
            font-size: 15px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 {ACCENT_TEAL_HOVER},
                stop:1 {ACCENT_TEAL}
            );
        }}
        QPushButton:pressed {{
            background: {ACCENT_TEAL_HOVER};
        }}
    """


def get_folder_button_stylesheet():
    """Stylesheet for the secondary folder selection button."""
    return f"""
        QPushButton {{
            background: rgba(255, 255, 255, 15);
            color: {TEXT_SECONDARY};
            border: 1px solid {BORDER_LIGHT};
            padding: 10px 20px;
            border-radius: {RADIUS_BUTTON};
            font-weight: 500;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background: {BG_CARD_HOVER};
            color: {TEXT_PRIMARY};
            border-color: {ACCENT_TEAL};
        }}
        QPushButton:pressed {{
            background: {BG_TERTIARY};
        }}
    """


def get_titlebar_stylesheet():
    """Stylesheet for the custom frameless titlebar."""
    return f"""
        QWidget#titlebar {{
            background: transparent;
        }}
        QLabel#titlebar_label {{
            color: {TEXT_SECONDARY};
            font-size: 12px;
            font-weight: 500;
            background: transparent;
            padding: 0;
        }}
    """


def get_titlebar_button_close_stylesheet():
    """Stylesheet for the close button — neo-glass circle with ✕ symbol."""
    return f"""
        QPushButton {{
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            min-width: 24px;
            max-width: 24px;
            min-height: 24px;
            max-height: 24px;
            padding: 0;
            color: {TEXT_MUTED};
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background: {ERROR};
            border-color: {ERROR};
            color: #ffffff;
        }}
    """


def get_titlebar_button_minimize_stylesheet():
    """Stylesheet for the minimize button — neo-glass circle with ─ symbol."""
    return f"""
        QPushButton {{
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            min-width: 24px;
            max-width: 24px;
            min-height: 24px;
            max-height: 24px;
            padding: 0;
            color: {TEXT_MUTED};
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background: {ACCENT_TEAL};
            border-color: {ACCENT_TEAL};
            color: {BG_VOID};
        }}
    """


def get_titlebar_button_maximize_stylesheet():
    """Stylesheet for the maximize button — neo-glass circle with □ symbol."""
    return f"""
        QPushButton {{
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            min-width: 24px;
            max-width: 24px;
            min-height: 24px;
            max-height: 24px;
            padding: 0;
            color: {TEXT_MUTED};
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background: {ACCENT_TEAL};
            border-color: {ACCENT_TEAL};
            color: {BG_VOID};
        }}
    """


def get_glow_line_stylesheet():
    """Stylesheet for a teal glow accent line."""
    return f"""
        QFrame {{
            background: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent,
                stop:0.2 {ACCENT_TEAL},
                stop:0.8 {ACCENT_TEAL},
                stop:1 transparent
            );
            border: none;
            max-height: 2px;
            min-height: 2px;
        }}
    """


def get_glass_card_accent_stylesheet():
    """Stylesheet for glass cards with teal top-accent border."""
    return f"""
        QFrame#glass_card {{
            background: qlineargradient(
                spread:pad, x1:0, y1:0, x2:0.8, y2:1,
                stop:0 {BG_CARD},
                stop:1 {BG_TERTIARY}
            );
            border: 1px solid {BORDER_SUBTLE};
            border-top: 2px solid rgba(20, 184, 166, 0.35);
            border-radius: {RADIUS_CARD};
            padding: 0px;
        }}
    """


def get_outer_frame_stylesheet():
    """Stylesheet for the outer frameless dialog frame with float gap."""
    return f"""
        QFrame#outer_frame {{
            background: qlineargradient(
                spread:pad, x1:0, y1:0, x2:1, y2:1,
                stop:0 {BG_VOID},
                stop:1 #0f1012
            );
            border: 1px solid {BORDER_SUBTLE};
            border-radius: {RADIUS_XL};
        }}
    """


def get_titlebar_button_about_stylesheet():
    """Stylesheet for the About (?) button — neo-glass circle with teal accent."""
    return f"""
        QPushButton {{
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            min-width: 24px;
            max-width: 24px;
            min-height: 24px;
            max-height: 24px;
            padding: 0;
            color: {TEXT_MUTED};
            font-size: 12px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background: {ACCENT_TEAL};
            border-color: {ACCENT_TEAL};
            color: {BG_VOID};
        }}
    """


def get_about_dialog_stylesheet():
    """Stylesheet for the About modal content."""
    return f"""
        QLabel#about_app_name {{
            color: {TEXT_HEADING};
            font-size: 20pt;
            font-weight: 700;
            background: transparent;
            padding: 0;
        }}
        QLabel#about_version {{
            color: {ACCENT_TEAL};
            font-size: 12pt;
            font-weight: 600;
            background: transparent;
            padding: 0;
        }}
        QLabel#about_description {{
            color: {TEXT_SECONDARY};
            font-size: 11pt;
            background: transparent;
            padding: 4px 0;
        }}
        QLabel#about_author {{
            color: {TEXT_MUTED};
            font-size: 10pt;
            background: transparent;
            padding: 2px 0;
        }}
        QLabel#about_license {{
            color: {TEXT_DIM};
            font-size: 9pt;
            background: transparent;
            padding: 2px 0;
        }}
        QPushButton#about_link {{
            color: {ACCENT_TEAL};
            font-size: 10pt;
            background: transparent;
            border: none;
            padding: 2px 0;
            text-decoration: none;
        }}
        QPushButton#about_link:hover {{
            color: {TEXT_HEADING};
        }}
        QPushButton#about_close {{
            background: {ACCENT_TEAL};
            color: {TEXT_INVERSE};
            border: none;
            padding: 10px 28px;
            border-radius: {RADIUS_BUTTON};
            font-weight: 600;
            font-size: 13px;
            min-height: 20px;
        }}
        QPushButton#about_close:hover {{
            background: {ACCENT_TEAL_HOVER};
        }}
    """
