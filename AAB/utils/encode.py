import subprocess
import re
import os
from typing import Optional

def encode_file(input_file: str) -> Optional[str]:
    """
    Encode the input video file, add subtitles, and include metadata.
    
    Args:
    input_file (str): Path to the input video file.
    
    Returns:
    Optional[str]: Path to the output encoded file, or None if encoding fails.
    """
    try:
        # Extract filename without extension
        filename = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{filename}_encoded.mp4"
        
        # Extract subtitles
        subprocess.run(["ffmpeg", "-i", input_file, "-c:s", "srt", "subtitles.srt"], check=True)
        
        # Prepare ffmpeg command
        command = [
            "ffmpeg",
            "-i", input_file,
            "-i", "subtitles.srt",
            "-c:v", "libx264",
            "-preset", "medium",  
            "-crf", "23", 
            "-c:a", "aac",
            "-b:a", "128k", 
            "-c:s", "mov_text",
            "-metadata", "encoded by @Anime_Wyvern",
            "-movflags", "+faststart",  
            output_file
        ]
        
        # Run encoding command
        subprocess.run(command, check=True)
        
        # Clean up subtitle file
        os.remove("subtitles.srt")
        
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error during encoding: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
