import os
import sys
import struct


# <<Interface>> GenericFile

class GenericFile:

    def __init__(self, path_absolut: str, frecvente: list):
        self.path_absolut = path_absolut
        self.frecvente = frecvente  # lista de 256 de frecvente (float, suma = 1.0)

    def get_path(self) -> str:
        raise NotImplementedError("get_path nu este implementata")

    def get_freq(self) -> list:
        raise NotImplementedError("get_freq nu este implementata")



class TextASCII(GenericFile):
    """\
    Frecvente mari pentru octeti in {9,10,13,32..127},
    frecvente foarte mici pentru octeti in {0..8,11,12,14..31,128..255}.
    """

    def __init__(self, path_absolut: str, frecvente: list):
        super().__init__(path_absolut, frecvente)

    def get_path(self) -> str:
        return self.path_absolut

    def get_freq(self) -> list:
        return self.frecvente



class XMLFile(TextASCII):
    """
    Are campul suplimentar first_tag (primul tag XML gasit).
    """

    def __init__(self, path_absolut: str, frecvente: list, first_tag: str):
        super().__init__(path_absolut, frecvente)
        self.first_tag = first_tag

    def get_first_tag(self) -> str:
        return self.first_tag



class TextUNICODE(GenericFile):
    """

    Caracterul 0 apare in cel putin 30% din tot textul.
    """

    def __init__(self, path_absolut: str, frecvente: list):
        super().__init__(path_absolut, frecvente)

    def get_path(self) -> str:
        return self.path_absolut

    def get_freq(self) -> list:
        return self.frecvente


class Binary(GenericFile):
    """
    Frecventele sunt distribuite oarecum uniform pe domeniul {0..255}.
    """

    def __init__(self, path_absolut: str, frecvente: list):
        super().__init__(path_absolut, frecvente)

    def get_path(self) -> str:
        return self.path_absolut

    def get_freq(self) -> list:
        return self.frecvente


class BMP(Binary):
    """
    Campuri suplimentare: width, height, bpp (bits per pixel).
    """

    def __init__(self, path_absolut: str, frecvente: list,
                 width: int, height: int, bpp: int):
        super().__init__(path_absolut, frecvente)
        self.width = width
        self.height = height
        self.bpp = bpp

    def show_info(self) -> str:
        return (f"BMP: {self.path_absolut} | "
                f"{self.width}x{self.height} px | {self.bpp} bpp")



def _compute_frequencies(content: bytes) -> list:

    total = len(content)
    if total == 0:
        return [0.0] * 256
    counts = [0] * 256
    for byte in content:
        counts[byte] += 1
    return [c / total for c in counts]


def _is_ascii_text(freq: list) -> bool:
    """
    Frecvente mari pentru {9,10,13,32..127},
    frecvente foarte mici pentru {0..8,11,12,14..31,128..255}.
    Prag: cel putin 90% din octeti sunt in zona ASCII imprimabila/spatiu alb.
    """
    printable_indices = set([9, 10, 13]) | set(range(32, 128))
    ascii_mass = sum(freq[i] for i in printable_indices)
    return ascii_mass >= 0.90


def _is_unicode_utf16(freq: list) -> bool:
    """Caracterul 0 apare in cel putin 30% din text => UTF-16."""
    return freq[0] >= 0.30


def _is_binary(freq: list) -> bool:
    """
    Frecventele sunt distribuite relativ uniform.(niciuna din conditiile ASCII/UNICODE nu e indeplinita.)
    """
    return not _is_ascii_text(freq) and not _is_unicode_utf16(freq)


def _read_bmp_header(content: bytes):
    """
    Parseaza antetul BMP si returneaza (width, height, bpp) sau None.
    bytes BMP: 'BM' (0x42 0x4D).
    """
    if len(content) < 54:
        return None
    if content[0:2] != b'BM':
        return None
    # DIB header incepe la offset 14
    # width  = bytes 18-21 (little-endian int32)
    # height = bytes 22-25 (little-endian int32, poate fi negativ)
    # bpp    = bytes 28-29 (little-endian uint16)
    width  = struct.unpack_from('<i', content, 18)[0]
    height = struct.unpack_from('<i', content, 22)[0]
    bpp    = struct.unpack_from('<H', content, 28)[0]
    return abs(width), abs(height), bpp


def _extract_first_xml_tag(content: bytes) -> str:
    """Gaseste primul tag XML din continut (ex: '<root' -> 'root')."""
    try:
        text = content.decode('utf-8', errors='ignore')
    except Exception:
        return ""
    start = text.find('<')
    while start != -1:
        # sari peste declaratia XML si comentarii
        if text[start:start+2] in ('<?', '<!'):
            end = text.find('>', start)
            start = text.find('<', end + 1) if end != -1 else -1
            continue
        end = text.find('>', start)
        if end == -1:
            break
        tag_content = text[start+1:end].strip().split()[0] if text[start+1:end].strip() else ''
        if tag_content:
            return tag_content
        start = text.find('<', start + 1)
    return ""


def _is_xml(content: bytes, freq: list) -> bool:
    """Un fisier ASCII care contine un tag XML valid la inceput."""
    if not _is_ascii_text(freq):
        return False
    tag = _extract_first_xml_tag(content)
    return bool(tag)


def classify_file(file_path: str):
    """
    Citeste fisierul, calculeaza frecventele si returneaza
    instanta corespunzatoare clasei potrivite (sau None la eroare).
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
    except (IOError, PermissionError):
        return None

    freq = _compute_frequencies(content)
    abs_path = os.path.abspath(file_path)

    # Ordinea conteaza: BMP < Binary, XMLFile < TextASCII
    bmp_info = _read_bmp_header(content)
    if bmp_info is not None:
        w, h, bpp = bmp_info
        return BMP(abs_path, freq, w, h, bpp)

    if _is_unicode_utf16(freq):
        return TextUNICODE(abs_path, freq)

    if _is_xml(content, freq):
        tag = _extract_first_xml_tag(content)
        return XMLFile(abs_path, freq, tag)

    if _is_ascii_text(freq):
        return TextASCII(abs_path, freq)

    return Binary(abs_path, freq)



def scan_directory(root_dir: str):
    xml_files    = []
    unicode_files = []
    bmp_files    = []

    for root, subdirs, files in os.walk(root_dir):
        for filename in os.listdir(root):
            file_path = os.path.join(root, filename)
            if not os.path.isfile(file_path):
                continue
            obj = classify_file(file_path)
            if obj is None:
                continue
            if isinstance(obj, XMLFile):
                xml_files.append(obj)
            elif isinstance(obj, TextUNICODE):
                unicode_files.append(obj)
            elif isinstance(obj, BMP):
                bmp_files.append(obj)

    return xml_files, unicode_files, bmp_files


def print_results(xml_files, unicode_files, bmp_files):
    print("\n" + "="*60)
    print("Fisiere XML ASCII:")
    print("="*60)
    if xml_files:
        for f in xml_files:
            print(f"  {f.get_path()}  [primul tag: <{f.get_first_tag()}>]")
    else:
        print("  (niciun fisier gasit)")

    print("\n" + "="*60)
    print("Fisiere UNICODE (UTF-16):")
    print("="*60)
    if unicode_files:
        for f in unicode_files:
            print(f"  {f.get_path()}")
    else:
        print("  (niciun fisier gasit)")

    print("\n" + "="*60)
    print("Fisiere BMP:")
    print("="*60)
    if bmp_files:
        for f in bmp_files:
            print(f"  {f.show_info()}")
    else:
        print("  (niciun fisier gasit)")
    print()



def main():
    if len(sys.argv) < 2:
        # daca nu se da argument, folosim directorul curent
        root_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Niciun director specificat. Se foloseste: {root_dir}")
    else:
        root_dir = sys.argv[1]

    if not os.path.isdir(root_dir):
        print(f"Eroare: '{root_dir}' nu este un director valid.")
        sys.exit(1)

    print(f"Scanare director: {root_dir}")
    xml_files, unicode_files, bmp_files = scan_directory(root_dir)
    print_results(xml_files, unicode_files, bmp_files)


if __name__ == "__main__":
    main()