import sys
from config import (
    INPUT_IMG_FOLDER,
    OUTPUT_VIDEO,
    DURATION_PER_IMAGE,
    SUPPORTED_IMAGE_FORMATS,
    MAX_IMAGES,
    TARGET_WIDTH,
    TARGET_HEIGHT
)
from backend import FolderManager, ImageResizer, VideoCreator

def prompt_with_default(prompt, default, cast_func=str):
    user_input = input(f"{prompt} [{default}]: ").strip()
    if not user_input:
        return default
    try:
        return cast_func(user_input)
    except Exception:
        print(f"Invalid input. Using default: {default}")
        return default

def format_duration(seconds):
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.2f}s" if minutes else f"{secs:.2f}s"

def main():
    print("--- Qik Movie Video Creator ---\n")
    img_folder = prompt_with_default("Input image folder", INPUT_IMG_FOLDER, str)
    output_video = prompt_with_default("Output video file", OUTPUT_VIDEO, str)
    duration_per_image = prompt_with_default("Duration per image (seconds)", DURATION_PER_IMAGE, float)
    max_images = prompt_with_default("Maximum number of images", MAX_IMAGES, int)
    target_width = prompt_with_default("Target video width", TARGET_WIDTH, int)
    target_height = prompt_with_default("Target video height", TARGET_HEIGHT, int)

    # Show supported formats
    print(f"Supported image formats: {', '.join(SUPPORTED_IMAGE_FORMATS)}")

    # Initialize managers
    folder = FolderManager(img_folder, SUPPORTED_IMAGE_FORMATS, max_images)
    resizer = ImageResizer(target_width, target_height)
    video_creator = VideoCreator(duration_per_image)

    # Get images
    images = folder.get_image_files()
    if not images:
        print("No images found in the directory!")
        sys.exit(1)
    print(f"Found {len(images)} images.")

    # Resize images
    resizer.ensure_resized_folder(img_folder)
    resized_images = resizer.resize_images(images)
    if not resized_images:
        print("No images could be processed!")
        sys.exit(1)
    print(f"Resized {len(resized_images)} images.")

    # Create video
    if video_creator.create_video(resized_images, output_video):
        total_duration = len(resized_images) * duration_per_image
        print(f"\nVideo created successfully: {output_video}")
        print(f"Output duration: {format_duration(total_duration)}")
    else:
        print("\nVideo creation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
