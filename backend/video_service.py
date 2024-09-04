import os
import sqlite3
from moviepy.editor import VideoFileClip
import config
import subprocess
from pydub import AudioSegment

class VideoService:
    def __init__(self):
        self.db_path = config.Config.DATABASE
        self.upload_folder = config.Config.UPLOAD_FOLDER
        self.audio_folder = config.Config.AUDIO_FOLDER
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS videos (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              filename TEXT NOT NULL,
                              filepath TEXT NOT NULL,
                              audio_path TEXT NOT NULL,
                              transcript TEXT,
                              status TEXT NOT NULL)''')
        conn.commit()
        conn.close()
    
    def save_video(self, filename, filepath, audio_path, transcript=None, status="processing"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO videos (filename, filepath, audio_path, transcript, status) 
                          VALUES (?, ?, ?, ?, ?)''',
                       (filename, filepath, audio_path, transcript, status))
        conn.commit()
        conn.close()
    
    def extract_audio(self, video_path):
        audio_path = video_path.replace('.mp4', '.wav')  # Adjust the output format as needed
    
        # Extract audio from video
        command = [
            'ffmpeg', '-i', video_path,
            '-ac', '1',  # Convert to mono
            '-ar', '16000',  # Set the sample rate (adjust as necessary)
            audio_path
        ]
        subprocess.run(command, check=True)
        
        # Split the audio file into parts based on silence
        self.split_audio(audio_path)
        
        return audio_path
    def create_database(self, db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS clips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time INTEGER,
                end_time INTEGER,
                text TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def insert_clip_data(self, db_path, start_time, end_time):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO clips (start_time, end_time, text)
            VALUES (?, ?, ?)
        ''', (start_time, end_time, ""))
        conn.commit()
        conn.close()
        
    def split_audio(self, audio_path, silence_thresh=-35, min_silence_len=300, padding=500, min_clip_len=2000):
        audio = AudioSegment.from_wav(audio_path)
        
        silences = self.detect_silence(audio, silence_thresh, min_silence_len)
        
        output_folder = os.path.join(self.audio_folder, os.path.splitext(os.path.basename(audio_path))[0])
        os.makedirs(output_folder, exist_ok=True)
        
        db_filename = f"{os.path.splitext(os.path.basename(audio_path))[0]}.db"
        db_path = os.path.join(output_folder, db_filename)
        self.create_database(db_path)
        
        i = 0
        start_time = 0
        j=1
        
        for i, silence_start in enumerate(silences):
            end_time = silence_start[0]
            
            # Ellenőrizzük, hogy az aktuális klip elég hosszú-e
            if end_time - start_time + padding < min_clip_len:
                continue
            
            # Ha a start_time 0, ne adjunk hozzá paddingot a kezdéshez
            if start_time == 0:
                clip = audio[start_time:end_time + padding]
            else:
                clip = audio[start_time - padding:end_time + padding]
            
            clip_filename = os.path.join(output_folder, f"{os.path.basename(audio_path).split('.')[0]}_part{j}.wav")
            j=j+1
            clip.export(clip_filename, format="wav")
            
            self.insert_clip_data(db_path, start_time, end_time)
            
            start_time = silence_start[1] + padding
        
        # Az utolsó szegmens mentése, akkor is ha a ciklus miatt kimaradt volna
        if len(audio) - start_time < min_clip_len and start_time < len(audio):
            clip = audio[start_time:]
            clip_filename = os.path.join(output_folder, f"{os.path.basename(audio_path).split('.')[0]}_part{j}.wav")
            clip.export(clip_filename, format="wav")
            
            self.insert_clip_data(db_path, start_time, len(audio))

    
    def detect_silence(self, audio, silence_thresh=-30, min_silence_len=500):
        silences = []
        silence_start = None
        
        for ms in range(0, len(audio)):
            if audio[ms:ms + min_silence_len].dBFS < silence_thresh:
                if silence_start is None:
                    silence_start = ms
            else:
                if silence_start is not None:
                    silence_end = ms
                    silences.append((silence_start, silence_end))
                    silence_start = None
        return silences
    
    def update_transcript(self, video_id, transcript):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''UPDATE videos SET transcript = ?, status = ? WHERE id = ?''',
                       (transcript, 'completed', video_id))
        conn.commit()
        conn.close()
    
    def get_video(self, video_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM videos WHERE id = ?', (video_id,))
        result = cursor.fetchone()
        conn.close()
        return result
