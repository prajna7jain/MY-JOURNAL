import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime, date
from data_base import connect_db, create_tables

class JournalApp:
    def __init__(self, master):
        self.master = master
        master.title("Personal Journal/Diary")
        master.geometry("1000x700")
        master.configure(bg="#f0f0f0")

        self.conn, self.cursor = connect_db('journal.db')
        create_tables(self.cursor)
        self.conn.commit()

        self.selected_entry_id = None
        self._create_widgets()
        self._load_entries()

    def _create_widgets(self):
        def lbl(frm, txt, r, c, **kwargs):
            tk.Label(frm, text=txt, font=("Inter", 10), bg="#ffffff", **kwargs).grid(row=r, column=c, sticky="w", pady=5)

        input_frame = tk.Frame(self.master, bg="#ffffff", padx=10, pady=10)
        input_frame.pack(side="left", fill="both", expand=False, padx=10, pady=10)
        input_frame.grid_columnconfigure(1, weight=1)

        tk.Label(input_frame, text="Journal Entry", font=("Inter", 16, "bold"), bg="#ffffff", fg="#333").grid(row=0, column=0, columnspan=2, pady=(0, 15))

        lbl(input_frame, "Title:", 1, 0)
        self.title_entry = tk.Entry(input_frame, font=("Inter", 10))
        self.title_entry.grid(row=1, column=1, sticky="ew")

        lbl(input_frame, "Date (YYYY-MM-DD):", 2, 0)
        self.date_entry = tk.Entry(input_frame, font=("Inter", 10))
        self.date_entry.grid(row=2, column=1, sticky="ew")
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

        lbl(input_frame, "Tags (comma-separated):", 3, 0)
        self.tags_entry = tk.Entry(input_frame, font=("Inter", 10))
        self.tags_entry.grid(row=3, column=1, sticky="ew")

        lbl(input_frame, "Content:", 4, 0)
        self.content_text = scrolledtext.ScrolledText(input_frame, wrap="word", font=("Inter", 10), height=15)
        self.content_text.grid(row=4, column=1, sticky="nsew")
        input_frame.grid_rowconfigure(4, weight=1)

        button_frame = tk.Frame(input_frame, bg="#ffffff")
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)
        for txt, cmd, bg in [("Save Entry", self._save_entry, "#4CAF50"),
                             ("New Entry", self._clear_fields, "#2196F3"),
                             ("Delete Entry", self._delete_entry, "#f44336")]:
            tk.Button(button_frame, text=txt, command=cmd, font=("Inter", 10, "bold"), bg=bg, fg="white", cursor="hand2").pack(side="left", padx=5)

        list_frame = tk.Frame(self.master, bg="#ffffff", padx=10, pady=10)
        list_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        list_frame.grid_rowconfigure(4, weight=1)

        tk.Label(list_frame, text="Your Entries", font=("Inter", 16, "bold"), bg="#ffffff").grid(row=0, column=0, columnspan=2, pady=(0, 15))

        for r, txt in enumerate(["Search :", "Search Tags:"], 1):
            lbl(list_frame, txt, r, 0)
        self.search_keyword_entry = tk.Entry(list_frame, font=("Inter", 10))
        self.search_keyword_entry.grid(row=1, column=1, sticky="ew")
        self.search_tags_entry = tk.Entry(list_frame, font=("Inter", 10))
        self.search_tags_entry.grid(row=2, column=1, sticky="ew")

        search_frame = tk.Frame(list_frame, bg="#ffffff")
        search_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        for txt, cmd, bg, fg in [("Search", self._load_entries, "#009688", "white"),
                                 ("Clear Search", self._clear_search_fields, "#FFC107", "#333")]:
            tk.Button(search_frame, text=txt, command=cmd, font=("Inter", 10, "bold"), bg=bg, fg=fg, cursor="hand2").pack(side="left", padx=5)

        self.entry_tree = ttk.Treeview(list_frame, columns=("Date", "Title", "Tags"), show="headings")
        
        for col in ("Date", "Title", "Tags"):
            self.entry_tree.heading(col, text=col)
        self.entry_tree.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=10)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.entry_tree.yview)
        scrollbar.grid(row=4, column=2, sticky="ns")
        self.entry_tree.configure(yscrollcommand=scrollbar.set)
        self.entry_tree.bind("<<TreeviewSelect>>", self._on_entry_select)


    def _validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _save_entry(self):
        title, content = self.title_entry.get().strip(), self.content_text.get("1.0", tk.END).strip()
        entry_date, tags_str = self.date_entry.get().strip(), self.tags_entry.get().strip()
        if not title or not self._validate_date(entry_date): return

        try:
            if self.selected_entry_id:
                self.cursor.execute('UPDATE entries SET title=?, content=?, entry_date=? WHERE id=?', (title, content, entry_date, self.selected_entry_id))
                self.cursor.execute('DELETE FROM entry_tags WHERE entry_id=?', (self.selected_entry_id,))
                entry_id = self.selected_entry_id
            else:
                self.cursor.execute('INSERT INTO entries (title, content, entry_date) VALUES (?, ?, ?)', (title, content, entry_date))
                entry_id = self.cursor.lastrowid

            for tag in [t.strip().lower() for t in tags_str.split(',') if t.strip()]:
                self.cursor.execute('SELECT id FROM tags WHERE name=?', (tag,))
                tag_id = self.cursor.fetchone()
                tag_id = tag_id[0] if tag_id else self.cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag,)).lastrowid
                self.cursor.execute('INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)', (entry_id, tag_id))

            self.conn.commit()
            self._clear_fields()
            self._load_entries()
        except: pass

    def _load_entries(self):
        self.entry_tree.delete(*self.entry_tree.get_children())
        kw, tag_str = self.search_keyword_entry.get().strip(), self.search_tags_entry.get().strip()
        query = '''SELECT e.id, e.title, e.content, e.entry_date, GROUP_CONCAT(t.name) FROM entries e
                   LEFT JOIN entry_tags et ON e.id = et.entry_id
                   LEFT JOIN tags t ON et.tag_id = t.id WHERE 1=1'''
        params = []

        if kw:
            query += " AND (e.title LIKE ? OR e.content LIKE ?)"
            params.extend([f"%{kw}%"] * 2)

        if tag_str:
            tags = [t.strip().lower() for t in tag_str.split(',') if t.strip()]
            placeholders = ','.join('?' * len(tags))
            query += f" AND e.id IN (SELECT et2.entry_id FROM entry_tags et2 JOIN tags t2 ON et2.tag_id = t2.id WHERE t2.name IN ({placeholders}))"
            params.extend(tags)

        query += " GROUP BY e.id ORDER BY e.entry_date DESC"
        for r in self.cursor.execute(query, params).fetchall():
            self.entry_tree.insert("", "end", iid=r[0], values=(r[3], r[1], r[4] or ""))

    def _on_entry_select(self, _):
        i = self.entry_tree.focus()
        if i:
            self.selected_entry_id = int(i)
            r = self.cursor.execute('''SELECT e.title, e.content, e.entry_date, GROUP_CONCAT(t.name) FROM entries e
                                        LEFT JOIN entry_tags et ON e.id = et.entry_id
                                        LEFT JOIN tags t ON et.tag_id = t.id WHERE e.id = ? GROUP BY e.id''', (i,)).fetchone()
            if r:
                self.title_entry.delete(0, tk.END); self.title_entry.insert(0, r[0])
                self.date_entry.delete(0, tk.END); self.date_entry.insert(0, r[2])
                self.content_text.delete("1.0", tk.END); self.content_text.insert("1.0", r[1])
                self.tags_entry.delete(0, tk.END); self.tags_entry.insert(0, r[3] or "")

    def _delete_entry(self):
        if self.selected_entry_id:
            self.cursor.execute('DELETE FROM entries WHERE id=?', (self.selected_entry_id,))
            self.conn.commit()
            self._clear_fields()
            self._load_entries()

    def _clear_fields(self):
        for e in [self.title_entry, self.tags_entry]: e.delete(0, tk.END)
        self.date_entry.delete(0, tk.END); self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.content_text.delete("1.0", tk.END)
        self.selected_entry_id = None
        self.entry_tree.selection_remove(self.entry_tree.selection())

    def _clear_search_fields(self):
        self.search_keyword_entry.delete(0, tk.END)
        self.search_tags_entry.delete(0, tk.END)
        self._load_entries()

    def on_closing(self):
        self.conn.close()
        self.master.destroy()
