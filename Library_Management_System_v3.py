import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

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
        self.root.geometry("1000x700")
        self.create_widgets()

    def create_widgets(self):
        """Create the main GUI components."""
        # Create a Notebook (tabbed interface)
        self.tab_control = ttk.Notebook(self.root)

        # Tabs
        self.tab_add = ttk.Frame(self.tab_control)
        self.tab_search = ttk.Frame(self.tab_control)
        self.tab_manage = ttk.Frame(self.tab_control)
        self.tab_view = ttk.Frame(self.tab_control)  # New Tab

        self.tab_control.add(self.tab_add, text='Add Book')
        self.tab_control.add(self.tab_search, text='Search Books')
        self.tab_control.add(self.tab_manage, text='Manage Check-in/Check-out')
        self.tab_control.add(self.tab_view, text='View All Books')  # Add new tab

        self.tab_control.pack(expand=1, fill="both")

        # Add Book Tab
        self.create_add_tab()

        # Search Books Tab
        self.create_search_tab()

        # Manage Check-in/Check-out Tab
        self.create_manage_tab()

        # View All Books Tab
        self.create_view_tab()

    def create_add_tab(self):
        """Create widgets for the Add Book tab."""
        frame = self.tab_add

        # Labels and Entry widgets
        lbl_title = ttk.Label(frame, text="Book Title:")
        lbl_title.grid(column=0, row=0, padx=10, pady=10, sticky=tk.W)
        self.entry_title = ttk.Entry(frame, width=50)
        self.entry_title.grid(column=1, row=0, padx=10, pady=10)

        lbl_author = ttk.Label(frame, text="Author:")
        lbl_author.grid(column=0, row=1, padx=10, pady=10, sticky=tk.W)
        self.entry_author = ttk.Entry(frame, width=50)
        self.entry_author.grid(column=1, row=1, padx=10, pady=10)

        lbl_year = ttk.Label(frame, text="Year of Release:")
        lbl_year.grid(column=0, row=2, padx=10, pady=10, sticky=tk.W)
        self.entry_year = ttk.Entry(frame, width=50)
        self.entry_year.grid(column=1, row=2, padx=10, pady=10)

        # Submit Button
        btn_submit = ttk.Button(frame, text="Add Book", command=self.add_book)
        btn_submit.grid(column=1, row=3, padx=10, pady=20, sticky=tk.E)

    def create_search_tab(self):
        """Create widgets for the Search Books tab."""
        frame = self.tab_search

        # Search Fields
        lbl_search_title = ttk.Label(frame, text="Search by Title:")
        lbl_search_title.grid(column=0, row=0, padx=10, pady=10, sticky=tk.W)
        self.search_title = ttk.Entry(frame, width=40)
        self.search_title.grid(column=1, row=0, padx=10, pady=10)

        lbl_search_author = ttk.Label(frame, text="Search by Author:")
        lbl_search_author.grid(column=0, row=1, padx=10, pady=10, sticky=tk.W)
        self.search_author = ttk.Entry(frame, width=40)
        self.search_author.grid(column=1, row=1, padx=10, pady=10)

        # Search Button
        btn_search = ttk.Button(frame, text="Search", command=self.search_books)
        btn_search.grid(column=1, row=2, padx=10, pady=10, sticky=tk.E)

        # Results Treeview
        self.tree_search = ttk.Treeview(frame, columns=("ID", "Title", "Author", "Year", "Status"), show='headings')
        self.tree_search.heading("ID", text="ID")
        self.tree_search.heading("Title", text="Title")
        self.tree_search.heading("Author", text="Author")
        self.tree_search.heading("Year", text="Year")
        self.tree_search.heading("Status", text="Status")
        self.tree_search.column("ID", width=30, anchor=tk.CENTER)
        self.tree_search.column("Title", width=250)
        self.tree_search.column("Author", width=180)
        self.tree_search.column("Year", width=80, anchor=tk.CENTER)
        self.tree_search.column("Status", width=120, anchor=tk.CENTER)
        self.tree_search.grid(column=0, row=3, columnspan=2, padx=10, pady=10, sticky='nsew')

        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_search.yview)
        self.tree_search.configure(yscroll=scrollbar.set)
        scrollbar.grid(column=2, row=3, sticky='ns')

    def create_manage_tab(self):
        """Create widgets for the Manage Check-in/Check-out tab."""
        frame = self.tab_manage

        # Search Fields
        lbl_manage_title = ttk.Label(frame, text="Book Title:")
        lbl_manage_title.grid(column=0, row=0, padx=10, pady=10, sticky=tk.W)
        self.manage_title = ttk.Entry(frame, width=40)
        self.manage_title.grid(column=1, row=0, padx=10, pady=10)

        lbl_manage_author = ttk.Label(frame, text="Author:")
        lbl_manage_author.grid(column=0, row=1, padx=10, pady=10, sticky=tk.W)
        self.manage_author = ttk.Entry(frame, width=40)
        self.manage_author.grid(column=1, row=1, padx=10, pady=10)

        # Search Button
        btn_manage_search = ttk.Button(frame, text="Search", command=self.manage_search)
        btn_manage_search.grid(column=1, row=2, padx=10, pady=10, sticky=tk.E)

        # Results Treeview
        self.tree_manage = ttk.Treeview(frame, columns=("ID", "Title", "Author", "Year", "Status"), show='headings')
        self.tree_manage.heading("ID", text="ID")
        self.tree_manage.heading("Title", text="Title")
        self.tree_manage.heading("Author", text="Author")
        self.tree_manage.heading("Year", text="Year")
        self.tree_manage.heading("Status", text="Status")
        self.tree_manage.column("ID", width=30, anchor=tk.CENTER)
        self.tree_manage.column("Title", width=250)
        self.tree_manage.column("Author", width=180)
        self.tree_manage.column("Year", width=80, anchor=tk.CENTER)
        self.tree_manage.column("Status", width=120, anchor=tk.CENTER)
        self.tree_manage.grid(column=0, row=3, columnspan=3, padx=10, pady=10, sticky='nsew')

        # Add scrollbar
        scrollbar_manage = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_manage.yview)
        self.tree_manage.configure(yscroll=scrollbar_manage.set)
        scrollbar_manage.grid(column=3, row=3, sticky='ns')

        # Action Buttons
        btn_check_in = ttk.Button(frame, text="Check In", command=self.check_in)
        btn_check_in.grid(column=1, row=4, padx=10, pady=10, sticky=tk.E)

        btn_check_out = ttk.Button(frame, text="Check Out", command=self.check_out)
        btn_check_out.grid(column=2, row=4, padx=10, pady=10, sticky=tk.W)

        btn_remove = ttk.Button(frame, text="Remove Book", command=self.remove_book)
        btn_remove.grid(column=1, row=5, padx=10, pady=10, sticky=tk.E)

    def create_view_tab(self):
        """Create widgets for the View All Books tab."""
        frame = self.tab_view

        # Treeview to display all books
        self.tree_view = ttk.Treeview(frame, columns=("ID", "Title", "Author", "Year", "Status"), show='headings')
        self.tree_view.heading("ID", text="ID")
        self.tree_view.heading("Title", text="Title")
        self.tree_view.heading("Author", text="Author")
        self.tree_view.heading("Year", text="Year")
        self.tree_view.heading("Status", text="Status")
        self.tree_view.column("ID", width=30, anchor=tk.CENTER)
        self.tree_view.column("Title", width=250)
        self.tree_view.column("Author", width=180)
        self.tree_view.column("Year", width=80, anchor=tk.CENTER)
        self.tree_view.column("Status", width=120, anchor=tk.CENTER)
        self.tree_view.grid(column=0, row=0, columnspan=4, padx=10, pady=10, sticky='nsew')

        # Add scrollbar
        scrollbar_view = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_view.yview)
        self.tree_view.configure(yscroll=scrollbar_view.set)
        scrollbar_view.grid(column=4, row=0, sticky='ns')

        # Refresh Button
        btn_refresh = ttk.Button(frame, text="Refresh List", command=self.refresh_view)
        btn_refresh.grid(column=0, row=1, padx=10, pady=10, sticky=tk.W)

        # Edit Button
        btn_edit = ttk.Button(frame, text="Edit Selected Book", command=self.edit_book)
        btn_edit.grid(column=1, row=1, padx=10, pady=10, sticky=tk.W)

        # Load all books initially
        self.load_all_books()

    def load_all_books(self):
        """Load all books into the view_all treeview."""
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)

        books = self.db.get_all_books()
        for book in books:
            self.tree_view.insert('', tk.END, values=book)

    def refresh_view(self):
        """Refresh the list of all books."""
        self.load_all_books()

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
            self.load_all_books()  # Refresh the view all books list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add book. Error: {e}")

    def search_books(self):
        """Handle searching for books."""
        title = self.search_title.get().strip()
        author = self.search_author.get().strip()

        results = self.db.search_books(title, author)

        # Clear previous results
        for item in self.tree_search.get_children():
            self.tree_search.delete(item)

        for book in results:
            self.tree_search.insert('', tk.END, values=book)

    def manage_search(self):
        """Handle searching books for management."""
        title = self.manage_title.get().strip()
        author = self.manage_author.get().strip()

        results = self.db.search_books(title, author)

        # Clear previous results
        for item in self.tree_manage.get_children():
            self.tree_manage.delete(item)

        for book in results:
            self.tree_manage.insert('', tk.END, values=book)

    def check_in(self):
        """Handle checking in a book."""
        selected_item = self.tree_manage.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a book to check in.")
            return

        book = self.tree_manage.item(selected_item)['values']
        book_id = book[0]
        status = book[4]

        if status == "Available":
            messagebox.showinfo("Info", "Book is already available.")
            return

        try:
            self.db.update_status(book_id, "Available")
            messagebox.showinfo("Success", f"Book '{book[1]}' checked in successfully.")
            self.manage_search()  # Refresh the list
            self.load_all_books()  # Refresh the view all books list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check in book. Error: {e}")

    def check_out(self):
        """Handle checking out a book."""
        selected_item = self.tree_manage.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a book to check out.")
            return

        book = self.tree_manage.item(selected_item)['values']
        book_id = book[0]
        status = book[4]

        if status == "Checked Out":
            messagebox.showinfo("Info", "Book is already checked out.")
            return

        try:
            self.db.update_status(book_id, "Checked Out")
            messagebox.showinfo("Success", f"Book '{book[1]}' checked out successfully.")
            self.manage_search()  # Refresh the list
            self.load_all_books()  # Refresh the view all books list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check out book. Error: {e}")

    def remove_book(self):
        """Handle removing a book."""
        selected_item = self.tree_manage.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a book to remove.")
            return

        book = self.tree_manage.item(selected_item)['values']
        book_id = book[0]
        title = book[1]
        author = book[2]

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove '{title}' by {author}?")
        if not confirm:
            return

        try:
            self.db.delete_book(book_id)
            messagebox.showinfo("Success", f"Book '{title}' removed successfully.")
            self.manage_search()  # Refresh the list
            self.load_all_books()  # Refresh the view all books list
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove book. Error: {e}")

    def edit_book(self):
        """Handle editing a book's information."""
        selected_item = self.tree_view.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a book to edit.")
            return

        book = self.tree_view.item(selected_item)['values']
        book_id = book[0]
        title = book[1]
        author = book[2]
        year = book[3]
        status = book[4]

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
            self.load_all_books()  # Refresh the view all books list
            self.manage_search()    # Refresh the manage list if applicable
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update book. Error: {e}")

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
