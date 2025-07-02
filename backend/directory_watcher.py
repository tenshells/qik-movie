import os
import hashlib
from typing import List, Dict, Set, Tuple
import time
from collections import Counter
import random

class DirectoryWatcher:
    def __init__(self, directory: str, supported_formats: Tuple[str, ...], max_images: int = 100):
        if not os.path.exists(directory):
            raise ValueError(f"Directory does not exist: {directory}")
        if not os.path.isdir(directory):
            raise ValueError(f"Path is not a directory: {directory}")
            
        self.directory = directory
        self.supported_formats = supported_formats
        self.max_images = max_images
        self._cache: Dict[str, str] = {}  # filename -> hash
        self._last_check_time = 0
        self._last_modified_time = 0
        
        # Validate that we can read the directory
        try:
            os.listdir(directory)
        except PermissionError:
            raise PermissionError(f"No permission to read directory: {directory}")

    def _get_file_hash(self, filepath: str) -> str:
        """Calculate MD5 hash of a file."""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, PermissionError) as e:
            print(f"Warning: Could not read file {filepath}: {str(e)}")
            return ""

    def _get_directory_state(self) -> Dict[str, str]:
        """Get current state of directory with file hashes."""
        state = {}
        try:
            for filename in os.listdir(self.directory):
                if filename.lower().endswith(self.supported_formats):
                    filepath = os.path.join(self.directory, filename)
                    if os.path.isfile(filepath):  # Only process files, not directories
                        state[filename] = self._get_file_hash(filepath)
        except Exception as e:
            print(f"Warning: Error reading directory: {str(e)}")
        return state

    def check_for_changes(self) -> Tuple[bool, List[str]]:
        """
        Check for changes in the directory.
        Returns: (has_changes, list_of_changed_files)
        """
        current_time = time.time()
        # Only check every 5 seconds to avoid excessive disk I/O
        if current_time - self._last_check_time < 5:
            return False, []

        self._last_check_time = current_time
        current_state = self._get_directory_state()
        changed_files = []

        # Check for modified or new files
        for filename, current_hash in current_state.items():
            if filename not in self._cache or self._cache[filename] != current_hash:
                changed_files.append(filename)

        # Check for deleted files
        for filename in self._cache:
            if filename not in current_state:
                changed_files.append(f"{filename} (deleted)")

        if changed_files:
            print("\nChanges detected in directory:")
            for file in changed_files:
                print(f"- {file}")
            print()  # Add a blank line for better readability

        # Update cache
        self._cache = current_state
        return len(changed_files) > 0, changed_files

    def get_image_files(self) -> List[str]:
        """Get sorted list of image files in the directory, limited to max_images."""
        try:
            files = []
            for img in os.listdir(self.directory):
                if img.lower().endswith(self.supported_formats):
                    filepath = os.path.join(self.directory, img)
                    if os.path.isfile(filepath):  # Only include files, not directories
                        files.append(filepath)
            
            # Sort files by name
            files.sort()
            
            # If we have more files than the limit, select a subset
            if len(files) > self.max_images:
                # Calculate step size to evenly distribute selection
                step = len(files) / self.max_images
                selected_indices = [int(i * step) for i in range(self.max_images)]
                files = [files[i] for i in selected_indices]
            
            return files
        except Exception as e:
            print(f"Error reading directory: {str(e)}")
            return []

    def get_file_counts_by_format(self) -> Dict[str, int]:
        """Get count of files by format."""
        files = self.get_image_files()
        format_counts = Counter()
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            format_counts[ext] += 1
        return dict(format_counts)

    def print_directory_info(self, duration_per_image: float = 1.0):
        """Print information about the watched directory and video duration."""
        print(f"\nWatching directory: {self.directory}")
        print(f"Supported formats: {', '.join(self.supported_formats)}")
        
        # Get all files first to show total counts
        all_files = []
        for img in os.listdir(self.directory):
            if img.lower().endswith(self.supported_formats):
                filepath = os.path.join(self.directory, img)
                if os.path.isfile(filepath):
                    all_files.append(filepath)
        
        if not all_files:
            print("\nNo supported image files found in the directory!")
            print("Please add some image files with the following extensions:")
            for ext in self.supported_formats:
                print(f"- {ext}")
        else:
            # Count all files by format
            all_format_counts = Counter()
            for file in all_files:
                ext = os.path.splitext(file)[1].lower()
                all_format_counts[ext] += 1
            
            # Get selected files
            selected_files = self.get_image_files()
            selected_format_counts = self.get_file_counts_by_format()
            
            print(f"\nFound {len(all_files)} total image files:")
            for ext, count in sorted(all_format_counts.items()):
                print(f"- {ext}: {count} files")
            
            if len(all_files) > self.max_images:
                print(f"\nSelecting {len(selected_files)} images (maximum limit: {self.max_images})")
                print("Selected files by format:")
                for ext, count in sorted(selected_format_counts.items()):
                    print(f"- {ext}: {count} files")
            
            # Calculate and display video duration
            total_duration = len(selected_files) * duration_per_image
            minutes = int(total_duration // 60)
            seconds = int(total_duration % 60)
            print(f"\nVideo will be {minutes} minutes and {seconds} seconds long")
            print(f"(Each image will be shown for {duration_per_image} seconds)")
        print() 