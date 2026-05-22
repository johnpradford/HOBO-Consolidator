from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

from .cli import run


def launch() -> None:
    root = tk.Tk()
    root.title("HOBO Consolidator")
    paths: list[str] = []

    def add_files() -> None:
        sel = filedialog.askopenfilenames(title="Select HOBO files")
        for s in sel:
            paths.append(s)
            lb.insert(tk.END, s)

    def add_folder() -> None:
        folder = filedialog.askdirectory(title="Select folder")
        if folder:
            paths.append(folder)
            lb.insert(tk.END, folder)

    def execute() -> None:
        if not paths:
            messagebox.showerror("Error", "No input paths selected")
            return
        code = run(paths)
        messagebox.showinfo("Done", f"Finished with code {code}")

    frm = tk.Frame(root)
    frm.pack(fill=tk.BOTH, expand=True)
    tk.Button(frm, text="Add Files", command=add_files).pack()
    tk.Button(frm, text="Add Folder", command=add_folder).pack()
    tk.Button(frm, text="Run", command=execute).pack()
    lb = tk.Listbox(frm, width=120)
    lb.pack(fill=tk.BOTH, expand=True)
    root.mainloop()


if __name__ == "__main__":
    launch()
