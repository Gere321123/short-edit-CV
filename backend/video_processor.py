from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import os
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

class VideoProcessor:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video = VideoFileClip(video_path)

    def add_text(self, text, position=('center', 'center'), font='Arial', font_size=70, color='white', duration=None):
        if duration is None:
            duration = self.video.duration

        text_clip = TextClip(text, fontsize=font_size, font=font, color=color).set_position(position).set_duration(duration)
        self.video = CompositeVideoClip([self.video, text_clip])

    def save_video(self, output_folder='uploads'):
        original_filename = os.path.basename(self.video_path)
        output_path = os.path.join(output_folder, original_filename)
        self.video.write_videofile(output_path, codec='libx264', audio_codec='aac')
        return output_path
