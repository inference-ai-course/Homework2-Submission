import whisper
import os
import logging
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()])

def transcribe_audio(audio_path: str, model_name: str = "tiny") -> str:
    """
    Transcribes an audio file using Whisper.

    Args:
        audio_path (str): Path to the audio file.
        model_name (str): Name of the Whisper model to use.

    Returns:
        str: The transcribed text.
    """
    if not os.path.exists(audio_path):
        logging.error(f"Audio file not found: {audio_path}")
        return ""

    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        return ""

def transcribe_single_file(audio_path: str, model_name: str = "tiny") -> dict:
    """
    Transcribes a single audio file and returns the result with metadata.

    Args:
        audio_path (str): Path to the audio file.
        model_name (str): Name of the Whisper model to use.

    Returns:
        dict: Dictionary containing file path, transcription, and status.
    """
    logging.info(f"Starting transcription for: {audio_path}")
    
    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(audio_path)
        
        # Save transcription to a text file in the same directory
        transcript_path = Path(audio_path).with_suffix('.txt')
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        
        logging.info(f"Completed transcription for: {audio_path}")
        
        return {
            "file": os.path.basename(audio_path),
            "path": audio_path,
            "transcription": result["text"],
            "transcript_file": str(transcript_path),
            "status": "success"
        }
    except Exception as e:
        logging.error(f"Error transcribing {audio_path}: {e}")
        return {
            "file": os.path.basename(audio_path),
            "path": audio_path,
            "transcription": "",
            "transcript_file": "",
            "status": f"error: {str(e)}"
        }

def transcribe_folder_threaded(folder_path: str, model_name: str = "tiny", max_workers: int = 3, file_extensions: list = None) -> list:
    """
    Transcribes all audio files in a folder using multiple threads.
    Saves each transcription as a .txt file in the same folder.

    Args:
        folder_path (str): Path to the folder containing audio files.
        model_name (str): Name of the Whisper model to use (default: "tiny").
        max_workers (int): Maximum number of concurrent threads (default: 3).
        file_extensions (list): List of file extensions to process (default: ['.mp3', '.wav', '.m4a', '.flac']).

    Returns:
        list: List of dictionaries containing transcription results.
    """
    if file_extensions is None:
        file_extensions = ['.mp3', '.wav', '.m4a', '.flac']
    
    if not os.path.exists(folder_path):
        logging.error(f"Folder not found: {folder_path}")
        return []
    
    # Get all audio files in the folder
    audio_files = []
    for filename in os.listdir(folder_path):
        if any(filename.lower().endswith(ext) for ext in file_extensions):
            audio_files.append(os.path.join(folder_path, filename))
    
    if not audio_files:
        logging.warning(f"No audio files found in {folder_path}")
        return []
    
    logging.info(f"Found {len(audio_files)} audio files to transcribe")
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all transcription tasks
        future_to_file = {
            executor.submit(transcribe_single_file, audio_file, model_name): audio_file 
            for audio_file in audio_files
        }
        
        # Process completed tasks as they finish
        for future in as_completed(future_to_file):
            audio_file = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logging.error(f"Exception for {audio_file}: {e}")
                results.append({
                    "file": os.path.basename(audio_file),
                    "path": audio_file,
                    "transcription": "",
                    "transcript_file": "",
                    "status": f"exception: {str(e)}"
                })
    
    # Save summary as JSONL
    summary_path = os.path.join(folder_path, "transcription_summary.jsonl")
    with open(summary_path, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')
    
    logging.info(f"Transcription complete. Summary saved to {summary_path}")
    logging.info(f"Successfully transcribed {sum(1 for r in results if r['status'] == 'success')} out of {len(results)} files")
    
    return results
