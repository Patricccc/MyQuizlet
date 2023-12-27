import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkbootstrap import Style

# Create database table
def create_table(conn):
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    set_name TEXT NOT NULL
        )
    ''')

    # Create table for words
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    definition TEXT NOT NULL,
                    set_id INTEGER NOT NULL,
                    FOREIGN KEY (set_id) REFERENCES sets (id)
        )
    ''')

# Insert a new set into the database
def insert_set(conn, set_name):
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO sets (set_name)
        VALUES (?)
    ''', (set_name,))
    set_id = cursor.lastrowid 
    conn.commit()
    return set_id

# Insert a new word into the database
def insert_word(conn, word, definition, set_id):
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO words (word, definition, set_id)
        VALUES (?, ?, ?)
    ''', (word, definition, set_id))
    # Get id
    card_id = cursor.lastrowid
    conn.commit()
    return card_id

# Get all sets from the database
def get_sets(conn):
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, set_name FROM sets
    ''')
    rows = cursor.fetchall()
    # Dictionary of sets
    sets = {row[1]: row[0] for row in rows}
    return sets

# Get all words from a set
def get_words(conn, set_id):
    cursor = conn.cursor()

    cursor.execute('''
        SELECT word, definition FROM words WHERE set_id = ?
    ''', (set_id,))
    rows = cursor.fetchall()
    # List of cards
    words = [(row[0], row[1]) for row in rows]
    return words

# Remove a set from the database
def remove_set(conn, set_id):
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM sets WHERE id = ?
    ''', (set_id,))
    conn.commit()
    sets_combo.set('')
    clear_display()
    populate_sets()

    # Clear the words from the set and reset the index
    global index, current
    index = 0
    current = []

# Create a new set
def create_set():
    set_name = set_name.get()
    if set_name:
        if set_name not in get_sets(conn):
            set_id = insert_set(conn, set_name)
            populate_sets()
            set_name.set('')
            word.set('')
            definition.set('')

def add_word():
    set_name = set_name.get()
    word = word.get()
    definition = definition.get()

    if set_name and word and definition:
        if set_name in get_sets(conn):
            set_id = get_sets(conn)[set_name]
        else:
            set_id = create_set(conn, set_name)

        insert_word(conn, word, definition, set_id)
        word.set('')
        definition.set('')
        populate_sets()

# Populate the combobox with sets
def populate_sets():
    sets_combo['values'] = tuple(get_sets(conn).keys())

# Delete a set
def delete_set():
    set_name = sets_combo.get()
    if set_name:
        result = messagebox.askyesno('Delete Set', 'Are you sure you want to delete this set?')
        if result == tk.YES:
            set_id = get_sets(conn)[set_name]
            remove_set(conn, set_id)
            populate_sets()
            clear_display()

# Select a set
def select_set():
    set_name = sets_combo.get()
    if set_name:
        set_id = get_sets(conn)[set_name]
        words = get_words(conn, set_id)
        if words:
            display_words(words)
        else: 
            word.label.config(text='No words in this set')
            define.label.config(text='')
    else:
        global index, current
        index = 0
        current = []
        clear_display()

# Display words
def display_words(words):
    global index, current
    current = words
    index = 0
    if not words:
        clear_display()
    else:
        show_word()
    show_word()

# Clear the display
def clear_display():
    word.label.config(text='')
    define.label.config(text='')

# Show a word
def show_word():
    global index, current
    if current:
        if 0 <= index < len(current):
            word, _= current[index]
            word.label.config(text=word)
            define.label.config(text='')
        else:
            clear_display()
    else:
        clear_display()

# Show the definition
def flip_card():
    global index, current
    if current:
        _, definition = current[index]
        define.label.config(text=definition) 

# Go to the next card
def next_card():
    global current, index
    if current:
        index = min(index + 1, len(current) - 1)
        show_word()

# Go to the previous card
def previous_card():
    global current, index
    if current:
        index = max(index - 1, 0)
        show_word()

if __name__ == '__main__':
    # Connect to database
    conn = sqlite3.connect('flashcards.db')
    create_table(conn)

    # Main GUI window
    root = tk.Tk()
    root.title("Flashcard App")
    root.geometry("500x500")

    # Create a style object
    style = Style(theme="darkly") # minty is also a good theme
    style.configure('Tlabel', font=('TkDefaultFont', 18))
    style.configure('TButton', font=('TkDefaultFont', 16))

    # Store user input
    set_name = tk.StringVar()
    word = tk.StringVar()
    definition = tk.StringVar()

    # Notebook widget for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # Create tabs
    # First tab is for creating a new set
    create_frame = ttk.Frame(notebook)
    notebook.add(create_frame, text="Create")

    # Label and input for set name, word and definition
    ttk.Label(create_frame, text="Set Name:").pack(padx=5, pady=5)
    ttk.Entry(create_frame, textvariable=set_name).pack(padx=5, pady=5)

    ttk.Label(create_frame, text="Word:").pack(padx=5, pady=5)
    ttk.Entry(create_frame, textvariable=word).pack(padx=5, pady=5)

    ttk.Label(create_frame, text="Definition:").pack(padx=5, pady=5)
    ttk.Entry(create_frame, textvariable=definition).pack(padx=5, pady=5)

    # Buttons for adding words and saving sets
    ttk.Button(create_frame, text="Add", command=add_word).pack(padx=5, pady=10)
    ttk.Button(create_frame, text="Save", command=create_set).pack(padx=5, pady=10)

    # Second tab is for choosing a set
    choose_frame = ttk.Frame(notebook)
    notebook.add(choose_frame, text="Choose")

    # Combobox for selecting a set
    sets_combo = ttk.Combobox(choose_frame)
    sets_combo.pack(padx=5, pady=40)

    # Button to choose a set
    ttk.Button(choose_frame, text="Choose Set", command=select_set).pack(padx=5, pady=5)
    
    # Button to remove a set
    ttk.Button(choose_frame, text="Remove Set", command=remove_set).pack(padx=5, pady=5)

    # Third tab is for practicing a set
    practice_frame = ttk.Frame(notebook)
    notebook.add(practice_frame, text="Practice")

    # Index and current
    index = 0
    current = []

    # Display flashcard
    flashcard = ttk.Label(practice_frame, text='', font=('TkDefaultFont', 24))
    flashcard.pack(padx=5, pady=40)

    # Display answer
    define = ttk.Label(practice_frame, text='')
    define.pack(padx=5, pady=5)

    # Button to show answer/flip card
    ttk.Button(practice_frame, text='Flip', command=flip_card).pack(side='left', padx=5, pady=5)

    # Button to go to next card
    ttk.Button(practice_frame, text='Next', command=next_card).pack(side='right', padx=5, pady=5)

    # Button to go to previous card
    ttk.Button(practice_frame, text='Previous', command=previous_card).pack(side='right', padx=5, pady=5)

    # Populate the combobox with sets
    populate_sets()

    root.mainloop()