"""
Video loading and management functionality.
"""
import os
import sys
import random
import subprocess
import platform
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

from src.utils.file_utils import get_video_files_recursively, get_all_m3u8_links
from src.config.settings import VIDEO_BUFFER_SIZE, LOW_LATENCY_MODE, HARDWARE_DECODE_PRIORITY, HARDWARE_ACCEL_STRATEGY, VIDEO_LOADING_TIMEOUT_MS

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
        self.player_count = 0  # Track number of players configured for alternating strategy
        
        # Initialize GPU info with defaults (detection will happen asynchronously)
        self.gpu_info = {
            'cuda_available': False,
            'cuda_devices': [],
            'rocm_available': False,
            'rocm_devices': [],
            'metal_available': platform.system() == "Darwin",
            'vaapi_available': False,
            'vdpau_available': False,
            'total_gpus': 0,
            'platform': platform.system()
        }
        self.current_gpu_index = 0  # For round-robin GPU assignment
        
        # Detect GPU capabilities in background (non-blocking)
        # For now, we'll use simple detection without subprocess calls
    
    def _detect_gpu_capabilities(self):
        """
        Detect available GPU hardware acceleration capabilities.
        
        Returns:
            dict: Information about available GPUs and acceleration methods
        """
        gpu_info = {
            'cuda_available': False,
            'cuda_devices': [],
            'rocm_available': False,
            'rocm_devices': [],
            'metal_available': False,
            'vaapi_available': False,
            'vdpau_available': False,
            'total_gpus': 0,
            'platform': platform.system()
        }
        
        system = platform.system()
        
        if system == "Linux":
            # Check for NVIDIA CUDA
            try:
                nvidia_smi = subprocess.run(['nvidia-smi', '--query-gpu=index,name,memory.total', '--format=csv,noheader'], 
                                          capture_output=True, text=True, timeout=5)
                if nvidia_smi.returncode == 0:
                    gpu_info['cuda_available'] = True
                    for line in nvidia_smi.stdout.strip().split('\n'):
                        parts = line.split(', ')
                        if len(parts) >= 3:
                            gpu_info['cuda_devices'].append({
                                'index': int(parts[0]),
                                'name': parts[1],
                                'memory': parts[2]
                            })
                    print(f"Detected {len(gpu_info['cuda_devices'])} NVIDIA GPU(s) with CUDA support")
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
            
            # Check for AMD ROCm
            try:
                rocm_smi = subprocess.run(['rocm-smi', '--showid'], 
                                         capture_output=True, text=True, timeout=5)
                if rocm_smi.returncode == 0:
                    gpu_info['rocm_available'] = True
                    # Parse ROCm devices
                    rocm_info = subprocess.run(['rocm-smi', '--showname'], 
                                              capture_output=True, text=True, timeout=5)
                    if rocm_info.returncode == 0:
                        lines = rocm_info.stdout.strip().split('\n')
                        for line in lines:
                            if 'GPU' in line and ':' in line:
                                gpu_info['rocm_devices'].append({'name': line.split(':')[1].strip()})
                    print(f"Detected {len(gpu_info['rocm_devices'])} AMD GPU(s) with ROCm support")
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
            
            # Check for Intel VAAPI
            try:
                vainfo = subprocess.run(['vainfo'], capture_output=True, text=True, timeout=5)
                if vainfo.returncode == 0 and 'VAProfileH264' in vainfo.stdout:
                    gpu_info['vaapi_available'] = True
                    print("Detected Intel VAAPI hardware acceleration")
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
            
            # Check for VDPAU (older NVIDIA)
            try:
                vdpauinfo = subprocess.run(['vdpauinfo'], capture_output=True, text=True, timeout=5)
                if vdpauinfo.returncode == 0:
                    gpu_info['vdpau_available'] = True
                    print("Detected VDPAU hardware acceleration")
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
                
        elif system == "Darwin":  # macOS
            # Check for Metal support (all modern Macs)
            gpu_info['metal_available'] = True
            # Check for Apple Silicon
            try:
                arch = subprocess.run(['arch'], capture_output=True, text=True)
                if arch.returncode == 0 and 'arm64' in arch.stdout:
                    print("Detected Apple Silicon with Metal acceleration")
                else:
                    print("Detected Intel Mac with Metal acceleration")
            except:
                pass
        
        elif system == "Windows":
            # Check for NVIDIA CUDA on Windows
            try:
                nvidia_smi = subprocess.run(['nvidia-smi.exe', '--query-gpu=index,name', '--format=csv,noheader'], 
                                          capture_output=True, text=True, timeout=5, shell=True)
                if nvidia_smi.returncode == 0:
                    gpu_info['cuda_available'] = True
                    for line in nvidia_smi.stdout.strip().split('\n'):
                        parts = line.split(', ')
                        if len(parts) >= 2:
                            gpu_info['cuda_devices'].append({
                                'index': int(parts[0]),
                                'name': parts[1]
                            })
            except:
                pass
        
        # Calculate total GPUs
        gpu_info['total_gpus'] = len(gpu_info['cuda_devices']) + len(gpu_info['rocm_devices'])
        if gpu_info['vaapi_available']:
            gpu_info['total_gpus'] += 1
            
        return gpu_info
        
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
                if hasattr(player, '_loading_timer'):
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
        hwa_enabled = os.environ.get('VIDEOWALL_HWA_ENABLED', '0') == '1'
        
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
        exclude_set.update(self.failed_streams)
        
        # Filter available streams
        available_streams = [url for url in self.m3u8_links if url not in exclude_set]
        
        if not available_streams:
            # If all streams are excluded, reset failed streams and try again
            if self.failed_streams:
                self.failed_streams.clear()
                return self.get_random_stream(exclude_list)
            # If still no streams, return None
            return None
            
        return random.choice(available_streams)