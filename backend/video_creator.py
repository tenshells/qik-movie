from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from typing import List

class VideoCreator:
    def __init__(self, duration_per_image: float):
        self.duration_per_image = duration_per_image

    def create_video(self, image_paths: List[str], output_path: str) -> bool:
        """
        Creates a video from a sequence of images.

        Parameters:
        - image_paths: List of paths to the images
        - output_path: Path where the video should be saved

        Returns:
        - bool: True if video creation was successful, False otherwise
        """
        try:
            # Create a video clip from the image sequence
            clip = ImageSequenceClip(
                image_paths,
                durations=[self.duration_per_image] * len(image_paths)
            )

            # Write the video file with specific parameters for better compatibility
            clip.write_videofile(
                output_path,
                codec='libx264',
                audio=False,
                preset='medium',
                threads=4,
                ffmpeg_params=['-pix_fmt', 'yuv420p']
            )
            
            return True
            
        except Exception as e:
            print(f"\nError creating video: {str(e)}")
            return False 