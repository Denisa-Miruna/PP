import tkinter as tk
from multiprocessing import freeze_support
from parser1 import Parser

# Acesta este punctul de intrare al aplicației.
# Rolul lui e simplu: creează fereastra și pornește aplicația.

if __name__ == '__main__':
    freeze_support()  # necesar pe Windows pentru multiprocessing

    root = tk.Tk()
    app = Parser(root)
    root.mainloop()   # mainloop() e DOAR aici