import os
from moviepy.editor import ImageSequenceClip, ImageClip
from PIL import Image

input_img_folder = 'C:\\Users\\shelt\\Pictures\\CAM\\482_1812'

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
        with Image.open(img_path) as img:
            resized_img = img.resize(target_size, Image.LANCZOS)
            resized_path = os.path.join(os.path.dirname(img_path), "resized_" + os.path.basename(img_path))
            resized_img.save(resized_path)
            resized_images.append(resized_path)
    
    return resized_images

def create_video_from_images(image_dir, output_video, fps=24, duration_per_image=2):
    """
    Creates a video from a sequence of images in a directory.

    Parameters:
    - image_dir: Path to the directory containing images.
    - output_video: Path to the output video file.
    - fps: Frames per second for the video.
    - duration_per_image: Duration each image should appear in the video.
    """
    # Get a sorted list of image file paths
    images = sorted([os.path.join(image_dir, img) for img in os.listdir(image_dir) if img.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.JPG'))])

    if not images:
        raise ValueError("No images found in the directory!")

    # Determine the target size (use the size of the first image)
    with Image.open(images[0]) as img:
        target_size = img.size

    # Resize images to the target size
    resized_images = resize_images(images, target_size)

    # Create a video clip from the resized image sequence
    clip = ImageSequenceClip(resized_images, fps=fps)

    # Adjust the duration if specified
    clip = clip.set_duration(duration_per_image * len(resized_images))

    # Write the video file
    clip.write_videofile(output_video, codec="libx264")

if __name__ == "__main__":
    image_dir = input_img_folder  # Use the input image folder
    output_video = "output_video.mp4"  # Replace with the desired output video file name
    fps = 1  # Frames per second
    duration_per_image = 1  # Duration each image will appear in the video (in seconds)

    create_video_from_images(image_dir, output_video, fps, duration_per_image)
