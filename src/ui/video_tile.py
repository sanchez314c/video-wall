"""
Video tile widget implementation.
"""
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QLabel, QSizePolicy, QProgressBar
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPalette

class VideoTile(QVideoWidget):
    """
    Video tile widget that displays video content and status overlays.
    """
    
    def __init__(self, tile_id, parent=None):
        """
        Initialize a video tile.
        
        Args:
            tile_id (int): Unique identifier for the tile
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.tile_id = tile_id
        self.setObjectName(f"Tile_{tile_id}")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAspectRatioMode(Qt.KeepAspectRatio)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("background-color: black; border: none;")

        self.status_label = QLabel("Initializing...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("background-color: rgba(0, 0, 0, 180); color: white; font-size: 10pt; padding: 3px;")
        self.status_label.setWordWrap(True)
        self.status_label.adjustSize()
        self.status_label.show()

        # Add loading progress bar
        self.loading_progress = QProgressBar(self)
        self.loading_progress.setRange(0, 100)
        self.loading_progress.setValue(0)
        self.loading_progress.setTextVisible(False)
        self.loading_progress.setStyleSheet("""
            QProgressBar {
                background-color: rgba(0, 0, 0, 180);
                border: none;
                border-radius: 2px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: rgba(100, 150, 255, 200);
                border-radius: 2px;
            }
        """)
        self.loading_progress.hide()

        # Loading animation timer
        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(self._update_loading_animation)

    def resizeEvent(self, event):
        """
        Handles resizing of the tile, repositions the status label and progress bar.

        Args:
            event (QResizeEvent): Resize event
        """
        super().resizeEvent(event)
        self.reposition_status_label()
        self.reposition_loading_progress()

    def reposition_status_label(self):
        """Calculates and sets the geometry for the status label to center it."""
        if not self.status_label.isVisible():
            return

        try:
            text_width = self.status_label.fontMetrics().horizontalAdvance(self.status_label.text())
            label_width = min(self.width() * 0.9, text_width + 20)
            label_height = self.status_label.sizeHint().height()

            x = (self.width() - label_width) / 2
            y = (self.height() - label_height) / 2

            x = max(0, x)
            y = max(0, y)
            label_width = min(label_width, self.width())
            label_height = min(label_height, self.height())

            self.status_label.setGeometry(int(x), int(y), int(label_width), int(label_height))
        except Exception as e:
            print(f"Error in VideoTile reposition_status_label for {self.tile_id}: {e}")

    def reposition_loading_progress(self):
        """Calculates and sets the geometry for the loading progress bar."""
        if not self.loading_progress.isVisible():
            return

        try:
            progress_width = min(self.width() * 0.8, 200)
            progress_height = 8

            x = (self.width() - progress_width) / 2
            y = (self.height() - progress_height) / 2 + 30  # Position below status text

            x = max(0, x)
            y = max(0, y)
            progress_width = min(progress_width, self.width())
            progress_height = min(progress_height, self.height())

            self.loading_progress.setGeometry(int(x), int(y), int(progress_width), int(progress_height))
        except Exception as e:
            print(f"Error in VideoTile reposition_loading_progress for {self.tile_id}: {e}")

    def _update_loading_animation(self):
        """Updates the loading progress bar animation."""
        try:
            current_value = self.loading_progress.value()
            new_value = (current_value + 5) % 100
            self.loading_progress.setValue(new_value)
        except Exception as e:
            print(f"Error in VideoTile _update_loading_animation for {self.tile_id}: {e}")

    def show_loading(self, message="Loading..."):
        """
        Shows loading animation with progress bar.

        Args:
            message (str): Loading message to display
        """
        try:
            self.status_label.setText(message)
            self.status_label.show()
            self.reposition_status_label()

            self.loading_progress.show()
            self.loading_progress.setValue(0)
            self.reposition_loading_progress()

            # Start loading animation
            if not self.loading_timer.isActive():
                self.loading_timer.start(100)  # Update every 100ms
        except Exception as e:
            print(f"Error in show_loading for Tile {self.tile_id}: {e}")

    def hide_loading(self):
        """Hides the loading animation."""
        try:
            self.loading_timer.stop()
            self.loading_progress.hide()
            self.safe_hide_status()
        except Exception as e:
            print(f"Error in hide_loading for Tile {self.tile_id}: {e}")

    def show_status(self, text, is_error=False, duration_ms=3000):
        """
        Displays a status message overlay on the video tile.
        
        Args:
            text (str): Status message to display
            is_error (bool, optional): Whether this is an error message
            duration_ms (int, optional): Duration to show the message in milliseconds
        """
        try:
            self.status_label.setText(text)
            if is_error:
                self.status_label.setStyleSheet("background-color: rgba(150, 0, 0, 200); color: white; font-size: 10pt; padding: 3px;")
            else:
                self.status_label.setStyleSheet("background-color: rgba(0, 0, 0, 180); color: white; font-size: 10pt; padding: 3px;")

            self.status_label.show()
            self.reposition_status_label()

            if duration_ms > 0:
                QTimer.singleShot(duration_ms, self.safe_hide_status)
        except Exception as e:
            print(f"Error in show_status for Tile {self.tile_id}: {e}")

    def safe_hide_status(self):
        """Safely hides the status label, checking if the widget still exists."""
        try:
            if self and self.status_label:
                self.status_label.hide()
        except RuntimeError:
            pass
        except Exception as e:
            print(f"Error hiding status label safely for Tile {self.tile_id}: {e}")