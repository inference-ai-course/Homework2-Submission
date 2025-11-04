# Task 3

import subprocess
import os
import json
import whisper

def download_youtube_audio(url, output_folder='audio_downloads'):
    """
    Download audio from a YouTube video using yt-dlp.
    
    Args:
        url (str): The YouTube video URL
        output_path (str): Directory to save the audio file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # yt-dlp command to download audio in best quality MP3
    command = [
        'yt-dlp',
        '-x',  # Extract audio
        '--audio-format', 'mp3',  # Convert to MP3
        '--audio-quality', '0',  # Best quality
        '-o', f'{output_folder}/%(title)s.%(ext)s',  # Output template
        url
    ]
    
    try:
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print("Download completed successfully!")
            # Extract filename from output
            for line in result.stdout.split('\n'):
                if '[download] Destination:' in line:
                    filename = line.split('[download] Destination: ')[1].strip()
                    filename = filename.replace(".webm", ".mp3")
                    return filename
        else:
            print(f"Error downloading {url}: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading audio: {e}")
        print(e.stderr)

    return None

def transcribe_audio(audio_path, model_size='base'):
    """
    Transcribe audio file using Whisper.
    
    Args:
        audio_path (str): Path to the audio file
        model_size (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
    
    Returns:
        str: Transcript text
    """
    try:
        # Load the Whisper model
        model = whisper.load_model(model_size)
        
        # Transcribe the audio
        result = model.transcribe(audio_path)
        
        # Return the transcript
        return result
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None

def save_transcript(audio_path, transcript_folder, video_url):
    """
    from audio file to a JSONL file.
    Args:
        audio_path (str): Path to the audio file
        transcript_folder (str): Folder Path to save the JSONL file
    """
    # Create output directory if it doesn't exist
    os.makedirs(transcript_folder, exist_ok=True)

    transcript_path = f'{transcript_folder}/' + os.path.splitext(os.path.basename(audio_path))[0] + '_transcript.jsonl'
    transcripts = []
    if audio_path:
        # Transcribe audio
        result = transcribe_audio(audio_path)
        title = os.path.splitext(os.path.basename(audio_path))[0]
        transcript_data = {
                        "url": video_url,
                        "title": title,
                        "transcript": [
                            {
                                "start": segment['start'],
                                "end": segment['end'],
                                "text": segment['text'].strip()
                            } for segment in result['segments']
                        ]
                    }
        transcripts.append(transcript_data)
    try:
        # Save transcript data to JSONL file
        with open(transcript_path, 'w', encoding='utf-8') as f:
            for item in transcripts:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"Transcript saved to: {transcript_path}")
    except Exception as e:
        print(f"Error saving transcript: {e}")

# Example usage
if __name__ == "__main__":
    output_folder = 'audio_downloads'
    transcript_folder = f'{output_folder}/transcripts'
    # video_urls = ["https://www.youtube.com/watch?v=9Kvm0K7dz48"]
    video_urls = [
        "https://www.youtube.com/watch?v=CMrHM8a3hqw", 
        "https://www.youtube.com/watch?v=d4gGtcobq8M", 
        "https://www.youtube.com/watch?v=2LcZjPPJfWo",
        "https://www.youtube.com/shorts/yHPbFXCDr3k",
        "https://www.youtube.com/watch?v=8dqAiizVF-U",
        "https://m.youtube.com/watch?v=DhB9fE-TQow",
        "https://www.youtube.com/watch?v=7ST6JEB-xJU",
        "https://www.youtube.com/watch?v=zC6qd86iUkU",
        "https://www.youtube.com/watch?v=TW7h71L-y1A",
        "https://www.youtube.com/watch?v=plCvF_7qrmY"
        ]
    
    for video_url in video_urls:
    # Download audio
        print(f"Processing {video_url}")
        audio_path = download_youtube_audio(video_url,output_folder)
        save_transcript(audio_path, transcript_folder, video_url)

            
