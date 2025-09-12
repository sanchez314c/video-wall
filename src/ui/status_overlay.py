"""
Status overlay components for video tiles.
"""
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QColor, QPainter, QPen, QFont

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
        
        # Set default styling
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180); color: white; font-size: 10pt; padding: 5px; border-radius: 3px;")
        
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
        
        # Apply error styling if needed
        if is_error:
            self.setStyleSheet("background-color: rgba(150, 0, 0, 200); color: white; font-size: 10pt; padding: 5px; border-radius: 3px;")
        else:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 180); color: white; font-size: 10pt; padding: 5px; border-radius: 3px;")
        
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