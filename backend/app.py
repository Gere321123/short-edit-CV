from flask import Flask, request, jsonify, send_from_directory, send_file
from video_service import VideoService
from video_processor import VideoProcessor
from transcriber import Transcriber
from flask_cors import CORS
import config
import concurrent.futures
import os
import sqlite3
import wave

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "http://localhost:8080"}})

UPLOAD_FOLDER = 'uploads'

PROCESSED_FOLDER = 'processed'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
video_service = VideoService()
transcriber = Transcriber()

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def get_sample_rate(file_path):
    with wave.open(file_path, 'rb') as audio_file:
        return audio_file.getframerate()

def transcribe_background(video_id, audio_path):
    try:
        transcript = transcriber.transcribe_long_audio(audio_path)
        video_service.update_transcript(video_id, transcript)
    except Exception as e:
        print(f"Transcription failed for video ID {video_id}: {e}")
        video_service.update_transcript(video_id, "Transcription failed")

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files or 'text' not in request.form:
        return jsonify({'error': 'No video file provided'}), 400

    file = request.files['video']
    text = request.form['text']
    

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save video file
    video_path = os.path.join(config.Config.UPLOAD_FOLDER, file.filename)
    file.save(video_path)
    
    
    #Vide Reldereles
    # processor = VideoProcessor(video_path)
    # processor.add_text(text)
    # processor.save_video(PROCESSED_FOLDER)

    # Extract audio
    # audio_path = video_service.extract_audio(video_path)
    
    # # Check the sample rate of the extracted audio
    # sample_rate = get_sample_rate(audio_path)
    # print(f"Audio Sample Rate: {sample_rate}")

    # # Save initial entry to database
    # video_service.save_video(file.filename, video_path, audio_path)
    # video_id = get_last_inserted_id()

    
    # video_id = os.path.splitext(file.filename)[0]
    # audio_folder = os.path.join('audios', video_id)
    
    # transcribe_background(video_id,audio_folder)

    return jsonify({'message': 'Video uploaded successfully', 'video_id': file.filename}), 200

def transcribe_and_collect(audio_file, audio_folder):
    audio_path = os.path.join(audio_folder, audio_file)

    try:
        transcription = transcriber.transcribe_long_audio(audio_path)
    except AttributeError:
        print("The method transcribe_audio does not exist in video_service.")
        transcription = None
    
    return transcription

def transcribe_background(filename, audio_folder):
    # Construct the path to the correct database file
    db_path = os.path.join(audio_folder, f"{os.path.splitext(filename)[0]}.db")

    # Ensure the database path is correct
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return

    # List all audio files in the folder
    audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.wav') and '_part' in f]

    # Sort files based on the part number
    audio_files.sort(key=lambda x: int(x.split('_part')[-1].split('.')[0]))

    # Use ThreadPoolExecutor to run the transcriptions in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Collect transcriptions
        transcriptions = list(executor.map(lambda audio_file: transcribe_and_collect(audio_file, audio_folder), audio_files))

    # Connect to the SQLite database once
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update the database with all transcriptions
    for part_number, audio_file in enumerate(audio_files, start=1):
        transcription = transcriptions[part_number - 1]
        if transcription is not None:
            cursor.execute("UPDATE clips SET text = ? WHERE id = ?", (transcription, part_number))

    conn.commit()
    conn.close()

    print(f"Transcription completed for video: {filename}")
    
@app.route('/download/<video_id>', methods=['GET'])
def download_video(video_id):
    # A letöltéshez az azonosítót használjuk
    for file_name in os.listdir(UPLOAD_FOLDER):
        if video_id in file_name:
            return send_file(os.path.join(UPLOAD_FOLDER, file_name), as_attachment=True)
    return {"error": "Video not found"}, 404


@app.route('/transcript/<int:video_id>', methods=['GET'])
def get_transcript(video_id):
    video = video_service.get_video(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    response = {
        'video_id': video[0],
        'filename': video[1],
        'filepath': video[2],
        'audio_path': video[3],
        'transcript': video[4],
        'status': video[5]
    }
    return jsonify(response), 200

def get_last_inserted_id():
    conn = sqlite3.connect(config.Config.DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT last_insert_rowid()')
    last_id = cursor.fetchone()[0]
    conn.close()
    return last_id

if __name__ == '__main__':
    app.run(debug=True)
