import tkinter as tk
from command_module import CommandHandler
import datetime
import sounddevice as sd
import wavio
import threading
import whisper
import numpy as np
import os
from doc_explorer import SearchWindow


# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

class ApplicationUI:
    def __init__(self, root):
        self.root = root
        self.command_handler = CommandHandler(self)

        # Configure the grid
        self.root.grid_rowconfigure(0, weight=1)  # Make the text area row expandable
        self.root.grid_columnconfigure(0, weight=1)  # Make the text area column expandable

        self.setup_ui()

        # Add a button to open the summary window
        self.summary_window_button = tk.Button(self.root, text="Open Summary", command=self.open_summary_window)
        self.summary_window_button.grid(row=7, column=0, sticky="ew")  # Adjust row/column as needed

        # Variable to keep track of the summary window
        self.summary_window = None

        # Initialise the recording list
        self.myrecording = []  # Initialize myrecording as an empty list

    def open_summary_window(self):
        # Ensure the summary window is open
        if self.summary_window is None or not self.summary_window.winfo_exists():
            self.summary_window = tk.Toplevel(self.root)
            self.summary_window.title("Summary")

            # Create a text widget for displaying the summary
            self.summary_text_area = tk.Text(self.summary_window, height=15, width=50)
            self.summary_text_area.grid(row=0, column=0, sticky="nsew")

        else:
            # Bring the window to the front if it's already open
            self.summary_window.lift()

        # Generate and display the summary
        summary_data = self.command_handler.generate_summary()
        self.update_summary_display(summary_data)


    def update_summary_display(self, summary_data):
        if self.summary_window and self.summary_window.winfo_exists():
            self.summary_text_area.config(state='normal')
            self.summary_text_area.delete('1.0', tk.END)  # Clear existing text
            self.summary_text_area.insert(tk.END, summary_data)  # Insert new summary data
            self.summary_text_area.config(state='disabled')
        else:
            print("Summary window is not open.")

    def setup_ui(self):
        # Create a Text widget with a Scrollbar
        self.text_area = tk.Text(self.root, state='disabled', height=15, width=50)
        self.scrollbar = tk.Scrollbar(self.root, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=self.scrollbar.set)
        # Improve readability of the text area
        self.text_area.config(font=("Arial", 12), wrap=tk.WORD, bg="white", fg="black")

        # Place the Text widget and the Scrollbar in the grid
        self.text_area.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Entry field for user input
        self.entry = tk.Entry(self.root)
        self.entry.grid(row=1, column=0, sticky="ew", columnspan=2)
        self.entry.bind("<Return>", self.execute_command)
        self.entry.config(font=("Arial", 12))

        # Submit button for sending commands
        self.submit_button = tk.Button(self.root, text="Submit", command=self.execute_command)
        self.submit_button.grid(row=2, column=0, sticky="ew")

        # Buttons for recording audio
        self.start_rec_button = tk.Button(self.root, text="Start Recording", command=self.start_recording)
        self.start_rec_button.grid(row=4, column=0)
        self.stop_rec_button = tk.Button(self.root, text="Stop Recording", command=self.stop_recording)
        self.stop_rec_button.grid(row=5, column=0)

       # Fetch .txt file names from a specific directory
        file_path = os.path.join(current_dir, "prompt_library")        
        txt_files = [f for f in os.listdir(file_path) if f.endswith('.txt')]

        # Dropdown for system prompts
        self.prompt_selector_var = tk.StringVar(self.root)
        self.prompt_dropdown = tk.OptionMenu(self.root, self.prompt_selector_var, *txt_files)
        self.prompt_dropdown.grid(row=3, column=1, sticky="ew")
        
        # Toggle switch for Whisper models
        self.model_options = tk.StringVar(value="medium")
        self.model_toggle = tk.OptionMenu(self.root, self.model_options, "base","small", "medium", "large")
        self.model_toggle.grid(row=4, column=1, sticky="ew")
       
        # Button to open search window
        self.search_window_button = tk.Button(self.root, text="Open Search Window", command=self.open_search_window)
        self.search_window_button.grid(row=6, column=0, sticky="ew")

    def ensure_directory_exists(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def open_search_window(self):
        # This method creates a new SearchWindow instance
        search_window = tk.Toplevel(self.root)
        SearchWindow(search_window)

    def transcribe_audio(self, audio_path):
        selected_model_size = self.model_options.get()  # Get the selected model size
        model = whisper.load_model(selected_model_size)  # Load the model based on the selection
        result = model.transcribe(audio_path)
        transcription = result["text"]
        return transcription

    def start_recording(self):
        self.recording = True
        self.record_thread = threading.Thread(target=self.record_audio)
        self.record_thread.start()

    def record_audio(self):
        fs = 44100  # Sample rate
        self.myrecording = []
        with sd.InputStream(samplerate=fs, channels=2) as stream:
            while self.recording:
                data, _ = stream.read(1024)  # Read chunks of 1024 frames
                self.myrecording.append(data)

    def stop_recording(self):
        self.recording = False
        self.record_thread.join()

        if not self.myrecording:
            print("No audio was recorded.")
            return
         
        # Convert the list of numpy arrays into a single numpy array
        recorded_audio = np.concatenate(self.myrecording, axis=0)
        self.myrecording = []  # Reset myrecording for the next recording

        # Define the directory and file name
        audio_file_path = self.get_audio_file_path()

        # Save the recording with a timestamp
        wavio.write(audio_file_path, recorded_audio, 44100, sampwidth=2)

        # Transcribe the audio
        transcription = self.transcribe_audio(audio_file_path)

        # Place the transcription in the entry field for editing
        self.entry.delete(0, tk.END)  # Clear any existing text in the entry field
        self.entry.insert(0, transcription)  # Insert the transcription

        # Optionally, delete the audio file if not needed
        # os.remove(audio_file_path)

    def get_audio_file_path(self):
        logs_dir = os.path.join(current_dir, "logs", "audio")
        self.ensure_directory_exists(logs_dir)  # Ensure the directory exists
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(logs_dir, f"audio_log_{timestamp}.wav")

    def execute_command(self, event=None):
        command = self.entry.get()
        self.command_handler.execute(command)
        self.entry.delete(0, tk.END)

    def display_message(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, formatted_message)
        self.text_area.config(state='disabled')

    def save_log(self, file_path):
        self.display_message(f"Log saved to {file_path}")

root = tk.Tk()
app = ApplicationUI(root)
root.mainloop()