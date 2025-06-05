import os
from moviepy import ImageSequenceClip, ImageClip
from PIL import Image
from config import (
    INPUT_IMG_FOLDER,
    OUTPUT_VIDEO,
    FPS,
    DURATION_PER_IMAGE,
    SUPPORTED_IMAGE_FORMATS
)
from directory_watcher import DirectoryWatcher
import time
import sys

def resize_images(image_paths, target_size):
    """
    Resizes all images to the target size.

    Parameters:
    - image_paths: List of image file paths.
    - target_size: Tuple of (width, height) to resize images to.
    
    Returns:
    - List of paths to resized images.
    """
    resized_images = []
    for img_path in image_paths:
        try:
            with Image.open(img_path) as img:
                resized_img = img.resize(target_size, Image.LANCZOS)
                resized_path = os.path.join(os.path.dirname(img_path), "resized_" + os.path.basename(img_path))
                resized_img.save(resized_path)
                resized_images.append(resized_path)
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
        # Determine the target size (use the size of the first image)
        with Image.open(images[0]) as img:
            target_size = img.size

        # Resize images to the target size
        resized_images = resize_images(images, target_size)
        
        if not resized_images:
            print("\nNo images could be processed!")
            return False

        # Create a video clip from the resized image sequence
        clip = ImageSequenceClip(resized_images, fps=fps)

        # Adjust the duration if specified
        clip = clip.set_duration(duration_per_image * len(resized_images))

        # Write the video file
        clip.write_videofile(output_video, codec="libx264")
        return True
        
    except Exception as e:
        print(f"\nError creating video: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # Initialize the directory watcher
        watcher = DirectoryWatcher(INPUT_IMG_FOLDER, SUPPORTED_IMAGE_FORMATS)
        
        # Print initial directory information with duration
        watcher.print_directory_info(DURATION_PER_IMAGE)
        
        # Create initial video
        if not create_video_from_images(watcher, OUTPUT_VIDEO, FPS, DURATION_PER_IMAGE):
            print("\nInitial video creation failed. Please check the directory contents and try again.")
            sys.exit(1)
        
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
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)
