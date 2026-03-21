import tkinter as tk
from tkinter import messagebox
import queue

import database


# Dimensiunile butoanelor de pe tablă
CELL_SIZE = 120


class GameWindow:

    def __init__(self, root, player_name, symbol, send_q, recv_q, opponent_name=""):
        """
        root        - fereastra Tkinter
        player_name - numele acestui jucător
        symbol      - 'X' (jucătorul 1) sau 'O' (jucătorul 2)
        send_q      - coada pe care trimitem mutările noastre
        recv_q      - coada de pe care citim mutările adversarului
        opponent_name - numele adversarului (primit prin coadă la start)
        """
        self.root = root
        self.player_name   = player_name
        self.symbol        = symbol          # 'X' sau 'O'
        self.opponent_sym  = 'O' if symbol == 'X' else 'X'
        self.send_q        = send_q
        self.recv_q        = recv_q
        self.opponent_name = opponent_name

        # Tabla de joc: lista 3x3 cu '' / 'X' / 'O'
        self.board = [[''] * 3 for _ in range(3)]

        # X începe întotdeauna primul
        self.my_turn = (symbol == 'X')

        self._build_ui()
        self._update_status()

        # Trimitem numele nostru adversarului
        self.send_q.put({'type': 'name', 'name': player_name})

        # Pornim polling-ul cozii de mesaje (la fiecare 200ms)
        self.root.after(200, self._poll_queue)

    # ----------------------------------------------------------
    # CONSTRUIRE INTERFAȚĂ
    # ----------------------------------------------------------

    def _build_ui(self):
        self.root.title(f'X și 0 — {self.player_name} ({self.symbol})')
        self.root.resizable(False, False)

        # --- Zona de scor (sus) ---
        self.score_lbl = tk.Label(
            self.root,
            text='Se încarcă scorul...',
            font=('Arial', 11),
            pady=4
        )
        self.score_lbl.grid(row=0, column=0, columnspan=3)

        # --- Status (rândul cui e) ---
        self.status_lbl = tk.Label(
            self.root,
            text='',
            font=('Arial', 13, 'bold'),
            pady=6
        )
        self.status_lbl.grid(row=1, column=0, columnspan=3)

        # --- Tabla 3x3 ---
        self.buttons = []
        for r in range(3):
            row_btns = []
            for c in range(3):
                btn = tk.Button(
                    self.root,
                    text='',
                    font=('Arial', 36, 'bold'),
                    width=3,
                    height=1,
                    relief='groove',
                    command=lambda row=r, col=c: self._on_click(row, col)
                )
                btn.grid(row=r + 2, column=c, padx=4, pady=4)
                row_btns.append(btn)
            self.buttons.append(row_btns)

        # --- Buton Joacă din nou ---
        self.restart_btn = tk.Button(
            self.root,
            text='Joacă din nou',
            font=('Arial', 11),
            state='disabled',
            command=self._restart
        )
        self.restart_btn.grid(row=5, column=0, columnspan=3, pady=8)

    # ----------------------------------------------------------
    # LOGICA JOCULUI
    # ----------------------------------------------------------

    def _on_click(self, row, col):
        """Apelat când jucătorul local face click pe o celulă."""
        if not self.my_turn:
            return
        if self.board[row][col] != '':
            return

        # Plasăm simbolul
        self._place(row, col, self.symbol)

        # Trimitem mutarea adversarului prin coadă
        self.send_q.put({'type': 'move', 'row': row, 'col': col})

        # Verificăm dacă am câștigat
        self._check_end()

    def _place(self, row, col, symbol):
        """Plasează simbolul pe tablă și actualizează butonul."""
        self.board[row][col] = symbol
        color = '#1565C0' if symbol == 'X' else '#C62828'
        self.buttons[row][col].config(
            text=symbol,
            fg=color,
            state='disabled'
        )
        self.my_turn = not self.my_turn
        self._update_status()

    def _check_end(self):
        """Verifică dacă jocul s-a terminat (câștig sau remiză)."""
        winner_sym = self._get_winner()

        if winner_sym:
            winner_name = self.player_name if winner_sym == self.symbol else self.opponent_name
            self._end_game(f'{winner_name} a câștigat!', winner_name)
        elif self._is_draw():
            self._end_game('Remiză!', 'Remiză')

    def _get_winner(self):
        """Returnează simbolul câștigătorului sau None."""
        b = self.board
        lines = [
            # linii orizontale
            [b[0][0], b[0][1], b[0][2]],
            [b[1][0], b[1][1], b[1][2]],
            [b[2][0], b[2][1], b[2][2]],
            # coloane
            [b[0][0], b[1][0], b[2][0]],
            [b[0][1], b[1][1], b[2][1]],
            [b[0][2], b[1][2], b[2][2]],
            # diagonale
            [b[0][0], b[1][1], b[2][2]],
            [b[0][2], b[1][1], b[2][0]],
        ]
        for line in lines:
            if line[0] != '' and line[0] == line[1] == line[2]:
                return line[0]
        return None

    def _is_draw(self):
        """Returnează True dacă tabla e plină și nu e câștigător."""
        return all(self.board[r][c] != '' for r in range(3) for c in range(3))

    def _end_game(self, message, winner_name):
        """Afișează rezultatul și salvează în baza de date."""
        self._disable_board()
        self.restart_btn.config(state='normal')
        self.status_lbl.config(text=message)

        # Salvăm scorul în SQLite
        database.save_score(self.player_name, self.opponent_name, winner_name)

        # Actualizăm afișarea scorului
        self._refresh_score()

        # Trimitem și adversarului că jocul s-a terminat (pentru a activa restart)
        self.send_q.put({'type': 'end', 'winner': winner_name})

    def _restart(self):
        """Resetează tabla și trimite restart adversarului."""
        self._reset_board()
        self.send_q.put({'type': 'restart'})
        self.restart_btn.config(state='disabled')

    def _reset_board(self):
        """Curăță tabla și repornește jocul."""
        self.board = [[''] * 3 for _ in range(3)]
        self.my_turn = (self.symbol == 'X')  # X începe mereu
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text='', state='normal', fg='black')
        self._update_status()

    def _disable_board(self):
        """Dezactivează toate celulele goale."""
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == '':
                    self.buttons[r][c].config(state='disabled')

    # ----------------------------------------------------------
    # POLLING COADĂ DE MESAJE
    # ----------------------------------------------------------

    def _poll_queue(self):
        """
        Verifică coada recv_q la fiecare 200ms.
        Procesăm toate mesajele disponibile fără blocare.
        """
        try:
            while True:
                msg = self.recv_q.get_nowait()  # nu blochează
                self._handle_message(msg)
        except queue.Empty:
            pass

        # Programăm următoarea verificare
        self.root.after(200, self._poll_queue)

    def _handle_message(self, msg):
        """Procesează un mesaj primit de la adversar."""
        msg_type = msg.get('type')

        if msg_type == 'name':
            # Am primit numele adversarului
            self.opponent_name = msg['name']
            self.root.title(f'X și 0 — {self.player_name} ({self.symbol}) vs {self.opponent_name}')
            self._refresh_score()
            self._update_status()

        elif msg_type == 'move':
            # Adversarul a făcut o mutare
            row, col = msg['row'], msg['col']
            self._place(row, col, self.opponent_sym)
            self._check_end()

        elif msg_type == 'end':
            # Adversarul a detectat sfârșitul jocului
            self.restart_btn.config(state='normal')
            self._disable_board()

        elif msg_type == 'restart':
            # Adversarul vrea să joace din nou
            self._reset_board()
            self.restart_btn.config(state='disabled')

    # ----------------------------------------------------------
    # HELPERS UI
    # ----------------------------------------------------------

    def _update_status(self):
        opp = self.opponent_name or 'adversar'
        if self.my_turn:
            self.status_lbl.config(text=f'Rândul tău ({self.symbol})', fg='#1B5E20')
        else:
            self.status_lbl.config(text=f'Rândul lui {opp} ({self.opponent_sym})', fg='#B71C1C')

    def _refresh_score(self):
        """Citește scorul din SQLite și îl afișează."""
        if not self.opponent_name:
            return
        scores = database.get_scores(self.player_name, self.opponent_name)
        my_wins  = scores.get(self.player_name, 0)
        opp_wins = scores.get(self.opponent_name, 0)
        draws    = scores.get('Remiză', 0)
        self.score_lbl.config(
            text=f'{self.player_name}: {my_wins}  |  Remize: {draws}  |  {self.opponent_name}: {opp_wins}'
        )