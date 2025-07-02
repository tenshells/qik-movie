import sys
import time
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
from backend import DirectoryWatcher, ImageResizer, VideoCreator

def main():
    try:
        # Initialize components
        watcher = DirectoryWatcher(INPUT_IMG_FOLDER, SUPPORTED_IMAGE_FORMATS, MAX_IMAGES)
        resizer = ImageResizer(TARGET_WIDTH, TARGET_HEIGHT)
        video_creator = VideoCreator(FPS, DURATION_PER_IMAGE)
        
        # Print initial directory information
        watcher.print_directory_info(DURATION_PER_IMAGE)
        
        # Get images and process them
        images = watcher.get_image_files()
        if not images:
            print("\nNo images found in the directory!")
            print("Please add some image files and try again.")
            return False
            
        # Ensure resized folder exists and resize images
        resizer.ensure_resized_folder(INPUT_IMG_FOLDER)
        resized_images = resizer.resize_images(images)
        
        if not resized_images:
            print("\nNo images could be processed!")
            return False
            
        # Create the video
        if not video_creator.create_video(resized_images, OUTPUT_VIDEO):
            print("\nVideo creation failed. Please check the directory contents and try again.")
            return False
            
        # Watch for changes if enabled
        if WATCH_DIRECTORY:
            print("\nWatching for changes...")
            print("Press Ctrl+C to exit")
            
            while True:
                has_changes, _ = watcher.check_for_changes()
                
                if has_changes:
                    print("Regenerating video due to changes...")
                    images = watcher.get_image_files()
                    resized_images = resizer.resize_images(images)
                    
                    if resized_images and video_creator.create_video(resized_images, OUTPUT_VIDEO):
                        print("Video regeneration complete!")
                    else:
                        print("Video regeneration failed!")
                
                time.sleep(5)
        else:
            print("\nVideo creation complete!")
            print(f"Output saved to: {OUTPUT_VIDEO}")
            
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
