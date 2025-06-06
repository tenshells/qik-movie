import os
from moviepy import ImageSequenceClip, ImageClip
from PIL import Image
from config import (
    INPUT_IMG_FOLDER,
    OUTPUT_VIDEO,
    FPS,
    DURATION_PER_IMAGE,
    SUPPORTED_IMAGE_FORMATS,
    MAX_IMAGES,
    TARGET_WIDTH,
    TARGET_HEIGHT,
    WATCH_DIRECTORY
)
from directory_watcher import DirectoryWatcher
import time
import sys
import shutil

def ensure_resized_folder():
    """Create a folder for resized images if it doesn't exist."""
    resized_folder = os.path.join(os.path.dirname(INPUT_IMG_FOLDER), "resized_images")
    if os.path.exists(resized_folder):
        # Clear existing files in the folder
        for file in os.listdir(resized_folder):
            file_path = os.path.join(resized_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Warning: Could not delete {file_path}: {str(e)}")
    else:
        os.makedirs(resized_folder)
    return resized_folder

def resize_images(image_paths, target_size):
    """
    Resizes all images to the target size and saves them in a dedicated folder.

    Parameters:
    - image_paths: List of image file paths.
    - target_size: Tuple of (width, height) to resize images to.
    
    Returns:
    - List of paths to resized images.
    """
    resized_folder = ensure_resized_folder()
    resized_images = []
    
    for img_path in image_paths:
        try:
            with Image.open(img_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    img = img.convert('RGB')
                
                # Resize image maintaining aspect ratio
                img.thumbnail(target_size, Image.LANCZOS)
                
                # Create a new image with the target size and black background
                new_img = Image.new('RGB', target_size, (0, 0, 0))
                
                # Calculate position to paste the resized image (centered)
                paste_x = (target_size[0] - img.size[0]) // 2
                paste_y = (target_size[1] - img.size[1]) // 2
                
                # Paste the resized image onto the new image
                new_img.paste(img, (paste_x, paste_y))
                
                # Save to the resized folder
                output_filename = f"resized_{os.path.basename(img_path)}"
                output_path = os.path.join(resized_folder, output_filename)
                new_img.save(output_path, quality=95)
                resized_images.append(output_path)
                
        except Exception as e:
            print(f"Warning: Could not process image {img_path}: {str(e)}")
    
    return resized_images

def create_video_from_images(directory_watcher: DirectoryWatcher, output_video: str, fps: int = 24, duration_per_image: int = 2):
    """
    Creates a video from a sequence of images in a directory.

    Parameters:
    - directory_watcher: DirectoryWatcher instance to monitor the image directory
    - output_video: Path to the output video file
    - fps: Frames per second for the video
    - duration_per_image: Duration each image should appear in the video
    """
    # Get the current list of images
    images = directory_watcher.get_image_files()

    if not images:
        print("\nNo images found in the directory!")
        print("Please add some image files and try again.")
        return False

    try:
        # Use fixed dimensions from config
        target_size = (TARGET_WIDTH, TARGET_HEIGHT)

        # Resize images to the target size
        resized_images = resize_images(images, target_size)
        
        if not resized_images:
            print("\nNo images could be processed!")
            return False

        # Create a video clip from the resized image sequence with specified duration
        clip = ImageSequenceClip(resized_images, fps=fps, durations=[duration_per_image] * len(resized_images))

        # Write the video file with specific parameters for better compatibility
        clip.write_videofile(
            output_video,
            codec='libx264',
            audio=False,
            fps=fps,
            preset='medium',
            threads=4,
            ffmpeg_params=['-pix_fmt', 'yuv420p']
        )
        
        return True
        
    except Exception as e:
        print(f"\nError creating video: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # Initialize the directory watcher with maximum image limit
        watcher = DirectoryWatcher(INPUT_IMG_FOLDER, SUPPORTED_IMAGE_FORMATS, MAX_IMAGES)
        
        # Print initial directory information with duration
        watcher.print_directory_info(DURATION_PER_IMAGE)
        
        # Create initial video
        if not create_video_from_images(watcher, OUTPUT_VIDEO, FPS, DURATION_PER_IMAGE):
            print("\nInitial video creation failed. Please check the directory contents and try again.")
            sys.exit(1)
        
        # Only continue watching if enabled in config
        if WATCH_DIRECTORY:
            print("\nWatching for changes...")
            print("Press Ctrl+C to exit")
            
            while True:
                # Check for changes every 5 seconds
                has_changes, _ = watcher.check_for_changes()
                
                if has_changes:
                    print("Regenerating video due to changes...")
                    if create_video_from_images(watcher, OUTPUT_VIDEO, FPS, DURATION_PER_IMAGE):
                        print("Video regeneration complete!")
                    else:
                        print("Video regeneration failed!")
                
                time.sleep(5)  # Wait 5 seconds before next check
        else:
            print("\nVideo creation complete!")
            print(f"Output saved to: {OUTPUT_VIDEO}")
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
