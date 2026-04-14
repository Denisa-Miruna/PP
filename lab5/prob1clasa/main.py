import tkinter as tk
from multiprocessing import freeze_support
from parser1 import Parser


if __name__ == '__main__':
    freeze_support()

    root = tk.Tk()
    app = Parser(root)
    root.mainloop()