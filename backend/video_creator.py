from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy import concatenate_videoclips
from typing import List, Optional
import os

class VideoCreator:
    def __init__(self, duration_per_media: float):
        self.duration_per_media = duration_per_media

    def create_video(self, media_paths: List[str], output_path: str, audio_path: Optional[str] = None) -> bool:
        """
        Creates a video from a sequence of images and videos, with optional audio.

        Parameters:
        - media_paths: List of paths to images and videos
        - output_path: Path where the video should be saved
        - audio_path: Path to the audio file (optional)

        Returns:
        - bool: True if video creation was successful, False otherwise
        """
        print("creating video")
        try:
            clips = []
            for path in media_paths:
                ext = os.path.splitext(path)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.JPG']:
                    clip = ImageClip(path, duration=self.duration_per_media)
                    clips.append(clip)
                elif ext in ['.mp4', '.mov', '.avi', '.mkv']:
                    clip = VideoFileClip(path)
                    # Ensure the video is exactly the right duration (should already be trimmed, but just in case)
                    if clip.duration > self.duration_per_media:
                        clip = clip.subclipped(0, self.duration_per_media)
                    clips.append(clip)
                else:
                    print(f"Warning: Unsupported file type for {path}, skipping.")
            if not clips:
                print("No valid media to create video.")
                return False
            final_clip = concatenate_videoclips(clips, method="chain")

            # Add audio if provided and file exists
            if audio_path and os.path.isfile(audio_path):
                audio = AudioFileClip(audio_path)
                if audio.duration < final_clip.duration:
                    n_loops = int(final_clip.duration // audio.duration) + 1
                    audio = audio.fx(lambda a: a.loop(n_loops)).subclipped(0, final_clip.duration)
                else:
                    audio = audio.subclipped(0, final_clip.duration)
                final_clip = final_clip.with_audio(audio)
            elif audio_path:
                print(f"Warning: Audio file not found at {audio_path}. Continuing without audio.")

            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio=True,
                preset='medium',
                threads=4,
                ffmpeg_params=['-pix_fmt', 'yuv420p']
            )
            final_clip.close()
            for c in clips:
                c.close()
            return True
        except Exception as e:
            print(f"\nError creating video: {str(e)}")
            return False 