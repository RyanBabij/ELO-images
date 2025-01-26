import os
import random
import math
import json
import time  # For tracking the last usage time
import argparse  # For parsing command-line arguments
from tkinter import Tk, Label, Frame
from PIL import Image, ImageTk

class ImageEloRanking:
    def __init__(self, directory, save_file="elo_image_results.json", base_rating=1000, window_width=None, window_height=None):
        self.directory = directory
        self.save_file = save_file
        self.base_rating = base_rating  # Set the base ELO rating
        self.image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        self.image_files.sort()  # Optional: Sort files alphabetically
        
        # Initialize comparison counter
        self.comparison_count = 0

        # Load or initialize ELO ratings, history, and last usage times
        self.elo_ratings = self.load_ratings()
        self.history = self.load_history()
        self.last_used = self.load_last_used()

        # Set up the Tkinter window
        self.root = Tk()
        self.root.title("Image ELO Ranking")

        # Use passed window dimensions or calculate based on screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Use the provided dimensions or fallback to defaults
        self.window_width = window_width if window_width else int(screen_width * 0.66)
        self.window_height = window_height if window_height else int(screen_height * 0.75)
        self.root.geometry(f"{self.window_width}x{self.window_height}")

        # Create a frame for two images
        self.frame = Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.left_label = Label(self.frame)
        self.left_label.pack(side="left", fill="both", expand=True)

        self.right_label = Label(self.frame)
        self.right_label.pack(side="right", fill="both", expand=True)

        # Create a label at the bottom for instructions
        self.instruction_label = Label(self.root, text="Left arrow for left image, right arrow for right image", font=("Helvetica", 10))
        self.instruction_label.pack(side="bottom", fill="x", pady=10)

        # Start with the next pair of images in history, or pick images based on usage
        if self.history:
            self.left_image, self.right_image = self.history[-1]  # Last pair in history
        else:
            self.pick_new_images()

        # Initialize cached images
        self.cached_left_image = None
        self.cached_right_image = None

        # Display the initial images
        self.show_images()

        # Bind arrow keys for voting
        self.root.bind("<Left>", self.left_preferred)   # Left arrow key
        self.root.bind("<Right>", self.right_preferred)  # Right arrow key

        # Bind window resize event to print "resize"
        self.root.bind("<Configure>", self.on_resize)
        
        self.root.bind("<Escape>", self.close_application)

        # Start the Tkinter event loop
        self.root.mainloop()

    def show_images(self):
        left_path = os.path.join(self.directory, self.left_image)
        right_path = os.path.join(self.directory, self.right_image)

        left_image = Image.open(left_path)
        right_image = Image.open(right_path)

        # Update frame to get valid dimensions
        self.frame.update_idletasks()

        # Only resize if the cached image doesn't exist
        self.cached_left_image = self.resize_image_to_fit(left_image)
        self.cached_right_image = self.resize_image_to_fit(right_image)

        self.left_tk_image = ImageTk.PhotoImage(self.cached_left_image)
        self.right_tk_image = ImageTk.PhotoImage(self.cached_right_image)

        self.left_label.config(image=self.left_tk_image)
        self.right_label.config(image=self.right_tk_image)

    def resize_image_to_fit(self, image):
        """Resize the image to fit within the available space while preserving aspect ratio."""
        frame_width = (self.frame.winfo_width() // 2) - 20  # Half of the screen width for each image
        frame_height = self.frame.winfo_height() - 20

        # Get current image dimensions
        img_width, img_height = image.size

        # Calculate scaling factors for width and height
        width_factor = frame_width / img_width
        height_factor = frame_height / img_height

        # Use the smaller of the two scaling factors to preserve aspect ratio
        scale_factor = min(width_factor, height_factor)

        # Calculate the new size
        new_width = int(img_width * scale_factor)
        new_height = int(img_height * scale_factor)

        # Ensure new size is valid
        if new_width <= 0 or new_height <= 0:
            new_width, new_height = img_width, img_height  # Fallback to original size

        # Resize the image
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def calculate_elo(self, rating_a, rating_b, outcome):
        """Update ELO ratings for two items."""
        k = 32  # K-factor
        expected_a = 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))
        new_rating_a = rating_a + k * (outcome - expected_a)

        # Round the new rating to the nearest whole number
        return round(new_rating_a)

    def update_ratings(self, winner, loser):
        winner_rating = self.elo_ratings.get(winner, self.base_rating)  # Use base rating if no rating is found
        loser_rating = self.elo_ratings.get(loser, self.base_rating)

        # Update winner and loser ratings
        self.elo_ratings[winner] = self.calculate_elo(winner_rating, loser_rating, 1)
        self.elo_ratings[loser] = self.calculate_elo(loser_rating, winner_rating, 0)

    def left_preferred(self, event=None):
        """Handle left-arrow key press: left image is preferred."""
        self.update_ratings(self.left_image, self.right_image)
        self.history.append((self.left_image, self.right_image))
        self.update_last_used(self.left_image)
        self.update_last_used(self.right_image)
        self.pick_new_images()

    def right_preferred(self, event=None):
        """Handle right-arrow key press: right image is preferred."""
        self.update_ratings(self.right_image, self.left_image)
        self.history.append((self.left_image, self.right_image))
        self.update_last_used(self.left_image)
        self.update_last_used(self.right_image)
        self.pick_new_images()

    def update_last_used(self, image):
        """Update the last used time for the given image."""
        self.last_used[image] = time.time()  # Store the current time as the last used timestamp

    def pick_new_images(self):
        """Pick the image that hasn't been picked for the longest time and then pick a random image to compare it against."""
        # Sort images by their last used time (least recent first)
        sorted_images = sorted(self.image_files, key=lambda img: self.last_used.get(img, 0))
        
        # Pick the image that hasn't been used for the longest time
        left_image = sorted_images[0]
        
        # Randomly pick another image for comparison, ensuring it's not the same as the left image
        remaining_images = [img for img in sorted_images if img != left_image]
        right_image = random.choice(remaining_images)
        
        # Set the left and right images
        self.left_image, self.right_image = left_image, right_image
        
        # Reset cached images
        self.cached_left_image = None
        self.cached_right_image = None

        self.show_images()

        # Increment comparison count
        self.comparison_count += 1
        
        # Display the number of comparisons made so far
        print(f"\nCurrent comparison #: {self.comparison_count}")
        
        # Optional: Print current ratings for debugging
        print("\nCurrent ELO Ratings:")
        for image, rating in sorted(self.elo_ratings.items(), key=lambda x: -x[1]):
            print(f"{image}: {rating}")

        # Save the updated ratings, history, and last usage times
        self.save_ratings()


    def save_ratings(self):
        """Save the ELO ratings, history, and last usage times to a JSON file.""" 
        # Sort the ratings by ELO in descending order
        sorted_elo_ratings = dict(sorted(self.elo_ratings.items(), key=lambda x: -x[1]))

        data = {
            "elo_ratings": sorted_elo_ratings,
            "history": self.history,
            "last_used": self.last_used
        }
        with open(self.save_file, 'w') as f:
            json.dump(data, f, indent=4)

    def load_ratings(self):
        """Load the ELO ratings from a JSON file."""
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                return data.get("elo_ratings", {})
        return {file: self.base_rating for file in self.image_files}  # Initialize with base_rating if no file exists

    def load_history(self):
        """Load the history of image comparisons from a JSON file.""" 
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                return data.get("history", [])
        return []

    def load_last_used(self):
        """Load the last usage times for the images from a JSON file.""" 
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                return data.get("last_used", {file: 0 for file in self.image_files})
        return {file: 0 for file in self.image_files}  # Initialize with 0 for all images

    def on_resize(self, event):
        """Print 'resize' when the window is resized.""" 
        # print("resize")
        self.cached_left_image = None
        self.cached_right_image = None
        self.show_images()
            
    def close_application(self, event=None):
        """Close the Tkinter application."""
        self.root.destroy()


# Command-line argument parsing
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image ELO Ranking Viewer")
    parser.add_argument("image_directory", type=str, help="Directory containing the images")
    parser.add_argument("--base_rating", type=int, default=1000, help="Base ELO rating for images")
    parser.add_argument("--window_width", type=int, default=None, help="Width of the window in pixels")
    parser.add_argument("--window_height", type=int, default=None, help="Height of the window in pixels")

    args = parser.parse_args()

    # Initialize the ImageEloRanking class with provided arguments
    ranking = ImageEloRanking(
        args.image_directory,
        base_rating=args.base_rating,
        window_width=args.window_width,
        window_height=args.window_height
    )
