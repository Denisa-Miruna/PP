import os
import sys
from multiprocessing import Process, Queue

from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog
from PyQt5.uic import loadUi


def task_convert_to_html(message_queue):
    """
    Citește conținutul din coadă și îl convertește în HTML.
    Prima linie → <title> și <h1>, restul → paragrafe <p>.
    """
    content = message_queue.get()

    lines = content.strip().split('\n')
    lines = [l.strip() for l in lines if l.strip()]  # eliminăm liniile goale

    if not lines:
        message_queue.put("<p>Fișier gol.</p>")
        return

    title = lines[0]
    paragraphs = lines[1:]

    html_parts = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        f'    <title>{title}</title>',
        '</head>',
        '<body>',
        f'    <h1>{title}</h1>',
    ]
    for p in paragraphs:
        html_parts.append(f'    <p>{p}</p>')
    html_parts += ['</body>', '</html>']

    message_queue.put('\n'.join(html_parts))


def task_send_to_c(message_queue):
    """
    Simulează trimiterea HTML-ului către programul C.
    Salvează conținutul în output.html în același dosar.
    (Varianta reală folosește sysv_ipc pe Linux.)
    """
    html_content = message_queue.get()

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'output.html'
    )
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    message_queue.put(f"Salvat în: {output_path}")


# Interfața grafică PyQt5

class HTMLConverter(QWidget):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        super(HTMLConverter, self).__init__()

        # Încărcăm interfața din fișierul .ui (ca în schelet)
        ui_path = os.path.join(self.ROOT_DIR, 'html_converter.ui')
        loadUi(ui_path, self)

        # Conectăm butoanele la metode
        self.browse_btn.clicked.connect(self.browse)
        self.convert_btn.clicked.connect(self.convert_to_html)
        self.send_btn.clicked.connect(self.send_to_c)

        self.file_path = None    # Calea fișierului selectat
        self.html_result = None  # HTML-ul generat, păstrat pentru Send



    def browse(self):
        """Deschide dialogul de selectare fișier .txt"""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog

        file, _ = QFileDialog.getOpenFileName(
            self,
            caption='Selectează fișier text',
            directory='',
            filter='Text Files (*.txt)',
            options=options
        )

        if file:
            self.file_path = file
            self.path_line_edit.setText(file)

    def convert_to_html(self):
        """
        Citește fișierul și lansează un proces care
        convertește conținutul în HTML prin coadă de mesaje.
        """
        if not self.file_path:
            self.result_text_edit.setPlainText('Selectează mai întâi un fișier!')
            return

        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Comunicare prin coadă de mesaje
        message_queue = Queue()
        message_queue.put(content)

        p = Process(target=task_convert_to_html, args=(message_queue,))
        p.start()
        p.join()

        self.html_result = message_queue.get()
        self.result_text_edit.setPlainText(self.html_result)

    def send_to_c(self):
        """
        Trimite HTML-ul generat prin coadă de mesaje
        (salvat în output.html în același dosar).
        """
        if not self.html_result:
            self.result_text_edit.setPlainText('Convertește mai întâi un fișier!')
            return

        message_queue = Queue()
        message_queue.put(self.html_result)

        p = Process(target=task_send_to_c, args=(message_queue,))
        p.start()
        p.join()

        status = message_queue.get()
        self.result_text_edit.append(f'\n--- {status} ---')