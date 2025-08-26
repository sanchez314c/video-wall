"""
Screen recorder for VideoWall using ffmpeg x11grab.
Captures the fullscreen video wall to MP4 files on the Desktop.
"""
import os
import subprocess
import signal
from datetime import datetime
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


class RecordingIndicator(QLabel):
    """Red blinking REC dot overlay shown during recording."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("  REC")
        self.setFont(QFont("Inter", 14, QFont.Bold))
        self.setFixedSize(90, 32)
        self._visible_state = True

        self.setStyleSheet(
            "background: rgba(220, 38, 38, 0.85);"
            "color: #ffffff;"
            "border-radius: 6px;"
            "padding: 4px 8px;"
        )
        self.hide()

        self._blink_timer = QTimer(self)
        self._blink_timer.timeout.connect(self._blink)

    def start(self):
        self.show()
        self.raise_()
        self._visible_state = True
        self._blink_timer.start(800)

    def stop(self):
        self._blink_timer.stop()
        self.hide()

    def _blink(self):
        self._visible_state = not self._visible_state
        self.setVisible(self._visible_state)
        if self._visible_state:
            self.raise_()


class ScreenRecorder:
    """
    Records the VideoWall screen region to MP4 using ffmpeg x11grab.
    Each start/stop cycle creates a new timestamped file on ~/Desktop/.
    """

    def __init__(self, video_wall):
        self.video_wall = video_wall
        self.process = None
        self.is_recording = False
        self.current_file = None
        self.recording_count = 0

        # Recording indicator overlay
        self.indicator = RecordingIndicator(video_wall)
        self.indicator.move(20, 20)

    @property
    def output_dir(self):
        return os.path.expanduser("~/Desktop")

    def toggle(self):
        """Toggle recording on/off. Returns the state after toggle."""
        if self.is_recording:
            self.stop()
        else:
            self.start()
        return self.is_recording

    def start(self):
        """Start recording the video wall screen region."""
        if self.is_recording:
            return

        # Get the window/screen geometry
        screen = self.video_wall.screen
        if screen:
            geom = screen.geometry()
        else:
            geom = self.video_wall.geometry()

        x = geom.x()
        y = geom.y()
        w = geom.width()
        h = geom.height()

        # Ensure even dimensions (ffmpeg h264 requirement)
        w = w if w % 2 == 0 else w - 1
        h = h if h % 2 == 0 else h - 1

        # Generate output filename
        self.recording_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"VideoWall-Recording-{timestamp}.mp4"
        self.current_file = os.path.join(self.output_dir, filename)

        # Build ffmpeg command
        display = os.environ.get("DISPLAY", ":0")
        cmd = [
            "ffmpeg",
            "-y",                           # Overwrite if exists
            "-video_size", f"{w}x{h}",
            "-framerate", "30",
            "-f", "x11grab",
            "-i", f"{display}+{x},{y}",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-threads", "0",                # Use all CPU cores
            self.current_file
        ]

        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.is_recording = True
            self.indicator.start()
            print(f"Recording started: {self.current_file}")
        except Exception as e:
            print(f"Failed to start recording: {e}")
            self.is_recording = False

    def stop(self):
        """Stop the current recording and finalize the MP4 file."""
        if not self.is_recording or not self.process:
            return

        try:
            # Send 'q' to ffmpeg stdin for graceful shutdown
            self.process.stdin.write(b"q")
            self.process.stdin.flush()
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if it doesn't stop gracefully
            self.process.send_signal(signal.SIGINT)
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        except Exception as e:
            print(f"Error stopping recording: {e}")
            if self.process:
                self.process.kill()

        self.is_recording = False
        self.process = None
        self.indicator.stop()
        print(f"Recording saved: {self.current_file}")

    def cleanup(self):
        """Stop recording if active. Call on app exit."""
        if self.is_recording:
            self.stop()
