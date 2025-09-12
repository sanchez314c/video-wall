"""
File handling utilities for VideoWall.
"""
import os

def get_all_m3u8_links(file_path):
    """
    Load and validate M3U8 links from a file.
    
    Args:
        file_path (str): Path to the M3U8 file
        
    Returns:
        list: List of valid M3U8 URLs
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        links = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Ensure URL has http/https protocol
                if not line.startswith(('http://', 'https://')):
                    line = 'https://' + line
                links.append(line)
                
        unique_links = sorted(list(set(links)))
        print(f"Loaded {len(links)} links, {len(unique_links)} unique.")
        
        # Validate URLs
        valid_links = []
        for url in unique_links:
            if '://' in url and '.' in url:  # Very basic URL validation
                valid_links.append(url)
            else:
                print(f"Warning: Skipping invalid URL: {url}")
        
        if not valid_links:
            print("Warning: No valid M3U8 links found in the file.")
            
        return valid_links
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return []

def get_video_files_recursively(folder_path):
    """
    Recursively scan a folder for video files.
    
    Args:
        folder_path (str): Path to the folder to scan
        
    Returns:
        list: List of full paths to video files
    """
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg', '.3gp']
    video_files = []
    
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # Skip hidden files (starting with ._) and other metadata files
                if file.startswith('._') or file.startswith('.'):
                    continue
                    
                if any(file.lower().endswith(ext) for ext in video_extensions):
                    full_path = os.path.join(root, file)
                    # Verify file exists and is accessible
                    if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                        video_files.append(full_path)
        
        print(f"Found {len(video_files)} valid local video files in {folder_path} and subdirectories.")
        return video_files
    except Exception as e:
        print(f"Error scanning for video files: {e}")
        return []