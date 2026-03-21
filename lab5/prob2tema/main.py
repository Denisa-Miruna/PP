import tkinter as tk
from tkinter import simpledialog, messagebox
from multiprocessing import freeze_support

import database
import network
from GameWindow import GameWindow


def ask_name(root):
    """Deschide un dialog simplu care cere numele jucătorului."""
    name = simpledialog.askstring(
        'Bun venit!',
        'Introdu numele tău:',
        parent=root
    )
    if not name or not name.strip():
        root.destroy()
        return None
    return name.strip()


def main():
    freeze_support()  # necesar pe Windows pentru multiprocessing

    # Inițializăm baza de date (creează fișierul dacă nu există)
    database.init_db()

    root = tk.Tk()
    root.withdraw()  # ascundem fereastra principală până configurăm totul

    # Cerem numele jucătorului
    player_name = ask_name(root)
    if not player_name:
        return

    # Încercăm să ne conectăm ca jucătorul 2 (client)
    # Dacă nu există server → devenim jucătorul 1 (server)
    try:
        send_q, recv_q = network.connect_client()
        symbol = 'O'
        messagebox.showinfo('Conectat!', 'Te-ai conectat ca Jucătorul 2 (O).\nJucătorul 1 (X) începe.')
    except Exception:
        send_q, recv_q = network.start_server()
        symbol = 'X'
        messagebox.showinfo('Așteaptă...', 'Ești Jucătorul 1 (X).\nAșteaptă ca Jucătorul 2 să se conecteze.')

    # Afișăm fereastra principală și pornim jocul
    root.deiconify()
    GameWindow(root, player_name, symbol, send_q, recv_q)
    root.mainloop()


if __name__ == '__main__':
    main()