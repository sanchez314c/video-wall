"""
Global stream tracking and assignment for VideoWall.
"""
import random
import os

class GlobalVideoAssigner:
    """
    Manages video source assignments across multiple monitors.
    Ensures optimal distribution of streams and local videos.
    """
    
    def __init__(self, all_links=None, local_videos=None):
        """
        Initialize the global video assigner.
        
        Args:
            all_links (list, optional): List of all M3U8 stream URLs
            local_videos (list, optional): List of local video file paths
        """
        self.all_links = all_links or []
        self.local_videos = local_videos or []
        self.monitor_assignments = {}
        self.reserved_videos = set()
        self.recently_used_videos = []
        
        # Filter out problematic local videos
        self.filter_local_videos()
    
    def get_unique_streams_for_monitor(self, screen_name, count):
        """
        Gets unique streams for a specific monitor that don't overlap with other monitors.
        
        Args:
            screen_name (str): Name of the screen/monitor
            count (int): Number of streams needed
            
        Returns:
            list: List of stream URLs assigned to this monitor
        """
        current_assignments = self.monitor_assignments.get(screen_name, {})
        all_used = set()
        
        # Collect all URLs already assigned to any monitor
        for assignments in self.monitor_assignments.values():
            all_used.update(assignments.values())
        
        # Try to get URLs not used anywhere
        available = [link for link in self.all_links if link not in all_used]
        needed = count
        result = []
        
        if available:
            random.shuffle(available)
            take = min(needed, len(available))
            result.extend(available[:take])
            needed -= take
        
        # If we still need more, take from those used by other monitors
        if needed > 0:
            other_used = all_used - set(current_assignments.values())
            if other_used:
                other_available = [link for link in self.all_links if link in other_used]
                random.shuffle(other_available)
                take = min(needed, len(other_available))
                result.extend(other_available[:take])
                needed -= take
        
        # If still more needed, take any remaining
        if needed > 0:
            remaining = [link for link in self.all_links if link not in result]
            if remaining:
                random.shuffle(remaining)
                result.extend(remaining[:needed])
        
        return result
    
    def filter_local_videos(self):
        """
        Filters the local_videos list to remove problematic files.
        """
        if not self.local_videos:
            return
            
        valid_videos = []
        for video_path in self.local_videos:
            # Skip macOS metadata files (._) and hidden files
            basename = os.path.basename(video_path)
            if basename.startswith('._') or basename.startswith('.'):
                continue
                
            # Skip files that don't exist or are zero size
            try:
                if not os.path.exists(video_path) or os.path.getsize(video_path) <= 0:
                    continue
            except Exception:
                continue
                
            valid_videos.append(video_path)
        
        self.local_videos = valid_videos
        print(f"GlobalVideoAssigner: Filtered to {len(self.local_videos)} valid local videos")
    
    def get_local_video(self):
        """
        Returns a random local video file, tracking recently used videos to avoid repetition.
        
        Returns:
            str: Path to a local video file, or None if no valid videos available
        """
        # First ensure we have valid videos
        self.filter_local_videos()
        
        if not self.local_videos:
            return None
            
        # Get available videos that weren't recently used
        available_videos = [v for v in self.local_videos if v not in self.recently_used_videos]
        
        # If all videos have been recently used, reset and use all videos
        if not available_videos:
            self.recently_used_videos = []
            available_videos = self.local_videos
            
        if not available_videos:
            print("  Warning: No valid local videos available after filtering")
            return None
            
        # Select a random video from available options
        selected_video = random.choice(available_videos)
        
        # Add to recently used and keep list at reasonable size
        self.recently_used_videos.append(selected_video)
        if len(self.recently_used_videos) > min(len(self.local_videos) // 2, 20):
            self.recently_used_videos.pop(0)  # Remove oldest entry
            
        return selected_video
    
    def update_assignments(self, screen_name, new_assignments):
        """
        Updates the video assignments for a monitor.
        
        Args:
            screen_name (str): Name of the screen/monitor
            new_assignments (dict): Dictionary mapping tile IDs to stream URLs
        """
        self.monitor_assignments[screen_name] = new_assignments