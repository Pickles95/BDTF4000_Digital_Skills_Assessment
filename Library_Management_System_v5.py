import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

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

    def create_widgets(self):
        """Create the main GUI components within a single tab."""
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

        btn_add = ttk.Button(add_frame, text="Add Book", command=self.add_book)
        btn_add.grid(column=1, row=3, padx=10, pady=10, sticky=tk.E)

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

        btn_show_all = ttk.Button(search_fields_frame, text="Show All", command=self.display_books)
        btn_show_all.grid(column=2, row=2, padx=10, pady=10, sticky=tk.W)

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

        btn_edit = ttk.Button(manage_frame, text="Edit Selected Book", command=self.edit_book)
        btn_edit.grid(column=0, row=0, padx=10, pady=10, sticky=tk.W)

        btn_check_in = ttk.Button(manage_frame, text="Check In", command=self.check_in)
        btn_check_in.grid(column=1, row=0, padx=10, pady=10, sticky=tk.W)

        btn_check_out = ttk.Button(manage_frame, text="Check Out", command=self.check_out)
        btn_check_out.grid(column=2, row=0, padx=10, pady=10, sticky=tk.W)

        btn_remove = ttk.Button(manage_frame, text="Remove Book", command=self.remove_book)
        btn_remove.grid(column=3, row=0, padx=10, pady=10, sticky=tk.W)

        # Load all books initially
        self.display_books()

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
        btn_save = ttk.Button(edit_window, text="Save Changes",
                              command=lambda: self.save_edit(book_id, entry_title.get().strip(),
                                                           entry_author.get().strip(),
                                                           entry_year.get().strip(),
                                                           status_var.get(),
                                                           edit_window))
        btn_save.grid(column=1, row=4, padx=10, pady=20, sticky=tk.E)

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
