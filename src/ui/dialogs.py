"""
Dialog windows for VideoWall.
Dark Neo Glass themed configuration dialog with frameless custom titlebar.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from src.ui.theme import (
    ACCENT_TEAL,
    BORDER_SUBTLE,
    TEXT_MUTED,
    TEXT_SECONDARY,
    get_about_dialog_stylesheet,
    get_dialog_description_stylesheet,
    get_dialog_section_header_stylesheet,
    get_dialog_title_stylesheet,
    get_folder_button_stylesheet,
    get_glass_card_accent_stylesheet,
    get_glow_line_stylesheet,
    get_outer_frame_stylesheet,
    get_start_button_stylesheet,
    get_status_info_label_stylesheet,
    get_titlebar_button_about_stylesheet,
    get_titlebar_button_close_stylesheet,
    get_titlebar_button_maximize_stylesheet,
    get_titlebar_button_minimize_stylesheet,
    get_titlebar_stylesheet,
    get_warning_label_stylesheet,
)


class GlassCard(QFrame):
    """
    A card-style container with Dark Neo Glass treatment.
    Gradient background, teal top-accent border, rounded corners, drop shadow.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("glass_card")
        self.setStyleSheet(get_glass_card_accent_stylesheet())
        self._add_shadow()

    def _add_shadow(self):
        """Add layered depth shadow effect."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)


class GlowLine(QFrame):
    """Teal glow accent line — horizontal separator with radial glow."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(2)
        self.setStyleSheet(get_glow_line_stylesheet())


class SeparatorLine(QFrame):
    """Subtle separator line for visual grouping."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 transparent,
                    stop:0.2 {BORDER_SUBTLE},
                    stop:0.8 {BORDER_SUBTLE},
                    stop:1 transparent
                );
                border: none;
                margin: 4px 0;
            }}
        """)


class AboutDialog(QDialog):
    """
    About modal for VideoWall — frameless glass panel with app info.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About VideoWall")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(420, 380)
        self.setWindowModality(Qt.ApplicationModal)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(0)

        outer_frame = QFrame()
        outer_frame.setObjectName("outer_frame")
        outer_frame.setStyleSheet(get_outer_frame_stylesheet())

        frame_shadow = QGraphicsDropShadowEffect(outer_frame)
        frame_shadow.setBlurRadius(48)
        frame_shadow.setColor(QColor(0, 0, 0, 120))
        frame_shadow.setOffset(0, 12)
        outer_frame.setGraphicsEffect(frame_shadow)

        frame_layout = QVBoxLayout(outer_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # Title bar
        titlebar = CustomTitleBar(self, "About")
        frame_layout.addWidget(titlebar)

        # Content
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 16, 28, 24)
        content_layout.setSpacing(6)
        content_layout.setAlignment(Qt.AlignCenter)

        content.setStyleSheet(get_about_dialog_stylesheet())

        app_name = QLabel("VideoWall")
        app_name.setObjectName("about_app_name")
        app_name.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(app_name)

        version_label = QLabel("v1.6.4")
        version_label.setObjectName("about_version")
        version_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(version_label)

        content_layout.addSpacing(4)
        glow = GlowLine()
        content_layout.addWidget(glow)
        content_layout.addSpacing(4)

        desc = QLabel("Multi-display video wall with M3U8 streaming\nand animated layout transitions.")
        desc.setObjectName("about_description")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        content_layout.addWidget(desc)

        content_layout.addSpacing(8)

        author = QLabel("J. Michaels (sanchez314c)")
        author.setObjectName("about_author")
        author.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(author)

        license_label = QLabel("MIT License")
        license_label.setObjectName("about_license")
        license_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(license_label)

        content_layout.addSpacing(4)

        link_btn = QPushButton("github.com/sanchez314c/video-wall")
        link_btn.setObjectName("about_link")
        link_btn.setCursor(Qt.PointingHandCursor)
        link_btn.setToolTip("https://github.com/sanchez314c/video-wall")
        link_btn.clicked.connect(self._open_github)
        content_layout.addWidget(link_btn)

        content_layout.addSpacing(12)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("about_close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        content_layout.addWidget(close_btn, alignment=Qt.AlignCenter)

        frame_layout.addWidget(content)
        root_layout.addWidget(outer_frame)

        self._drag_pos = None

    def _open_github(self):
        """Open the GitHub repository in the default browser."""
        from PyQt5.QtGui import QDesktopServices
        from PyQt5.QtCore import QUrl
        QDesktopServices.openUrl(QUrl("https://github.com/sanchez314c/video-wall"))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


class CustomTitleBar(QWidget):
    """
    Custom frameless titlebar with neo-glass window controls.
    Drag to move the parent window.
    """

    def __init__(self, parent_dialog, title=""):
        super().__init__(parent_dialog)
        self.parent_dialog = parent_dialog
        self.setObjectName("titlebar")
        self.setFixedHeight(44)
        self.setStyleSheet(get_titlebar_stylesheet())
        self._drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 4)
        layout.setSpacing(8)

        # Title label (left side)
        title_label = QLabel(title)
        title_label.setObjectName("titlebar_label")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_MUTED};
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            }}
        """)
        layout.addWidget(title_label)

        layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # About button (?)
        self.btn_about = QPushButton("?")
        self.btn_about.setStyleSheet(get_titlebar_button_about_stylesheet())
        self.btn_about.setCursor(Qt.PointingHandCursor)
        self.btn_about.setToolTip("About")
        self.btn_about.clicked.connect(self._show_about)

        # Neo-glass window controls (right side, matching Electron apps)
        self.btn_minimize = QPushButton("\u2500")  # ─
        self.btn_minimize.setStyleSheet(get_titlebar_button_minimize_stylesheet())
        self.btn_minimize.setCursor(Qt.PointingHandCursor)
        self.btn_minimize.setToolTip("Minimize")
        self.btn_minimize.clicked.connect(parent_dialog.showMinimized)

        self.btn_maximize = QPushButton("\u25a1")  # □
        self.btn_maximize.setStyleSheet(get_titlebar_button_maximize_stylesheet())
        self.btn_maximize.setCursor(Qt.PointingHandCursor)
        self.btn_maximize.setToolTip("Maximize")
        self.btn_maximize.clicked.connect(self._toggle_maximize)

        self.btn_close = QPushButton("\u2715")  # ✕
        self.btn_close.setStyleSheet(get_titlebar_button_close_stylesheet())
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setToolTip("Close")
        self.btn_close.clicked.connect(parent_dialog.reject)

        layout.addWidget(self.btn_about)
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_maximize)
        layout.addWidget(self.btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.parent_dialog.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.LeftButton:
            self.parent_dialog.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def _show_about(self):
        """Open the About modal dialog."""
        about = AboutDialog(self.parent_dialog)
        about.exec_()

    def _toggle_maximize(self):
        """Toggle between maximized and normal window state."""
        if self.parent_dialog.isMaximized():
            self.parent_dialog.showNormal()
            self.btn_maximize.setText("\u25a1")  # □ restore icon
        else:
            self.parent_dialog.showMaximized()
            self.btn_maximize.setText("\u25a3")  # ▣ maximized icon


class LocalVideoDialog(QDialog):
    """
    Configuration dialog for local video settings and stream options.
    Dark Neo Glass themed with frameless window, custom titlebar,
    glass cards with teal accent borders and layered shadows.
    """

    def __init__(self, parent=None):
        """
        Initialize the configuration dialog.

        Args:
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Video Wall Configuration")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(520)

        # Drag support for the whole window
        self._drag_pos = None

        # Root layout (no margins — the outer frame provides the visual boundary)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(0)

        # Outer frame — the visible "floating panel" with rounded corners
        outer_frame = QFrame()
        outer_frame.setObjectName("outer_frame")
        outer_frame.setStyleSheet(get_outer_frame_stylesheet())

        # Add drop shadow to the outer frame for floating effect
        frame_shadow = QGraphicsDropShadowEffect(outer_frame)
        frame_shadow.setBlurRadius(48)
        frame_shadow.setColor(QColor(0, 0, 0, 120))
        frame_shadow.setOffset(0, 12)
        outer_frame.setGraphicsEffect(frame_shadow)

        frame_layout = QVBoxLayout(outer_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # ── Custom Titlebar ──
        titlebar = CustomTitleBar(self, "Video Wall Configuration")
        frame_layout.addWidget(titlebar)

        # ── Content area ──
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(28, 8, 28, 24)
        content_layout.setSpacing(16)

        # ── Title ──
        title_label = QLabel("Video Wall Configuration")
        title_label.setStyleSheet(get_dialog_title_stylesheet())
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)

        # Teal glow line under title
        glow = GlowLine()
        content_layout.addWidget(glow)

        # Subtitle
        subtitle = QLabel("Configure streams and local video playback")
        subtitle.setStyleSheet(get_dialog_description_stylesheet())
        subtitle.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(subtitle)

        content_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # ── Stream Configuration Card ──
        stream_card = GlassCard()
        stream_layout = QVBoxLayout(stream_card)
        stream_layout.setContentsMargins(20, 18, 20, 18)
        stream_layout.setSpacing(10)

        stream_header = QLabel("Stream Settings")
        stream_header.setStyleSheet(get_dialog_section_header_stylesheet())
        stream_layout.addWidget(stream_header)

        stream_desc = QLabel("Live Stream Handling:")
        stream_desc.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_SECONDARY};
                font-size: 11pt;
                background: transparent;
                padding: 2px 0;
            }}
        """)
        stream_layout.addWidget(stream_desc)

        # Skip stream testing checkbox
        self.skip_stream_testing = QCheckBox("Skip Stream Testing (Assume All Streams are Valid)")
        self.skip_stream_testing.setChecked(True)
        self.skip_stream_testing.setToolTip(
            "Enable this to skip stream validation and assume all streams are valid. "
            "Recommended for better startup."
        )
        stream_layout.addWidget(self.skip_stream_testing)

        # Record streams checkbox
        self.record_streams = QCheckBox("Record Streams to Desktop")
        self.record_streams.setChecked(False)
        self.record_streams.setToolTip(
            "Record the video wall to MP4 files saved on your Desktop. "
            "Press R during playback to start/stop recordings."
        )
        stream_layout.addWidget(self.record_streams)

        # Warning label
        warning_label = QLabel(
            "Note: When streams go offline, they'll automatically fall back to local videos."
        )
        warning_label.setStyleSheet(get_warning_label_stylesheet())
        warning_label.setWordWrap(True)
        stream_layout.addWidget(warning_label)

        content_layout.addWidget(stream_card)

        # ── Local Video Configuration Card ──
        local_card = GlassCard()
        local_layout = QVBoxLayout(local_card)
        local_layout.setContentsMargins(20, 18, 20, 18)
        local_layout.setSpacing(10)

        local_header = QLabel("Local Video Settings")
        local_header.setStyleSheet(get_dialog_section_header_stylesheet())
        local_layout.addWidget(local_header)

        desc_label = QLabel(
            "Would you like to include local videos in the playback? "
            "Local videos will be used as fallbacks when streams are offline."
        )
        desc_label.setStyleSheet(get_dialog_description_stylesheet())
        desc_label.setWordWrap(True)
        local_layout.addWidget(desc_label)

        # Checkbox for enabling local videos
        self.enable_local_videos = QCheckBox("Enable Local Video Fallback")
        self.enable_local_videos.setChecked(True)
        local_layout.addWidget(self.enable_local_videos)

        # Button to select folder
        self.select_folder_button = QPushButton("Select Video Folder")
        self.select_folder_button.setStyleSheet(get_folder_button_stylesheet())
        self.select_folder_button.setCursor(Qt.PointingHandCursor)
        self.select_folder_button.clicked.connect(self.select_folder)
        local_layout.addWidget(self.select_folder_button)

        # Status label
        self.status_label = QLabel("No folder selected")
        self.status_label.setStyleSheet(get_status_info_label_stylesheet())
        local_layout.addWidget(self.status_label)

        content_layout.addWidget(local_card)

        # ── Spacer ──
        content_layout.addSpacerItem(QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ── Separator ──
        content_layout.addWidget(SeparatorLine())

        # ── Start Button ──
        self.continue_button = QPushButton("Start Video Wall")
        self.continue_button.setStyleSheet(get_start_button_stylesheet())
        self.continue_button.setCursor(Qt.PointingHandCursor)
        self.continue_button.clicked.connect(self.accept)
        content_layout.addWidget(self.continue_button)

        frame_layout.addWidget(content_widget)
        root_layout.addWidget(outer_frame)

        self.folder_path = None

    def select_folder(self):
        """
        Open a file dialog to select a folder with video files.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with Video Files")
        if folder:
            self.folder_path = folder
            self.status_label.setText(f"Selected: {folder}")
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    color: {ACCENT_TEAL};
                    font-size: 10pt;
                    padding: 6px 0;
                    background: transparent;
                }}
            """)

    def get_results(self):
        """
        Get the configuration results from the dialog.

        Returns:
            dict: Configuration settings
        """
        return {
            "use_local_videos": self.enable_local_videos.isChecked(),
            "folder_path": self.folder_path,
            "skip_stream_testing": self.skip_stream_testing.isChecked(),
            "record_streams": self.record_streams.isChecked(),
        }
