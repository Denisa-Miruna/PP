

import tkinter as tk
from tkinter import simpledialog
import sysv_ipc          # pip install sysv_ipc   (Linux / macOS)
import sqlite3
import threading
import json
import time
import os

# ══════════════════════════════════════════════════════════════════
#  CONSTANTE
# ══════════════════════════════════════════════════════════════════

# Cheia cozii System-V – ambele instanțe folosesc ACEEAȘI cheie
MSG_KEY = 0xABCD          # = 43981 în zecimal

# Tipuri de mesaje (fiecare tip e "canalul" propriu)
TYPE_CONNECT  = 1   # P2  → P1 : "mă conectez, sunt <nume>"
TYPE_ACK      = 2   # P1  → P2 : "te-am acceptat + scor anterior"
TYPE_MOVE_P1  = 3   # P1  → P2 : index celulă (0-8)
TYPE_MOVE_P2  = 4   # P2  → P1 : index celulă (0-8)
TYPE_RESET    = 5   # ori → ori : "vrem o nouă rundă"
TYPE_QUIT     = 6   # ori → ori : "am închis fereastra"

# Triplete câștigătoare pentru tabla 3×3
WINS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rânduri
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # coloane
    (0, 4, 8), (2, 4, 6),              # diagonale
]


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv/scores.db")

def init_db():
    """Creează tabelul dacă nu există."""
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            player1  TEXT NOT NULL,
            player2  TEXT NOT NULL,
            wins1    INTEGER DEFAULT 0,
            wins2    INTEGER DEFAULT 0,
            draws    INTEGER DEFAULT 0,
            PRIMARY KEY (player1, player2)
        )
    """)
    con.commit()
    con.close()


def get_score(p1, p2):

    con = sqlite3.connect(DB_PATH)
    # Încearcă ordinea directă (p1, p2)
    row = con.execute(
        "SELECT wins1, wins2, draws FROM scores WHERE player1=? AND player2=?",
        (p1, p2)
    ).fetchone()
    if row is None:
        # Încearcă ordinea inversată (p2, p1) și inversează coloanele
        row = con.execute(
            "SELECT wins2, wins1, draws FROM scores WHERE player1=? AND player2=?",
            (p2, p1)
        ).fetchone()
    con.close()
    return row


def save_result(p1, p2, result):

    con = sqlite3.connect(DB_PATH)

    row = con.execute(
        "SELECT wins1, wins2, draws FROM scores WHERE player1=? AND player2=?",
        (p1, p2)
    ).fetchone()

    if row:
        w1, w2, d = row
        if result == 'p1':   w1 += 1
        elif result == 'p2': w2 += 1
        else:                d  += 1
        con.execute(
            "UPDATE scores SET wins1=?, wins2=?, draws=? WHERE player1=? AND player2=?",
            (w1, w2, d, p1, p2)
        )
    else:
        # Poate există (p2, p1) → actualizăm cu perspectiva inversată
        row2 = con.execute(
            "SELECT wins1, wins2, draws FROM scores WHERE player1=? AND player2=?",
            (p2, p1)
        ).fetchone()
        if row2:
            w1, w2, d = row2
            # 'p1' din apel = 'p2' din DB (ordinea e inversată)
            if result == 'p1':   w2 += 1
            elif result == 'p2': w1 += 1
            else:                d  += 1
            con.execute(
                "UPDATE scores SET wins1=?, wins2=?, draws=? WHERE player1=? AND player2=?",
                (w1, w2, d, p2, p1)
            )
        else:
            # Prima partidă → inserăm
            if result == 'p1':
                w1 = 1
            else:
                w1 = 0

            if result == 'p2':
                w2 = 1
            else:
                w2 = 0

            if result == 'draw':
                d = 1
            else:
                d = 0
            con.execute(
                "INSERT INTO scores VALUES (?, ?, ?, ?, ?)",
                (p1, p2, w1, w2, d)
            )

    con.commit()
    con.close()



#  CLASA PRINCIPALĂ A JOCULUI

class TicTacToe:

    def __init__(self):
        init_db()

        # ── State ────────────────────────────────────────────────
        self.is_host   = False    # True = Jucător 1 (X), False = Jucător 2 (O)
        self.my_name   = ""
        self.opp_name  = ""
        self.my_sym    = ""       # "X" sau "O"
        self.opp_sym   = ""
        self.send_type = 0        # tipul cu care trimit mutările mele
        self.recv_type = 0        # tipul din care primesc mutările adversarului
        self.mq        = None     # obiectul coadă System-V
        self.board     = [""] * 9
        self.my_turn   = False
        self.game_over = False
        self.running   = True
        self.round_id  = 0        # crește la fiecare rundă nouă

        # ── Tkinter ──────────────────────────────────────────────
        self.root = tk.Tk()
        self.root.title("X și 0 – P2P")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")     #culoare background

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)   #apeleaza un fel de destructor al jocului cand apesi pe x
        self._ask_name()
        self.root.mainloop()


    #  CONSTRUIRE INTERFAȚĂ


    def _build_ui(self):
        BG   = "#1e1e2e"
        CARD = "#2a2a3e"  #culori

        # Titlu
        tk.Label(self.root, text="X și 0",
                 bg=BG, fg="#ffffff").pack(pady=(14, 0))  #fgg culloare text, 14 px mai jos te margine sus

        # Scor istoric (afișat sus, în albastru-deschis)
        self.lbl_hist = tk.Label(self.root, text="",
                                 font=("Helvetica", 11),
                                 bg=BG, fg="#89dceb")
        self.lbl_hist.pack(pady=(4, 0))

        # Status curent (tura, victorie etc.)
        self.lbl_st = tk.Label(self.root, text="Se inițializează…",
                               font=("Helvetica", 13, "bold"),
                               bg=BG, fg="#cdd6f4", wraplength=300)
        self.lbl_st.pack(pady=8)

        # ── Tabla 3×3 ─────────────────────────────────────────────
        frm = tk.Frame(self.root, bg="#45475a", padx=3, pady=3)
        frm.pack(padx=16, pady=4)

        self.btns = []
        for i in range(9):
            btn = tk.Button(
                frm,
                text="",
                font=("Helvetica", 48, "bold"),
                width=3, height=1,
                bg=CARD, fg="#cdd6f4",
                activebackground="#313244",
                relief="flat",
                disabledforeground="#6c7086",
                command=lambda i=i: self._click(i)
            )
            btn.grid(row=i // 3, column=i % 3, padx=2, pady=2)
            self.btns.append(btn)

        self._lock_board()

        # ── Buton rundă nouă
        self.btn_new = tk.Button(
            self.root, text=" Rundă nouă",
            font=("Helvetica", 12, "bold"),
            bg="#a6e3a1", fg="#1e1e2e",
            activebackground="#94e2d5",
            relief="flat", padx=10, pady=5,
            command=self._request_new_round
        )



    def _st(self, txt):
        """Actualizează eticheta de status din orice thread."""
        self.root.after(0, lambda: self.lbl_st.config(text=txt))

    def _lock_board(self):
        for b in self.btns:
            b.config(state=tk.DISABLED)

    def _unlock_board(self):
        for i, b in enumerate(self.btns):
            if self.board[i] == "":
                b.config(state=tk.NORMAL)

    def _update_hist(self, score):
        """
        Afișează scorul anterior în eticheta de sus.
        score = (w_me, w_opp, draws) SAU None
        """
        if score:
            w_me, w_opp, d = score
            txt = (f"📊  {self.my_name}: {w_me} victorii  │  "
                   f"{self.opp_name}: {w_opp} victorii  │  Egaluri: {d}")
        else:
            txt = "Prima partidă între voi!"
        self.lbl_hist.config(text=txt)


    #  CONECTARE  (System-V Message Queue)


    def _ask_name(self):
        name = simpledialog.askstring(
            "Jucător", "Introduceți numele dumneavoastră:", parent=self.root)
        if not name or not name.strip():
            self.root.quit()
            return
        self.my_name = name.strip()
        self._connect()

    def _connect(self):
        try:
            # ── Încearcă să CREEZE coada → devine Jucătorul 1 (X / host) ──
            self.mq = sysv_ipc.MessageQueue(
                MSG_KEY,
                flags=sysv_ipc.IPC_CREX,   # eșuează dacă există deja
                mode=0o666,
                max_message_size=512
            )
            self.is_host   = True
            self.my_sym    = "X"
            self.opp_sym   = "O"
            self.send_type = TYPE_MOVE_P1
            self.recv_type = TYPE_MOVE_P2
            self._st(f"Bun venit, {self.my_name}!\nAșteptăm celălalt jucător…")
            threading.Thread(target=self._host_handshake, daemon=True).start()

        except sysv_ipc.ExistentialError:
            # ── Coada există → devine Jucătorul 2 (O / client) ──
            self.mq = sysv_ipc.MessageQueue(MSG_KEY, mode=0o666, max_message_size=512)
            self.is_host   = False
            self.my_sym    = "O"
            self.opp_sym   = "X"
            self.send_type = TYPE_MOVE_P2
            self.recv_type = TYPE_MOVE_P1
            # Trimitem imediat mesajul de conectare cu numele nostru
            self._send(TYPE_CONNECT, {"name": self.my_name})
            self._st("Conectat! Așteptăm confirmarea host-ului…")
            threading.Thread(target=self._client_handshake, daemon=True).start()



    def _host_handshake(self):
        """Host: așteaptă mesajul de conectare de la client."""
        data = self._recv_block(TYPE_CONNECT, timeout=300)
        if data is None:
            self._st("Timeout! Niciun jucător nu s-a conectat.")
            return

        self.opp_name = data["name"]

        # Citim scorul din BD (perspectiva host-ului: eu = p1)
        score = get_score(self.my_name, self.opp_name)
        # Trimitem ACK cu numele nostru și scorul (ca dict, pentru JSON)
        sd = {"w1": score[0], "w2": score[1], "d": score[2]} if score else None
        self._send(TYPE_ACK, {"name": self.my_name, "score": sd})

        # Actualizăm UI-ul din firul principal
        self.root.after(0, lambda s=score: self._update_hist(s))
        self.root.after(0, self._start_game)

    def _client_handshake(self):
        """Client: așteaptă ACK-ul de la host."""
        data = self._recv_block(TYPE_ACK, timeout=300)
        if data is None:
            self._st("Host-ul nu a răspuns. Reporniți jocul.")
            return

        self.opp_name = data["name"]
        sd = data.get("score")

        # sd e din perspectiva host-ului: w1=host, w2=client
        # Inversăm pentru a afișa din perspectiva clientului
        if sd:
            score = (sd["w2"], sd["w1"], sd["d"])   # (w_me, w_opp, draws)
        else:
            score = None

        self.root.after(0, lambda s=score: self._update_hist(s))
        self.root.after(0, self._start_game)



    def _start_game(self):
        """Resetează tabla și pornește o rundă nouă."""
        self.board     = [""] * 9
        self.game_over = False
        self.round_id += 1          # semnalizăm thread-ului vechi să se oprească
        self.btn_new.pack_forget()

        # Resetăm vizual butoanele tablei
        for b in self.btns:
            b.config(text="", bg="#2a2a3e", fg="#cdd6f4")

        # X (host) începe întotdeauna primul
        self.my_turn = self.is_host
        if self.my_turn:
            self._st(f"Tura ta!  Joci cu  {self.my_sym}")
            self._unlock_board()
        else:
            self._st(f"Tura lui {self.opp_name}…  ({self.opp_sym})")
            self._lock_board()

        # Pornește thread-ul de ascultare (cu round_id curent)
        current_round = self.round_id
        threading.Thread(
            target=self._recv_loop,
            args=(current_round,),
            daemon=True
        ).start()

    def _click(self, pos):
        """Apelat când jucătorul local apasă o celulă."""
        if not self.my_turn or self.board[pos] or self.game_over:
            return
        self._apply_move(pos, self.my_sym)          # aplică local
        self._send(self.send_type, {"pos": pos})    # trimite adversarului

    def _apply_move(self, pos, sym):
        """
        Aplică mutarea pe tablă (și local și la primire).
        Verifică câștigătorul după fiecare mutare.
        """
        self.board[pos] = sym
        color = "#f38ba8" if sym == "X" else "#89b4fa"   # roșu / albastru
        self.btns[pos].config(text=sym, fg=color, state=tk.DISABLED)

        winner = self._check_winner()

        if winner:
            # ── Jocul s-a terminat ──
            self.game_over = True
            self._lock_board()
            self._highlight_winner(winner)

            if winner == "draw":
                self._st("Egalitate!  ")
                self.root.after(0, lambda: self._finish("draw"))
            elif winner == self.my_sym:
                self._st("Ai câștigat!  ")
                # 'p1' = host câștigă; 'p2' = clientul câștigă
                result = "p1" if self.is_host else "p2"
                self.root.after(0, lambda r=result: self._finish(r))
            else:
                self._st(f"{self.opp_name} a câștigat!  ")
                result = "p2" if self.is_host else "p1"
                self.root.after(0, lambda r=result: self._finish(r))
        else:
            # ── Jocul continuă; schimbăm tura ──
            if sym == self.my_sym:
                self.my_turn = False
                self._st(f"Tura lui {self.opp_name}…  ({self.opp_sym})")
                self._lock_board()
            else:
                self.my_turn = True
                self._st(f"Tura ta!  Joci cu  {self.my_sym}")
                self.root.after(0, self._unlock_board)

    def _check_winner(self):
        """
        Returnează simbolul câștigător, 'draw' sau None (joc în curs).
        """
        b = self.board
        for a, bb, c in WINS:
            if b[a] and b[a] == b[bb] == b[c]:
                return b[a]
        if "" not in b:
            return "draw"
        return None

    def _highlight_winner(self, winner):
        """Colorează linia câștigătoare în galben."""
        if winner not in ("X", "O"):
            return
        for a, bb, c in WINS:
            if self.board[a] == self.board[bb] == self.board[c] == winner:
                for i in (a, bb, c):
                    self.btns[i].config(bg="#f9e2af")
                break

    def _finish(self, result):
        """
        Apelat după fiecare rundă: salvează scorul (doar host-ul)
        și afișează butonul de rundă nouă.
        """
        if self.is_host:
            # Host-ul salvează scorul în SQLite
            save_result(self.my_name, self.opp_name, result)
            # Reîncarcă și afișează imediat
            score = get_score(self.my_name, self.opp_name)
            self._update_hist(score)
        else:
            # Clientul așteaptă puțin ca host-ul să salveze, apoi reîncarcă
            self.root.after(400, self._reload_hist)

        self.btn_new.pack(pady=10)

    def _reload_hist(self):
        score = get_score(self.my_name, self.opp_name)
        self._update_hist(score)

    def _request_new_round(self):
        """Butonul 'Rundă nouă' – trimite reset și repornește local."""
        self._send(TYPE_RESET, {})
        self.btn_new.pack_forget()
        self._start_game()


    #  THREAD DE ASCULTARE  (rulează în fundal)


    def _recv_loop(self, my_round):
        """
        Ascultă în buclă mesajele adversarului.
        Se oprește automat dacă round_id s-a schimbat (rundă nouă).
        """
        while self.running and self.round_id == my_round:
            # ── Ascultă mutarea adversarului (dacă jocul e în curs) ──
            if not self.game_over:
                msg = self._recv_nb(self.recv_type)
                if msg is not None:
                    pos = msg["pos"]
                    self.root.after(0, lambda p=pos: self._apply_move(p, self.opp_sym))

            # ── Ascultă cerere de rundă nouă ──
            rst = self._recv_nb(TYPE_RESET)
            if rst is not None:
                self.root.after(0, self._start_game)
                return   # _start_game va porni un thread nou

            # ── Ascultă ieșire adversar ──
            q = self._recv_nb(TYPE_QUIT)
            if q is not None:
                self.root.after(0, lambda: self._st(
                    f"{self.opp_name} a ieșit din joc."))
                return

            time.sleep(0.05)

    #  TRIMITERE / PRIMIRE MESAJE


    def _send(self, mtype, data):
        """Trimite un dict Python ca JSON în coadă."""
        payload = json.dumps(data).encode("utf-8")
        self.mq.send(payload, type=mtype)

    def _recv_block(self, mtype, timeout=60):
        """
        Primire blocantă cu timeout (secunde).
        Returnează dict sau None la expirare.
        """
        deadline = time.time() + timeout
        while self.running and time.time() < deadline:
            try:
                raw, _ = self.mq.receive(type=mtype, block=False)
                return json.loads(raw.decode("utf-8"))
            except sysv_ipc.BusyError:
                time.sleep(0.1)
        return None

    def _recv_nb(self, mtype):
        """Primire ne-blocantă; returnează dict sau None."""
        try:
            raw, _ = self.mq.receive(type=mtype, block=False)
            return json.loads(raw.decode("utf-8"))
        except sysv_ipc.BusyError:
            return None



    def _on_close(self):
        self.running = False
        try:
            self._send(TYPE_QUIT, {})
        except Exception:
            pass
        # Host-ul șterge coada la ieșire
        if self.is_host and self.mq:
            try:
                self.mq.remove()
            except Exception:
                pass
        self.root.destroy()



if __name__ == "__main__":
    TicTacToe()