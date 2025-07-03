import os
from typing import List
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip

class MediaResizer:
    def __init__(self, target_width: int, target_height: int, duration: float):
        self.target_size = (target_width, target_height)
        self.duration = duration
        self.resized_folder = None

    def ensure_resized_folder(self, input_folder: str) -> str:
        """Create a folder for resized images if it doesn't exist."""
        self.resized_folder = os.path.join(os.path.dirname(input_folder), "resized_media")
        if os.path.exists(self.resized_folder):
            # Clear existing files in the folder
            for file in os.listdir(self.resized_folder):
                file_path = os.path.join(self.resized_folder, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Warning: Could not delete {file_path}: {str(e)}")
        else:
            os.makedirs(self.resized_folder)
        return self.resized_folder

    def resize_images(self, image_paths: List[str]) -> List[str]:
        """
        Resizes all images to the target size and saves them in a dedicated folder.

        Parameters:
        - image_paths: List of image file paths.
        
        Returns:
        - List of paths to resized images.
        """
        if not self.resized_folder:
            raise ValueError("Resized folder not initialized. Call ensure_resized_folder first.")
            
        resized_images = []
        
        for img_path in image_paths:
            try:
                with Image.open(img_path) as img:
                    # Convert to RGB if necessary (for PNG with transparency)
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        img = img.convert('RGB')
                    
                    # Resize image maintaining aspect ratio
                    img.thumbnail(self.target_size, Image.LANCZOS)
                    
                    # Create a new image with the target size and black background
                    new_img = Image.new('RGB', self.target_size, (0, 0, 0))
                    
                    # Calculate position to paste the resized image (centered)
                    paste_x = (self.target_size[0] - img.size[0]) // 2
                    paste_y = (self.target_size[1] - img.size[1]) // 2
                    
                    # Paste the resized image onto the new image
                    new_img.paste(img, (paste_x, paste_y))
                    
                    # Save to the resized folder
                    output_filename = f"resized_{os.path.basename(img_path)}"
                    output_path = os.path.join(self.resized_folder, output_filename)
                    new_img.save(output_path, quality=95)
                    resized_images.append(output_path)
                    
            except Exception as e:
                print(f"Warning: Could not process image {img_path}: {str(e)}")
        
        return resized_images 

    def resize_and_trim_videos(self, video_paths: List[str]) -> List[str]:
        resized_videos = []
        for vid_path in video_paths:
            try:
                clip = VideoFileClip(vid_path)
                # Resize and trim
                clip = clip.resized(new_size=self.target_size).subclipped(0, min(self.duration, clip.duration))
                output_filename = f"resized_{os.path.splitext(os.path.basename(vid_path))[0]}.mp4"
                output_path = os.path.join(self.resized_folder, output_filename)
                # Write the video file
                clip.write_videofile(
                    output_path,
                    codec='libx264',
                    audio=True if clip.audio else False,
                    preset='medium',
                    threads=4,
                    ffmpeg_params=['-pix_fmt', 'yuv420p'],
                    logger=None
                )
                resized_videos.append(output_path)
                clip.close()
            except Exception as e:
                print(f"Warning: Could not process video {vid_path}: {str(e)}")
        return resized_videos 