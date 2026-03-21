import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scores.db')

# Comanda SQL pentru creare tabel (dacă nu există deja)
CREATE_CMD = '''
CREATE TABLE IF NOT EXISTS scores (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    player1   TEXT NOT NULL,
    player2   TEXT NOT NULL,
    winner    TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
'''

# Salvăm o rundă nouă
INSERT_CMD = '''
INSERT INTO scores (player1, player2, winner)
VALUES (?, ?, ?)
'''

# Luăm scorul între doi jucători (indiferent de ordine)
SELECT_CMD = '''
SELECT winner, COUNT(*) as wins
FROM scores
WHERE (player1 = ? AND player2 = ?)
   OR (player1 = ? AND player2 = ?)
GROUP BY winner
'''


def init_db():
    """Creează baza de date și tabelul dacă nu există."""
    with sqlite3.connect(DB_PATH) as db:
        db.execute(CREATE_CMD)


def save_score(player1, player2, winner):
    """Salvează rezultatul unei runde."""
    with sqlite3.connect(DB_PATH) as db:
        db.execute(INSERT_CMD, (player1, player2, winner))


def get_scores(player1, player2):
    """
    Returnează un dict cu numărul de victorii pentru fiecare jucător
    și numărul de remize, între cei doi jucători.
    Ex: {'Ana': 3, 'Ion': 1, 'Remiză': 2}
    """
    with sqlite3.connect(DB_PATH) as db:
        rows = db.execute(SELECT_CMD, (player1, player2, player2, player1)).fetchall()

    result = {}
    for winner, wins in rows:
        result[winner] = wins
    return result