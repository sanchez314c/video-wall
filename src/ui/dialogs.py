"""
Dialog windows for VideoWall.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel,
                            QFileDialog, QCheckBox, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class LocalVideoDialog(QDialog):
    """
    Configuration dialog for local video settings and stream options.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the configuration dialog.
        
        Args:
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Video Wall Configuration")
        self.setMinimumWidth(500)
        
        self.layout = QVBoxLayout()
        
        # Add a title label with larger font
        title_label = QLabel("Video Wall Configuration")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)
        
        # Create stream configuration section
        self._create_stream_section()
        
        # Create local video configuration section
        self._create_local_video_section()
        
        # Buttons
        self.continue_button = QPushButton("Start Video Wall")
        self.continue_button.clicked.connect(self.accept)
        self.layout.addWidget(self.continue_button)
        
        self.setLayout(self.layout)
        
        self.folder_path = None
        
    def _create_stream_section(self):
        """Create the stream configuration section of the dialog."""
        # Stream Configuration Section
        stream_group = QWidget()
        stream_layout = QVBoxLayout(stream_group)
        
        stream_header = QLabel("Stream Settings")
        stream_header.setFont(QFont("Arial", 12, QFont.Bold))
        stream_layout.addWidget(stream_header)
        
        # Stream testing options
        stream_options_label = QLabel("Live Stream Handling:")
        stream_layout.addWidget(stream_options_label)
        
        # Skip stream testing checkbox
        self.skip_stream_testing = QCheckBox("Skip Stream Testing (Assume All Streams are Valid)")
        self.skip_stream_testing.setChecked(True)  # Default to skipping tests
        self.skip_stream_testing.setToolTip("Enable this to skip stream validation and assume all streams are valid. Recommended for better startup.")
        stream_layout.addWidget(self.skip_stream_testing)
        
        # Warning label
        warning_label = QLabel("Note: When streams go offline, they'll automatically fall back to local videos.")
        warning_label.setStyleSheet("color: #AA5500;")
        warning_label.setWordWrap(True)
        stream_layout.addWidget(warning_label)
        
        self.layout.addWidget(stream_group)
        
    def _create_local_video_section(self):
        """Create the local video configuration section of the dialog."""
        # Local Video Configuration Section
        local_group = QWidget()
        local_layout = QVBoxLayout(local_group)
        
        local_header = QLabel("Local Video Settings")
        local_header.setFont(QFont("Arial", 12, QFont.Bold))
        local_layout.addWidget(local_header)
        
        # Add description
        desc_label = QLabel("Would you like to include local videos in the playback? "
                           "Local videos will be used as fallbacks when streams are offline.")
        desc_label.setWordWrap(True)
        local_layout.addWidget(desc_label)
        
        # Checkbox for enabling local videos
        self.enable_local_videos = QCheckBox("Enable Local Video Fallback")
        self.enable_local_videos.setChecked(True)
        local_layout.addWidget(self.enable_local_videos)
        
        # Button to select folder
        self.select_folder_button = QPushButton("Select Video Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        local_layout.addWidget(self.select_folder_button)
        
        # Status label
        self.status_label = QLabel("No folder selected")
        local_layout.addWidget(self.status_label)
        
        self.layout.addWidget(local_group)
        
    def select_folder(self):
        """
        Open a file dialog to select a folder with video files.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with Video Files")
        if folder:
            self.folder_path = folder
            self.status_label.setText(f"Selected: {folder}")
            
    def get_results(self):
        """
        Get the configuration results from the dialog.
        
        Returns:
            dict: Configuration settings
        """
        return {
            "use_local_videos": self.enable_local_videos.isChecked(),
            "folder_path": self.folder_path,
            "skip_stream_testing": self.skip_stream_testing.isChecked()
        }