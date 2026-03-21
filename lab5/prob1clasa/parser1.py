import os
import tkinter as tk
from multiprocessing import Process, Queue


# ============================================================
# FUNCȚII PENTRU PROCESE - fiecare rulează într-un proces separat
# ============================================================

def task_filter_odd(message_queue):
    numbers = message_queue.get()
    result = [n for n in numbers if n % 2 != 0]
    message_queue.put(result)


def task_filter_primes(message_queue):
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    numbers = message_queue.get()
    result = [n for n in numbers if is_prime(n)]
    message_queue.put(result)


def task_sum(message_queue):
    numbers = message_queue.get()
    message_queue.put(sum(numbers))


# ============================================================
# CLASA PRINCIPALĂ – Interfața grafică
# ============================================================

class Parser:
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self, gui):
        self.gui = gui
        self.gui.title('Exemplul 1 cu Tkinter')
        self.gui.geometry("700x400")

        self.integer_list = []

        # --- Rândul 0: input lista ---
        self.integer_list_lbl = tk.Label(master=self.gui, text="List of integers:")
        self.integer_list_text = tk.Text(self.gui, width=50, height=1)
        self.integer_list_text.insert(tk.END, str(list(range(1, 16)))[1:-1])
        self.add_list_btn = tk.Button(master=self.gui, text="Add list",
                                      command=self.add_list)

        self.integer_list_lbl.grid(row=0, column=0, padx=5, pady=10, sticky="e")
        self.integer_list_text.grid(row=0, column=1, padx=5, pady=10)
        self.add_list_btn.grid(row=0, column=2, padx=5, pady=10)

        # --- Rândul 1: zona de rezultate ---
        result_lbl = tk.Label(master=self.gui, text="Result:")
        result_lbl.grid(row=1, column=0, padx=5, sticky="ne")

        self.result_text = tk.Text(self.gui, width=50, height=12, state="disabled")
        self.result_text.grid(row=1, column=1, padx=5, pady=5)

        # --- Butoanele pentru operații ---
        self.filter_odd_btn = tk.Button(master=self.gui, text="Filter odd",
                                        width=12, command=self.filter_odd)
        self.filter_primes_btn = tk.Button(master=self.gui, text="Filter primes",
                                           width=12, command=self.filter_primes)
        self.sum_btn = tk.Button(master=self.gui, text="Sum numbers",
                                 width=12, command=self.sum_numbers)

        self.filter_odd_btn.grid(row=1, column=2, padx=5, pady=5, sticky="n")
        self.filter_primes_btn.grid(row=2, column=2, padx=5, pady=5, sticky="n")
        self.sum_btn.grid(row=3, column=2, padx=5, pady=5, sticky="n")

        # IMPORTANT: mainloop() NU e aici! Este în main.py

    def add_list(self):
        raw_text = self.integer_list_text.get("1.0", tk.END)
        raw_text = raw_text.strip().replace(' ', '')
        try:
            self.integer_list = [int(item) for item in raw_text.split(',')]
            self._show_result(f"Lista incarcata: {self.integer_list}\n")
        except ValueError:
            self._show_result("Eroare: introdu doar numere intregi separate prin virgula!\n")

    def filter_odd(self):
        if not self._check_list():
            return
        message_queue = Queue()
        message_queue.put(self.integer_list)
        p = Process(target=task_filter_odd, args=(message_queue,))
        p.start()
        p.join()
        self._show_result(f"Numere impare: {message_queue.get()}\n")

    def filter_primes(self):
        if not self._check_list():
            return
        message_queue = Queue()
        message_queue.put(self.integer_list)
        p = Process(target=task_filter_primes, args=(message_queue,))
        p.start()
        p.join()
        self._show_result(f"Numere prime: {message_queue.get()}\n")

    def sum_numbers(self):
        if not self._check_list():
            return
        message_queue = Queue()
        message_queue.put(self.integer_list)
        p = Process(target=task_sum, args=(message_queue,))
        p.start()
        p.join()
        self._show_result(f"Suma: {message_queue.get()}\n")

    def _check_list(self):
        if not self.integer_list:
            self._show_result("Apasa mai intai 'Add list'!\n")
            return False
        return True

    def _show_result(self, text):
        self.result_text.config(state="normal")
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)
        self.result_text.config(state="disabled")