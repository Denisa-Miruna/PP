import multiprocessing as mp
from multiprocessing.managers import BaseManager
import threading

PORT = 50001
KEY  = b'xo_secret_key'


class GameManager(BaseManager):
    pass


def start_server():
    """
    Jucătorul 1 devine server.
    Creează două cozi și le înregistrează pe server:
      q1 = P1 trimite, P2 citește
      q2 = P2 trimite, P1 citește
    Returnează (send_queue, recv_queue) pentru P1.
    """
    q1 = mp.Queue()  # P1 → P2
    q2 = mp.Queue()  # P2 → P1

    GameManager.register('get_q1', callable=lambda: q1)
    GameManager.register('get_q2', callable=lambda: q2)

    manager = GameManager(address=('', PORT), authkey=KEY)
    server = manager.get_server()

    # Serverul rulează în background (daemon = se închide cu programul)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    return q1, q2   # P1 trimite pe q1, primește pe q2


def connect_client():
    """
    Jucătorul 2 se conectează la serverul lui P1.
    Returnează (send_queue, recv_queue) pentru P2.
    Aruncă excepție dacă serverul nu e pornit.
    """
    GameManager.register('get_q1')
    GameManager.register('get_q2')

    manager = GameManager(address=('localhost', PORT), authkey=KEY)
    manager.connect()

    q1 = manager.get_q1()  # P1 → P2 (P2 citește de aici)
    q2 = manager.get_q2()  # P2 → P1 (P2 trimite aici)

    return q2, q1   # P2 trimite pe q2, primește pe q1