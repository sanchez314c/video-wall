"""
Video loading and management functionality.
"""

import os
import random

from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtMultimedia import QMediaContent

from src.config.settings import (
    LOW_LATENCY_MODE,
    VIDEO_LOADING_TIMEOUT_MS,
)


class VideoLoader:
    """
    Handles loading of videos from various sources and prepares them for display.
    """

    def __init__(self, m3u8_links=None, local_videos=None):
        """
        Initialize the video loader.

        Args:
            m3u8_links (list, optional): List of M3U8 stream URLs
            local_videos (list, optional): List of local video file paths
        """
        self.m3u8_links = m3u8_links or []
        self.local_videos = local_videos or []
        self.recently_used_videos = []
        self.failed_streams = set()
        self.player_count = 0  # Track number of players configured

    def load_stream(self, url, player, timeout_callback=None):
        """
        Load an M3U8 stream into a media player.

        Args:
            url (str): Stream URL
            player (QMediaPlayer): Media player to load the stream into
            timeout_callback (callable, optional): Function to call on timeout

        Returns:
            bool: True if loading initiated successfully, False otherwise
        """
        try:
            if not url or not player:
                return False

            # Create a QMediaContent object with the stream URL
            media_content = QMediaContent(QUrl(url))

            # Configure player settings for streaming
            # Note: setBufferSize is not available in PyQt5's QMediaPlayer

            # Set playback rate options for streaming
            if LOW_LATENCY_MODE:
                player.setPlaybackRate(1.01)  # Slightly faster to catch up

            # Set media and initiate playback
            player.setMedia(media_content)

            # Set up loading timeout
            if timeout_callback:
                # Store timeout timer on player for cleanup
                if hasattr(player, "_loading_timer"):
                    player._loading_timer.stop()
                player._loading_timer = QTimer()
                player._loading_timer.setSingleShot(True)
                player._loading_timer.timeout.connect(lambda: timeout_callback(url, player))
                player._loading_timer.start(VIDEO_LOADING_TIMEOUT_MS)

            return True
        except Exception as e:
            print(f"Error loading stream {url}: {e}")
            self.failed_streams.add(url)
            return False

    def load_local_video(self, player):
        """
        Load a random local video into a media player, avoiding recently used videos.

        Args:
            player (QMediaPlayer): Media player to load the video into

        Returns:
            str: Path to the loaded video file, or None if loading failed
        """
        if not self.local_videos:
            return None

        # Get available videos that weren't recently used
        available_videos = [v for v in self.local_videos if v not in self.recently_used_videos]

        # If all videos have been recently used, reset and use all videos
        if not available_videos:
            self.recently_used_videos = []
            available_videos = self.local_videos

        if not available_videos:
            return None

        # Select a random video from available options
        selected_video = random.choice(available_videos)

        try:
            # Create QMediaContent with local file path
            file_url = QUrl.fromLocalFile(selected_video)
            media_content = QMediaContent(file_url)

            # Set media and playback options
            player.setMedia(media_content)

            # Add to recently used and keep list at reasonable size
            self.recently_used_videos.append(selected_video)
            if len(self.recently_used_videos) > min(len(self.local_videos) // 2, 20):
                self.recently_used_videos.pop(0)  # Remove oldest entry

            return selected_video
        except Exception as e:
            print(f"Error loading local video {selected_video}: {e}")
            return None

    def configure_player(self, player):
        """
        Configure a QMediaPlayer with optimal settings.

        Args:
            player (QMediaPlayer): Media player to configure
        """
        # Set audio settings (muted for video wall)
        player.setMuted(True)
        player.setVolume(0)

        # Set notification interval for smoother playback
        player.setNotifyInterval(100)  # Update every 100ms instead of default

        # Check if hardware acceleration is enabled
        hwa_enabled = os.environ.get("VIDEOWALL_HWA_ENABLED", "0") == "1"

        # In PyQt5, we can't directly control HWA per player, but we can log the status
        if self.player_count == 0:
            if hwa_enabled:
                print("Hardware acceleration: ENABLED for video playback")
            else:
                print("Hardware acceleration: DISABLED - using CPU only for video playback")

        # Increment player count for next configuration
        self.player_count += 1

    def get_random_stream(self, exclude_list=None):
        """
        Get a random stream URL, avoiding those in the exclude list.

        Args:
            exclude_list (list, optional): List of URLs to exclude

        Returns:
            str: Stream URL, or None if no viable streams available
        """
        if not self.m3u8_links:
            return None

        exclude_set = set(exclude_list or [])

        # Filter available streams (excluding caller's blocklist)
        available_streams = [url for url in self.m3u8_links if url not in exclude_set]

        if not available_streams:
            return None

        # Prefer non-failed streams
        non_failed = [url for url in available_streams if url not in self.failed_streams]
        if non_failed:
            return random.choice(non_failed)

        # All remaining streams have failed before — clear failures and try one
        self.failed_streams.clear()
        return random.choice(available_streams)
