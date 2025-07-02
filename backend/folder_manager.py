import os
from typing import List, Tuple

class FolderManager:
    def __init__(self, directory: str, supported_formats: Tuple[str, ...], max_images: int = 100):
        if not os.path.exists(directory):
            raise ValueError(f"Directory does not exist: {directory}")
        if not os.path.isdir(directory):
            raise ValueError(f"Path is not a directory: {directory}")
        self.directory = directory
        self.supported_formats = supported_formats
        self.max_images = max_images

    def get_image_files(self) -> List[str]:
        """Get sorted list of image files in the directory, limited to max_images."""
        try:
            files = []
            for img in os.listdir(self.directory):
                if img.lower().endswith(self.supported_formats):
                    filepath = os.path.join(self.directory, img)
                    if os.path.isfile(filepath):
                        files.append(filepath)
            files.sort()
            if len(files) > self.max_images:
                step = len(files) / self.max_images
                selected_indices = [int(i * step) for i in range(self.max_images)]
                files = [files[i] for i in selected_indices]
            return files
        except Exception as e:
            print(f"Error reading directory: {str(e)}")
            return [] 