import os
import shutil
import requests
from tkinter import filedialog, Tk, Label
from PIL import Image, ImageTk
from termcolor import colored

# Define file type categories
file_types = {
    'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.csv'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    'Videos': ['.mp4', '.mkv', '.avi', '.mov'],
    'Audio': ['.mp3', '.wav', '.aac', '.flac'],
    'Scripts': ['.py', '.js', '.html', '.css'],
    'Archives': ['.zip', '.tar', '.rar', '.7z'],
    'Others': []
}

def get_category(file_extension):
    """Return category based on file extension."""
    for category, extensions in file_types.items():
        if file_extension in extensions:
            return category
    return 'Others'

def organize_files(directory, gif_path=None):
    """Organize files by category into folders based on file extension."""
    if not os.path.exists(directory):
        print(colored("The specified directory does not exist.", 'red'))
        return

    os.chdir(directory)
    files = [f for f in os.listdir() if os.path.isfile(f)]
    
    # Create categories folders if they do not exist
    for category in file_types.keys():
        category_folder = os.path.join(directory, category)
        if not os.path.exists(category_folder):
            os.makedirs(category_folder)
    
    # Move files into the appropriate folder
    for file in files:
        file_extension = os.path.splitext(file)[-1].lower()
        category = get_category(file_extension)
        
        source = os.path.join(directory, file)
        destination = os.path.join(directory, category, file)
        
        shutil.move(source, destination)
        print(colored(f"Moved '{file}' to '{category}/'", 'green'))
    
    print(colored("\nFiles have been successfully organized!", 'blue'))
    
    if gif_path:
        gif_label.config(image=gif_image)
        window.update_idletasks()

def browse_directory():
    """Open a file dialog to select the directory."""
    root = Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory(title="Select Folder to Organize")
    return folder_selected

def download_gif(gif_url):
    """Download the GIF from the provided URL."""
    response = requests.get(gif_url)
    gif_path = "loading.gif"
    with open(gif_path, 'wb') as f:
        f.write(response.content)
    return gif_path

if __name__ == '__main__':
    # Create a window with tkinter to display the GIF
    window = Tk()
    window.title("File Organizer")
    
    # Set window size and make it non-resizable
    window.geometry("300x300")
    window.resizable(False, False)
    
    # Add a label to show the GIF
    gif_label = Label(window)
    gif_label.pack()

    # URL of the GIF you want to display
    gif_url = "https://your-gif-url-here.gif"  # Replace with your actual GIF URL
    gif_path = download_gif(gif_url)

    # Load the GIF using Pillow
    gif_image = Image.open(gif_path)
    gif_image = ImageTk.PhotoImage(gif_image)

    # Start the window in a separate thread to show the GIF
    window.after(1000, lambda: window.deiconify())  # Show window after 1 second
    
    print(colored("Welcome to the Modern File Organizer!", 'cyan'))
    print(colored("This tool helps you organize your files into categories.", 'cyan'))
    
    directory = browse_directory()  # Allow the user to select a folder
    if directory:
        organize_files(directory, gif_path)
    else:
        print(colored("No folder selected. Exiting...", 'red'))
    
    window.mainloop()  # Keep the GUI window running
