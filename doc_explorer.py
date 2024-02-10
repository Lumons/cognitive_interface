
from log_indexer import search_index 
import tkinter as tk
from tkinter import ttk
import os

class SearchWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Search Logs")

        self.setup_ui()

    def setup_ui(self):
        # Text box for search input
        self.search_box = tk.Entry(self.master)
        self.search_box.pack()

        # Button to initiate search
        self.search_button = tk.Button(self.master, text="Search", command=self.perform_search)
        self.search_button.pack()

        # Dropdown to select the log file index
        self.log_file_var = tk.StringVar(self.master)
        self.log_file_dropdown = self.create_log_file_dropdown()
        self.log_file_dropdown.pack()
  
        # Creation of the Treeview widget for displaying search results
        self.results_table = ttk.Treeview(self.master)
        self.setup_results_table()  # Call the method to set up the results table
        # Create a Text widget to act as a console
        self.console = tk.Text(self.master, height=10, state='disabled')
        self.console.pack()
 
        # Disable editing of the console
        self.console.config(state='disabled')
    def create_log_file_dropdown(self):
        # Assuming logs are stored in a directory named 'logs'
        log_files = self.get_log_files()
        return tk.OptionMenu(self.master, self.log_file_var, *log_files)

    def get_log_files(self):
        log_dir = "logs"  # Update this path
        return [f for f in os.listdir(log_dir) if os.path.isfile(os.path.join(log_dir, f))]

    def setup_results_table(self):
        self.results_table['columns'] = ("File Name", "Role", "Content")
        self.results_table.column("#0", width=0, stretch=tk.NO)
        self.results_table.column("File Name", anchor=tk.W, width=120)
        self.results_table.column("Role", anchor=tk.CENTER, width=100)
        self.results_table.column("Content", anchor=tk.CENTER, width=300)

        self.results_table.heading("#0", text="", anchor=tk.W)
        self.results_table.heading("File Name", text="File Name", anchor=tk.W)
        self.results_table.heading("Role", text="Role", anchor=tk.CENTER)
        self.results_table.heading("Content", text="Content", anchor=tk.CENTER)

        self.results_table.pack()
        
        # Bind the sorting function to column headings
        for col in self.results_table['columns']:
            self.results_table.heading(col, text=col,
                command=lambda _col=col: self.treeview_sort_column(self.results_table, _col, False))

    def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # Reverse the sorting order for the next time
        tv.heading(col, command=lambda _col=col: self.treeview_sort_column(tv, _col, not reverse))


    def perform_search(self):
        # Get the search query
        query_str = self.search_box.get()
        # Perform the search
        search_results = search_index(query_str)

        # Clear existing results in the table
        for i in self.results_table.get_children():
            self.results_table.delete(i)

        # Populate the table with new results
        for result in search_results:
            self.results_table.insert("", 'end', values=(result['filename'], result['role'], result['content']))

        # Clear the console
        self.console.config(state='normal')
        self.console.delete('1.0', tk.END)

        # Populate the table with new results and print filenames to the console
        for result in search_results:
            self.results_table.insert("", 'end', values=(result['filename'], result['role'], result['content']))
            self.console.insert(tk.END, f"{result['filename']}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = SearchWindow(root)
    root.mainloop()
