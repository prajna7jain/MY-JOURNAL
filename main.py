from tkinter import Tk
from show_entries import JournalApp

if __name__ == "__main__":
    root = Tk()

    from tkinter import ttk
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Inter", 10, "bold"), background="#e0e0e0", foreground="#333333")
    style.configure("Treeview", font=("Inter", 10), rowheight=25, background="#f9f9f9", foreground="#333333")
    style.map("Treeview", background=[("selected", "#007bff")])

    app = JournalApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()