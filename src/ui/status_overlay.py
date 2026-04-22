"""
Status overlay components for video tiles.
Dark Neo Glass themed.
"""

from PyQt5.QtCore import QPropertyAnimation, QRect, Qt, QTimer
from PyQt5.QtWidgets import QLabel

from src.ui.theme import get_status_label_stylesheet


class StatusOverlay(QLabel):
    """
    Enhanced status overlay for video tiles with animation effects.
    """

    def __init__(self, parent=None):
        """
        Initialize a status overlay.

        Args:
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setWordWrap(True)

        # Set default styling from theme
        self.setStyleSheet(get_status_label_stylesheet(is_error=False))

        # Configure fade animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)  # 500ms fade

        # Hide by default
        self.hide()

    def show_message(self, text, is_error=False, duration_ms=3000):
        """
        Show a status message with optional auto-hide.

        Args:
            text (str): Message to display
            is_error (bool, optional): Whether this is an error message
            duration_ms (int, optional): Duration to show in milliseconds
        """
        # Set text
        self.setText(text)

        # Apply themed styling
        self.setStyleSheet(get_status_label_stylesheet(is_error=is_error))

        # Resize and reposition
        self.adjustSize()
        self.center_in_parent()

        # Show with fade-in effect
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.show()
        self.fade_animation.start()

        # Auto-hide if duration is specified
        if duration_ms > 0:
            QTimer.singleShot(duration_ms, self.hide_message)

    def hide_message(self):
        """
        Hide the message with a fade-out effect.
        """
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()

        # Actually hide the widget after animation completes
        self.fade_animation.finished.connect(self.hide)

    def center_in_parent(self):
        """
        Center the overlay in its parent widget.
        """
        if self.parentWidget():
            parent_size = self.parentWidget().size()
            self_size = self.size()

            x = max(0, (parent_size.width() - self_size.width()) // 2)
            y = max(0, (parent_size.height() - self_size.height()) // 2)

            self.setGeometry(QRect(x, y, self_size.width(), self_size.height()))
