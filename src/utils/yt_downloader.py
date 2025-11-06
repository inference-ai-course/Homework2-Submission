import subprocess
import os

def download_youtube_audio(url, output_filename):
    """
    Download audio from a YouTube video using yt-dlp.
    
    Args:
        url (str): YouTube video URL
        output_filename (str): Name of the output audio file (without extension)
    
    Returns:
        bool: True if download successful, False otherwise
    
    Example:
        >>>     video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        >>>     output_file = "my_audio"
        >>>     download_youtube_audio(video_url, output_file)
    """
    try:
        # Construct the yt-dlp command
        command = [
            'yt-dlp',
            '-x',  # Extract audio
            '--audio-format', 'mp3',  # Convert to mp3
            '--audio-quality', '0',  # Best quality
            '-o', f'{output_filename}.%(ext)s',  # Output template
            url
        ]
        
        # Run the command
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        
        print(f"Successfully downloaded audio to {output_filename}.mp3")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error downloading audio: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: yt-dlp is not installed or not found in PATH")
        print("Install it with: pip install yt-dlp")
        return False

import subprocess
import os

def download_youtube_audio_v2(url, output_filename, is_playlist=False):
    """
    Download audio from a YouTube video or playlist using yt-dlp.
    
    Args:
        url (str): YouTube video or playlist URL
        output_filename (str): Name of the output audio file (without extension)
                              For playlists, this becomes a template for individual files
        is_playlist (bool): Set to True if downloading a playlist
    
    Returns:
        bool: True if download successful, False otherwise

    Examples:
        >>> # Download a single video
        >>> video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        >>> download_youtube_audio_v2(video_url, "my_audio", is_playlist=False)
        >>> # Download a playlist
        >>> playlist_url = "https://www.youtube.com/playlist?list=PLAYLIST_ID"
        >>> download_youtube_audio_v2(playlist_url, "my_playlist", is_playlist=True)
    """
    try:
        # Base command
        command = [
            'yt-dlp',
            '-x',  # Extract audio
            '--audio-format', 'mp3',  # Convert to mp3
            '--audio-quality', '0',  # Best quality
        ]
        
        # Configure output template based on whether it's a playlist
        if is_playlist:
            # For playlists: add playlist index and video title
            command.extend([
                '-o', f'{output_filename}/%(playlist_index)s - %(title)s.%(ext)s',
                '--yes-playlist'  # Ensure playlist download
            ])
        else:
            command.extend([
                '-o', f'{output_filename}.%(ext)s',
                '--no-playlist'  # Only download single video even if URL is from playlist
            ])
        
        # Add the URL
        command.append(url)
        
        # Run the command
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True
        )
        
        if is_playlist:
            print(f"Successfully downloaded playlist to {output_filename}/ directory")
        else:
            print(f"Successfully downloaded audio to {output_filename}.mp3")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error downloading audio: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: yt-dlp is not installed or not found in PATH")
        print("Install it with: pip install yt-dlp")
        return False