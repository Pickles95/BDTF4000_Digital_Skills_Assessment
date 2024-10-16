import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Tooltip class for displaying tooltips
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Removes all window decorations
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)
    
    def hide_tooltip(self, event=None):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()

# Database handler class
class LibraryDatabase:
    def __init__(self, db_name="library.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()

    def connect(self):
        """Connect to the SQLite database."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        """Create the Books table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Books (
                BookID INTEGER PRIMARY KEY AUTOINCREMENT,
                Title TEXT NOT NULL,
                Author TEXT NOT NULL,
                Year INTEGER NOT NULL,
                Status TEXT NOT NULL CHECK (Status IN ('Available', 'Checked Out'))
            )
        """)
        self.conn.commit()

    def add_book(self, title, author, year):
        """Add a new book to the database."""
        self.cursor.execute("""
            INSERT INTO Books (Title, Author, Year, Status)
            VALUES (?, ?, ?, 'Available')
        """, (title, author, year))
        self.conn.commit()

    def search_books(self, title="", author=""):
        """Search books based on title and/or author."""
        query = "SELECT * FROM Books WHERE 1=1"
        params = []
        if title:
            query += " AND Title LIKE ?"
            params.append(f"%{title}%")
        if author:
            query += " AND Author LIKE ?"
            params.append(f"%{author}%")
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def update_status(self, book_id, status):
        """Update the status of a book (Available/Checked Out)."""
        self.cursor.execute("""
            UPDATE Books
            SET Status = ?
            WHERE BookID = ?
        """, (status, book_id))
        self.conn.commit()

    def update_book(self, book_id, title, author, year):
        """Update the details of a book."""
        self.cursor.execute("""
            UPDATE Books
            SET Title = ?, Author = ?, Year = ?
            WHERE BookID = ?
        """, (title, author, year, book_id))
        self.conn.commit()

    def delete_book(self, book_id):
        """Delete a book from the database."""
        self.cursor.execute("""
            DELETE FROM Books
            WHERE BookID = ?
        """, (book_id,))
        self.conn.commit()

    def get_all_books(self):
        """Retrieve all books from the database."""
        self.cursor.execute("SELECT * FROM Books")
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

# GUI class
class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.db = LibraryDatabase()

        # Set window size
        self.root.geometry("1000x800")
        self.create_widgets()

        # Initialize sort settings
        self.sort_column = None
        self.sort_reverse = False

    def create_widgets(self):
        """Create the main GUI components within a single tab."""
        # Initialize style
        style = ttk.Style()
        style.theme_use('clam')  # Choose a modern theme

        # Customize styles
        style.configure('TFrame', background='#ECF0F1')
        style.configure('TLabel', background='#ECF0F1', foreground='#34495E', font=('Arial', 12))
        style.configure('TButton', font=('Arial', 12, 'bold'))
        style.map('TButton',
                  background=[('active', '#34495E')],
                  foreground=[('active', 'white')])

        # Define custom styles for Add and Remove buttons
        style.configure('Add.TButton', background='green', foreground='white')
        style.map('Add.TButton',
                  background=[('active', 'dark green')],
                  foreground=[('active', 'white')])

        style.configure('Remove.TButton', background='red', foreground='white')
        style.map('Remove.TButton',
                  background=[('active', 'dark red')],
                  foreground=[('active', 'white')])

        style.configure('Edit.TButton', foreground='#34495E', font=('Arial', 12, 'bold'))
        style.map('Edit.TButton',
                  background=[('active', '#95A5A6')],
                  foreground=[('active', 'white')])

        style.configure('CheckIn.TButton', foreground='#34495E', font=('Arial', 12, 'bold'))
        style.map('CheckIn.TButton',
                  background=[('active', '#16A085')],
                  foreground=[('active', 'white')])

        style.configure('CheckOut.TButton', foreground='#34495E', font=('Arial', 12, 'bold'))
        style.map('CheckOut.TButton',
                  background=[('active', '#2980B9')],
                  foreground=[('active', 'white')])

        # Create a single frame to hold all sections
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # ---------------------------- Add Book Section ----------------------------
        add_frame = ttk.LabelFrame(main_frame, text="Add New Book")
        add_frame.pack(fill='x', padx=10, pady=10)

        lbl_title = ttk.Label(add_frame, text="Book Title:")
        lbl_title.grid(column=0, row=0, padx=10, pady=5, sticky=tk.W)
        self.entry_title = ttk.Entry(add_frame, width=50)
        self.entry_title.grid(column=1, row=0, padx=10, pady=5)

        lbl_author = ttk.Label(add_frame, text="Author:")
        lbl_author.grid(column=0, row=1, padx=10, pady=5, sticky=tk.W)
        self.entry_author = ttk.Entry(add_frame, width=50)
        self.entry_author.grid(column=1, row=1, padx=10, pady=5)

        lbl_year = ttk.Label(add_frame, text="Year of Release:")
        lbl_year.grid(column=0, row=2, padx=10, pady=5, sticky=tk.W)
        self.entry_year = ttk.Entry(add_frame, width=50)
        self.entry_year.grid(column=1, row=2, padx=10, pady=5)

        # Add Book button with green style
        btn_add = ttk.Button(add_frame, text="Add Book", style='Add.TButton', command=self.add_book)
        btn_add.grid(column=1, row=3, padx=10, pady=10, sticky=tk.E)
        ToolTip(btn_add, "Add a new book to the library")

        # ---------------------------- Search & Display Section ----------------------------
        search_display_frame = ttk.LabelFrame(main_frame, text="Search and View Books")
        search_display_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Search Fields
        search_fields_frame = ttk.Frame(search_display_frame)
        search_fields_frame.pack(fill='x', padx=10, pady=10)

        lbl_search_title = ttk.Label(search_fields_frame, text="Search by Title:")
        lbl_search_title.grid(column=0, row=0, padx=10, pady=5, sticky=tk.W)
        self.search_title = ttk.Entry(search_fields_frame, width=40)
        self.search_title.grid(column=1, row=0, padx=10, pady=5)

        lbl_search_author = ttk.Label(search_fields_frame, text="Search by Author:")
        lbl_search_author.grid(column=0, row=1, padx=10, pady=5, sticky=tk.W)
        self.search_author = ttk.Entry(search_fields_frame, width=40)
        self.search_author.grid(column=1, row=1, padx=10, pady=5)

        btn_search = ttk.Button(search_fields_frame, text="Search", command=self.display_books)
        btn_search.grid(column=1, row=2, padx=10, pady=10, sticky=tk.E)
        ToolTip(btn_search, "Search books by title and/or author")

        btn_show_all = ttk.Button(search_fields_frame, text="Reset Filter", command=self.reset_search)
        btn_show_all.grid(column=2, row=2, padx=10, pady=10, sticky=tk.W)
        ToolTip(btn_show_all, "Reset search filters and display all books")

        # Results Treeview
        tree_frame = ttk.Frame(search_display_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.tree_books = ttk.Treeview(tree_frame, columns=("ID", "Title", "Author", "Year", "Status"), show='headings')
        self.tree_books.heading("ID", text="ID")
        self.tree_books.heading("Title", text="Title")
        self.tree_books.heading("Author", text="Author")
        self.tree_books.heading("Year", text="Year")
        self.tree_books.heading("Status", text="Status")
        self.tree_books.column("ID", width=50, anchor=tk.CENTER)
        self.tree_books.column("Title", width=250)
        self.tree_books.column("Author", width=200)
        self.tree_books.column("Year", width=100, anchor=tk.CENTER)
        self.tree_books.column("Status", width=120, anchor=tk.CENTER)
        self.tree_books.pack(side=tk.LEFT, fill='both', expand=True)

        scrollbar_books = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_books.yview)
        self.tree_books.configure(yscroll=scrollbar_books.set)
        scrollbar_books.pack(side=tk.LEFT, fill='y')

        # ---------------------------- Manage Books Section ----------------------------
        manage_frame = ttk.LabelFrame(main_frame, text="Manage Selected Book")
        manage_frame.pack(fill='x', padx=10, pady=10)

        btn_edit = ttk.Button(manage_frame, text="Edit Selected Book", style='Edit.TButton', command=self.edit_book)
        btn_edit.grid(column=0, row=0, padx=10, pady=10, sticky=tk.W)
        ToolTip(btn_edit, "Edit the details of the selected book")

        btn_check_in = ttk.Button(manage_frame, text="Check In", style='CheckIn.TButton', command=self.check_in)
        btn_check_in.grid(column=1, row=0, padx=10, pady=10, sticky=tk.W)
        ToolTip(btn_check_in, "Mark the selected book as available")

        btn_check_out = ttk.Button(manage_frame, text="Check Out", style='CheckOut.TButton', command=self.check_out)
        btn_check_out.grid(column=2, row=0, padx=10, pady=10, sticky=tk.W)
        ToolTip(btn_check_out, "Mark the selected book as checked out")

        btn_remove = ttk.Button(manage_frame, text="Remove Book", style='Remove.TButton', command=self.remove_book)
        btn_remove.grid(column=3, row=0, padx=10, pady=10, sticky=tk.W)
        ToolTip(btn_remove, "Remove the selected book from the library")

        # ---------------------------- Context Menu ----------------------------
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_book)
        self.context_menu.add_command(label="Check In", command=self.check_in)
        self.context_menu.add_command(label="Check Out", command=self.check_out)
        self.context_menu.add_command(label="Remove", command=self.remove_book)

        # Bind right-click to Treeview
        self.tree_books.bind("<Button-3>", self.show_context_menu)  # Right-click on Windows/Linux
        self.tree_books.bind("<Button-2>", self.show_context_menu)  # Right-click on macOS

        # Bind the heading click for sorting
        for col in ("ID", "Title", "Author", "Year", "Status"):
            self.tree_books.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False))

        # Load all books initially
        self.display_books()

    def reset_search(self):
        """Reset search fields and display all books."""
        self.search_title.delete(0, tk.END)
        self.search_author.delete(0, tk.END)
        self.display_books()
        messagebox.showinfo("Search Reset", "Search filters have been cleared. Displaying all books.")

    def add_book(self):
        """Handle adding a new book."""
        title = self.entry_title.get().strip()
        author = self.entry_author.get().strip()
        year = self.entry_year.get().strip()

        if not title or not author or not year:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        if not year.isdigit():
            messagebox.showwarning("Input Error", "Year must be a number.")
            return

        try:
            self.db.add_book(title, author, int(year))
            messagebox.showinfo("Success", f"Book '{title}' added successfully.")
            self.entry_title.delete(0, tk.END)
            self.entry_author.delete(0, tk.END)
            self.entry_year.delete(0, tk.END)
            self.display_books()  # Refresh the book list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add book. Error: {e}")

    def display_books(self):
        """Display books based on search criteria or show all."""
        title = self.search_title.get().strip()
        author = self.search_author.get().strip()

        if title or author:
            books = self.db.search_books(title, author)
        else:
            books = self.db.get_all_books()

        # Clear previous results
        for item in self.tree_books.get_children():
            self.tree_books.delete(item)

        for book in books:
            self.tree_books.insert('', tk.END, values=book)

    def get_selected_book(self):
        """Retrieve the currently selected book."""
        selected_item = self.tree_books.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a book from the list.")
            return None

        book = self.tree_books.item(selected_item)['values']
        return book

    def edit_book(self):
        """Handle editing a book's information."""
        book = self.get_selected_book()
        if not book:
            return

        book_id, title, author, year, status = book

        # Create a new window for editing
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"Edit Book ID {book_id}")
        edit_window.geometry("400x300")
        edit_window.resizable(False, False)

        # Labels and Entry widgets
        lbl_title = ttk.Label(edit_window, text="Book Title:")
        lbl_title.grid(column=0, row=0, padx=10, pady=10, sticky=tk.W)
        entry_title = ttk.Entry(edit_window, width=40)
        entry_title.grid(column=1, row=0, padx=10, pady=10)
        entry_title.insert(0, title)

        lbl_author = ttk.Label(edit_window, text="Author:")
        lbl_author.grid(column=0, row=1, padx=10, pady=10, sticky=tk.W)
        entry_author = ttk.Entry(edit_window, width=40)
        entry_author.grid(column=1, row=1, padx=10, pady=10)
        entry_author.insert(0, author)

        lbl_year = ttk.Label(edit_window, text="Year of Release:")
        lbl_year.grid(column=0, row=2, padx=10, pady=10, sticky=tk.W)
        entry_year = ttk.Entry(edit_window, width=40)
        entry_year.grid(column=1, row=2, padx=10, pady=10)
        entry_year.insert(0, year)

        lbl_status = ttk.Label(edit_window, text="Status:")
        lbl_status.grid(column=0, row=3, padx=10, pady=10, sticky=tk.W)
        status_var = tk.StringVar()
        status_combobox = ttk.Combobox(edit_window, textvariable=status_var, state="readonly")
        status_combobox['values'] = ("Available", "Checked Out")
        status_combobox.grid(column=1, row=3, padx=10, pady=10)
        status_combobox.set(status)

        # Save Button
        btn_save = ttk.Button(edit_window, text="Save Changes", command=lambda: self.save_edit(book_id, entry_title.get().strip(),
                                                                                               entry_author.get().strip(),
                                                                                               entry_year.get().strip(),
                                                                                               status_var.get(),
                                                                                               edit_window))
        btn_save.grid(column=1, row=4, padx=10, pady=20, sticky=tk.E)
        ToolTip(btn_save, "Save the changes made to the book")

    def save_edit(self, book_id, title, author, year, status, window):
        """Save the edited book information."""
        if not title or not author or not year or not status:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        if not year.isdigit():
            messagebox.showwarning("Input Error", "Year must be a number.")
            return

        try:
            self.db.update_book(book_id, title, author, int(year))
            self.db.update_status(book_id, status)  # Update status separately
            messagebox.showinfo("Success", f"Book ID {book_id} updated successfully.")
            window.destroy()
            self.display_books()  # Refresh the book list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update book. Error: {e}")

    def check_in(self):
        """Handle checking in a book."""
        book = self.get_selected_book()
        if not book:
            return

        book_id, title, author, year, status = book

        if status == "Available":
            messagebox.showinfo("Info", "Book is already available.")
            return

        confirm = messagebox.askyesno("Confirm Check-In", f"Are you sure you want to check in '{title}'?")
        if not confirm:
            return

        try:
            self.db.update_status(book_id, "Available")
            messagebox.showinfo("Success", f"Book '{title}' checked in successfully.")
            self.display_books()  # Refresh the book list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check in book. Error: {e}")

    def check_out(self):
        """Handle checking out a book."""
        book = self.get_selected_book()
        if not book:
            return

        book_id, title, author, year, status = book

        if status == "Checked Out":
            messagebox.showinfo("Info", "Book is already checked out.")
            return

        confirm = messagebox.askyesno("Confirm Check-Out", f"Are you sure you want to check out '{title}'?")
        if not confirm:
            return

        try:
            self.db.update_status(book_id, "Checked Out")
            messagebox.showinfo("Success", f"Book '{title}' checked out successfully.")
            self.display_books()  # Refresh the book list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check out book. Error: {e}")

    def remove_book(self):
        """Handle removing a book."""
        book = self.get_selected_book()
        if not book:
            return

        book_id, title, author, year, status = book

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove '{title}' by {author}?")
        if not confirm:
            return

        try:
            self.db.delete_book(book_id)
            messagebox.showinfo("Success", f"Book '{title}' removed successfully.")
            self.display_books()  # Refresh the book list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove book. Error: {e}")

    def show_context_menu(self, event):
        """Display the context menu on right-click."""
        # Identify the row under mouse
        region = self.tree_books.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree_books.identify_row(event.y)
        if row_id:
            # Select the row
            self.tree_books.selection_set(row_id)
            # Display the context menu
            self.context_menu.post(event.x_root, event.y_root)

    def sort_treeview(self, col, reverse):
        """Sort Treeview contents when a column header is clicked."""
        # Determine the sort order
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_reverse = False
        self.sort_column = col

        # Get all data from the Treeview
        data = [(self.tree_books.set(child, col), child) for child in self.tree_books.get_children('')]

        # For numerical sorting on 'ID' and 'Year'
        if col in ("ID", "Year"):
            try:
                data.sort(key=lambda t: int(t[0]), reverse=self.sort_reverse)
            except ValueError:
                data.sort(key=lambda t: t[0], reverse=self.sort_reverse)
        elif col == "Status":
            # Custom sort for Status: Available before Checked Out
            status_order = {"Available": 0, "Checked Out": 1}
            data.sort(key=lambda t: status_order.get(t[0], 2), reverse=self.sort_reverse)
        else:
            # Alphabetical sorting for 'Title' and 'Author'
            data.sort(key=lambda t: t[0].lower(), reverse=self.sort_reverse)

        # Rearrange items in sorted positions
        for index, (val, child) in enumerate(data):
            self.tree_books.move(child, '', index)

        # Update the sort indicators
        self.update_sort_indicators()

    def update_sort_indicators(self):
        """Update the column headers with sort indicators."""
        # Clear all sort indicators
        for col in ("ID", "Title", "Author", "Year", "Status"):
            self.tree_books.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False))

        # Add sort indicator to the current sorted column
        if self.sort_column:
            sort_indicator = " ▲" if not self.sort_reverse else " ▼"
            new_text = f"{self.sort_column}{sort_indicator}"
            self.tree_books.heading(self.sort_column, text=new_text, command=lambda _col=self.sort_column: self.sort_treeview(_col, not self.sort_reverse))

    def reset_search(self):
        """Reset search fields and display all books."""
        self.search_title.delete(0, tk.END)
        self.search_author.delete(0, tk.END)
        self.display_books()
        messagebox.showinfo("Search Reset", "Search filters have been cleared. Displaying all books.")

    def on_closing(self):
        """Handle application closing."""
        self.db.close()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = LibraryGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
