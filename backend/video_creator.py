from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from typing import List, Optional
import os

class VideoCreator:
    def __init__(self, duration_per_image: float):
        self.duration_per_image = duration_per_image

    def create_video(self, image_paths: List[str], output_path: str, audio_path: Optional[str] = None) -> bool:
        """
        Creates a video from a sequence of images, with optional audio.

        Parameters:
        - image_paths: List of paths to the images
        - output_path: Path where the video should be saved
        - audio_path: Path to the audio file (optional)

        Returns:
        - bool: True if video creation was successful, False otherwise
        """
        try:
            # Create a video clip from the image sequence
            clip = ImageSequenceClip(
                image_paths,
                durations=[self.duration_per_image] * len(image_paths)
            )

            # Add audio if provided and file exists
            if audio_path and os.path.isfile(audio_path):
                audio = AudioFileClip(audio_path)
                # Loop or trim audio to match video duration
                if audio.duration < clip.duration:
                    n_loops = int(clip.duration // audio.duration) + 1
                    audio = audio.fx(lambda a: a.loop(n_loops)).subclipped(0, clip.duration)
                else:
                    audio = audio.subclipped(0, clip.duration)
                clip = clip.with_audio(audio)
            elif audio_path:
                print(f"Warning: Audio file not found at {audio_path}. Continuing without audio.")

            # Write the video file with specific parameters for better compatibility
            clip.write_videofile(
                output_path,
                codec='libx264',
                audio=True,
                preset='medium',
                threads=4,
                ffmpeg_params=['-pix_fmt', 'yuv420p']
            )
            
            return True
            
        except Exception as e:
            print(f"\nError creating video: {str(e)}")
            return False 