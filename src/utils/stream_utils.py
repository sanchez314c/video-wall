"""
Stream utilities for VideoWall.
"""
import time
import random
import requests
from urllib.parse import urlparse

def validate_stream(url, timeout=5):
    """
    Validate if a stream URL is accessible.
    
    Args:
        url (str): Stream URL to validate
        timeout (int, optional): Request timeout in seconds
        
    Returns:
        bool: True if the stream appears valid, False otherwise
    """
    try:
        # Parse URL to ensure it's valid
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            print(f"Invalid URL format: {url}")
            return False
            
        # Make a HEAD request with timeout
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        # Check if response is successful
        if response.status_code == 200:
            print(f"Stream validation successful: {url}")
            return True
        else:
            print(f"Stream validation failed with status {response.status_code}: {url}")
            return False
            
    except requests.RequestException as e:
        print(f"Stream validation error: {e} - {url}")
        return False
    except Exception as e:
        print(f"Unexpected error during stream validation: {e} - {url}")
        return False

def get_stream_metadata(url):
    """
    Retrieve metadata about a stream.
    
    Args:
        url (str): Stream URL to check
        
    Returns:
        dict: Dictionary containing stream metadata or None if retrieval fails
    """
    try:
        # Make a HEAD request to get headers
        response = requests.head(url, timeout=5, allow_redirects=True)
        
        if response.status_code == 200:
            # Extract content type and length if available
            metadata = {
                'content_type': response.headers.get('Content-Type', 'unknown'),
                'content_length': response.headers.get('Content-Length', 'unknown'),
                'server': response.headers.get('Server', 'unknown'),
            }
            return metadata
        else:
            return None
            
    except Exception:
        return None

def should_retry_stream(retry_count, max_retries=3, base_delay=5):
    """
    Determine if a stream should be retried and calculate backoff delay.
    
    Args:
        retry_count (int): Current retry count
        max_retries (int, optional): Maximum number of retries
        base_delay (int, optional): Base delay in seconds
        
    Returns:
        tuple: (should_retry, delay_seconds)
    """
    if retry_count >= max_retries:
        return False, 0
        
    # Exponential backoff with jitter
    delay = base_delay * (2 ** retry_count) + random.uniform(0, 1)
    return True, delay