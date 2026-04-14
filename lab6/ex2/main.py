import os
import sys


class FileAnalyzer:
    def analyze(self, content: bytes):
        raise NotImplementedError()


class XMLAnalyzer(FileAnalyzer):

    def analyze(self, content: bytes):
        if not content:
            return False

        try:
            text = content.decode("ascii", errors="ignore")
        except:
            return False

        return text.strip().startswith("<?xml")



class UnicodeAnalyzer(FileAnalyzer):

    def analyze(self, content: bytes):
        if not content:
            return False

        total = len(content)
        zero_count = content.count(0)

        return (zero_count / total) >= 0.30



class BMPAnalyzer(FileAnalyzer):

    def analyze(self, content: bytes):
        return len(content) > 2 and content[0:2] == b'BM'

    def get_info(self, content: bytes):
        """
        Extrage:
        width, height, bits per pixel
        din header BMP
        """

        if len(content) < 30:
            return None

        # offseturi standard BMP
        width = int.from_bytes(content[18:22], byteorder='little')
        height = int.from_bytes(content[22:26], byteorder='little')
        bpp = int.from_bytes(content[28:30], byteorder='little')

        return width, height, bpp



class DirectoryScanner:

    def __init__(self, root_dir):
        self.root_dir = root_dir

        self.xml_analyzer = XMLAnalyzer()
        self.unicode_analyzer = UnicodeAnalyzer()
        self.bmp_analyzer = BMPAnalyzer()

    def scan(self):
        print(f"\n🔍 Scanare: {self.root_dir}\n")

        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                path = os.path.join(root, file)
                self.process_file(path)

    def process_file(self, path):
        try:
            with open(path, "rb") as f:
                content = f.read()

            abs_path = os.path.abspath(path)

            #  BMP
            if self.bmp_analyzer.analyze(content):
                info = self.bmp_analyzer.get_info(content)
                if info:
                    w, h, bpp = info
                    print(f"[BMP] {abs_path} → ({w}x{h}), {bpp} bpp")
                return

            #  XML ASCII
            if self.xml_analyzer.analyze(content):
                print(f"[XML ASCII] {abs_path}")
                return

            #  UNICODE
            if self.unicode_analyzer.analyze(content):
                print(f"[UNICODE] {abs_path}")
                return

        except Exception as e:
            print(f"[EROARE] {path}: {e}")



def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <director>")
        return

    root_dir = sys.argv[1]

    scanner = DirectoryScanner(root_dir)
    scanner.scan()


if __name__ == "__main__":
    main()