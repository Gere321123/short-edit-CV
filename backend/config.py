import os

class Config:
    UPLOAD_FOLDER = 'uploads'
    AUDIO_FOLDER = 'audios'
    DATABASE = 'videos.db'
    GOOGLE_CLOUD_CREDENTIALS = 'credentials.json'
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(AUDIO_FOLDER, exist_ok=True)
