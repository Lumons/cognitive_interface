import tkinter as tk
from command_module import CommandHandler

class ApplicationUI:
    def __init__(self, root):
        self.root = root
        self.command_handler = CommandHandler(self)

        self.setup_ui()

    def setup_ui(self):
        self.text_area = tk.Text(self.root, state='disabled', height=15, width=50)
        self.text_area.pack()

        self.entry = tk.Entry(self.root)
        self.entry.pack()
        self.entry.bind("<Return>", self.execute_command)

        self.submit_button = tk.Button(self.root, text="Submit", command=self.execute_command)
        self.submit_button.pack()

    def execute_command(self, event=None):
        command = self.entry.get()
        self.command_handler.execute(command)
        self.entry.delete(0, tk.END)

    def display_message(self, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, f"{message}\n")
        self.text_area.config(state='disabled')

    def save_log(self, file_path):
        self.display_message(f"Log saved to {file_path}")

root = tk.Tk()
app = ApplicationUI(root)
root.mainloop()