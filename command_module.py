from api_module import APIClient
import datetime
import os
from datetime import timezone
import json

class CommandHandler:
    def __init__(self, ui):
        self.ui = ui
        self.api_client = APIClient()

    def execute(self, command):
        # Check for specific commands and handle them
        if command.lower() == "initiate log entry":
            self.initiate_log_entry()
        else:
            # If it's not a special command, assume it's a log entry input
            self.handle_log_entry_input(command)

    def initiate_log_entry(self):
        # Set up for log session
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        now = datetime.datetime.now(timezone.utc)
        iso_date_str_with_offset = now.strftime("%Y-%m-%dT%H-%M-%S%z")
        log_count = len([name for name in os.listdir(log_dir) if name.startswith(now.strftime("%Y-%m-%d"))]) + 1
        self.file_name = f"{iso_date_str_with_offset}-Log-entry-{log_count}.json"
        self.file_path = os.path.join(log_dir, self.file_name)

        # Initialize history
        history = [{"role": "system", "content": "System prompt"}]
        self.api_client.set_history(history)

        # Display system prompt and get initial response
        self.ui.display_message("System: System prompt")
        response = self.api_client.send_request("Hello, let's initiate a log entry.")
        self.ui.display_message(f"Assistant: {response}")

    def handle_log_entry_input(self, user_input):
        # Handle ongoing user inputs for the log session
        if user_input.lower() == 'end log':
            self.end_log_session()
            return

        response = self.api_client.send_request(user_input)
        self.ui.display_message(f"User: {user_input}")
        self.ui.display_message(f"Assistant: {response}")

    def end_log_session(self):
        # Save the conversation history
        updated_history = self.api_client.get_history()
        with open(self.file_path, "w") as file:
            json.dump(updated_history, file, indent=4)
        self.ui.save_log(self.file_path)
        # Optionally reset the UI for normal operation
