import sys
import os
from config import (
    INPUT_IMG_FOLDER,
    OUTPUT_VIDEO,
    AUDIO_PATH,
    DURATION_PER_IMAGE,
    SUPPORTED_IMAGE_FORMATS,
    SUPPORTED_VIDEO_FORMATS,
    MAX_IMAGES,
    MAX_VIDEOS,
    TARGET_WIDTH,
    TARGET_HEIGHT,
)
from backend import FolderManager, MediaResizer, VideoCreator


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
    img_folder = prompt_with_default("Input image/video folder", INPUT_IMG_FOLDER, str)
    output_video = prompt_with_default("Output video file", OUTPUT_VIDEO, str)
    audio_path = prompt_with_default("Audio file path (mp3/wav)", AUDIO_PATH, str)
    duration_per_media = prompt_with_default(
        "Duration per image/video (seconds)", DURATION_PER_IMAGE, float
    )
    max_images = prompt_with_default("Maximum number of images", MAX_IMAGES, int)
    max_videos = prompt_with_default("Maximum number of videos", MAX_VIDEOS, int)
    target_width = prompt_with_default("Target video width", TARGET_WIDTH, int)
    target_height = prompt_with_default("Target video height", TARGET_HEIGHT, int)

    print(f"Supported image formats: {', '.join(SUPPORTED_IMAGE_FORMATS)}")
    print(f"Supported video formats: {', '.join(SUPPORTED_VIDEO_FORMATS)}")

    folder = FolderManager(
        img_folder,
        SUPPORTED_IMAGE_FORMATS,
        max_images,
        SUPPORTED_VIDEO_FORMATS,
        max_videos,
    )
    resizer = MediaResizer(target_width, target_height, duration_per_media)
    video_creator = VideoCreator(duration_per_media)

    # Get images and videos
    images, videos = folder.get_media_files()
    if not images and not videos:
        print("No images or videos found in the directory!")
        sys.exit(1)
    print(f"Found {len(images)} images and {len(videos)} videos.")

    # Resize images and videos
    resizer.ensure_resized_folder(img_folder)
    resized_images = resizer.resize_images(images)
    resized_videos = resizer.resize_and_trim_videos(videos)
    if not resized_images and not resized_videos:
        print("No media could be processed!")
        sys.exit(1)
    print(f"Resized {len(resized_images)} images and {len(resized_videos)} videos.")

    # Mix images and videos in original folder order
    all_files = images + videos
    all_resized = {
        **{img: rimg for img, rimg in zip(images, resized_images)},
        **{vid: rvid for vid, rvid in zip(videos, resized_videos)},
    }
    mixed_media = [
        all_resized[f]
        for f in sorted(
            all_files, key=lambda x: os.listdir(img_folder).index(os.path.basename(x))
        )
        if f in all_resized
    ]

    # Create video
    if video_creator.create_video(mixed_media, output_video, audio_path=audio_path):
        total_duration = len(mixed_media) * duration_per_media
        print(f"\nVideo created successfully: {output_video}")
        print(f"Output duration: {format_duration(total_duration)}")
    else:
        print("\nVideo creation failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
