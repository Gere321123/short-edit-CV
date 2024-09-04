from google.cloud import speech
from google.oauth2 import service_account
import config
import os

class Transcriber:
    def __init__(self):
        credentials_path = config.Config.GOOGLE_CLOUD_CREDENTIALS
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Google Cloud credentials file not found at {credentials_path}")
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.client = speech.SpeechClient(credentials=credentials)
    
    def transcribe_long_audio(self, audio_path):
        with open(audio_path, 'rb') as audio_file:
            content = audio_file.read()
        
        audio = speech.RecognitionAudio(content=content)
        
        config_audio = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,  # Ensure this matches the sample rate of your mono audio
            language_code='en-US',
            enable_automatic_punctuation=True
        )
        
        operation = self.client.long_running_recognize(config=config_audio, audio=audio)
        response = operation.result(timeout=900)
        
        transcript = ''
        for result in response.results:
            transcript += result.alternatives[0].transcript + ' '
        
        transcript = transcript.strip()
        
        # Print the transcript to the console
        print(f"Transcript: {transcript}")
        
        return transcript



