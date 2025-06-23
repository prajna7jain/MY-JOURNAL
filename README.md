# 📝 Personal Journal App (Tkinter + SQLite)

A simple and elegant desktop application to write, manage, and search your personal journal entries with tags and dates. Built using **Python**, **Tkinter**, and **SQLite**.

---

## 🚀 Features

- 🖊️ Add journal entries with title, date, content, and tags
- 🗃️ View and search previous entries by keywords or tags
- 📅 Filter entries by date or tag
- 🗑️ Update or delete existing entries
- 🧠 Clean and user-friendly interface using `ttk.Treeview`
- 💾 Local data storage using SQLite

---


## 🛠️ Technologies Used

- `Python 3.12+`
- `Tkinter` for GUI
- `ttk` for styled widgets
- `SQLite` for persistent storage
- `ScrolledText`, `Treeview`, and custom styling

---

## 📂 Project Structure

├── main.py # Entry point of the application
├── show_entries.py # Main JournalApp class with GUI and logic
├── data_base.py # SQLite connection and table setup
├── journal.db # Generated on first run
└── README.md


## ▶️ How to Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/prajna7jain/MY-JOURNAL.git
   cd MY-JOURNAL
