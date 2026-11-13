"""
V2 tools for the free laptop assistant (Windows).
Only tools.py is new - main.py already calls these functions.
All functions return a short message in English.
Nothing runs without the user typing the command first, except
power-off, which always asks for a second confirmation first.

Install for V2 (all free):
    pip install requests pyautogui screen_brightness_control pyperclip pywhatkit

PDF and Word files need no extra install at all (built with Python only).
python-docx and fpdf2 are deliberately NOT used, because pip could not
resolve their Pillow / lxml dependencies on Python 3.14.

pywhatkit is only for WhatsApp, and only works if WhatsApp Web is
already logged in on the laptop browser.
"""

import os
import subprocess
import sys
import webbrowser

# Common Windows apps. Add your own here, e.g. "vscode": "Code.exe"
KNOWN_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "terminal": "cmd.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "firefox": "firefox.exe",
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
    "spotify": "Spotify.exe",
}


def open_app(name):
    """Open an app by name, e.g. open_app('notepad'). Windows only for .exe."""
    name = (name or "").strip().lower()
    if not name:
        return "Which app should I open? For example: notepad kholo"
    if name in ("browser", "google chrome"):
        webbrowser.open("https://www.google.com")
        return "Browser opened."
    exe = KNOWN_APPS.get(name, name)
    try:
        if sys.platform == "win32":
            os.startfile(exe)  # noqa: S606 - user-typed app name, local only
        else:
            subprocess.Popen([exe])
        return f"Opened {name}."
    except Exception:
        return (f"Could not open {name}. It may not be installed, "
                f"or the name may be wrong. For a browser, type 'browser kholo'.")


def google_search(query):
    query = (query or "").strip()
    if not query:
        return "What should I search on Google? For example: google search python"
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Opened a Google search for: {query}"


def open_ai_site(site, query=""):
    """Open an AI site. Auto-typing inside a logged-in AI chat is not
    reliable, so this opens the site; the user can paste the question.
    The local assistant itself (Ollama) can already answer without this."""
    sites = {
        "chatgpt": "https://chatgpt.com/",
        "muse": "https://muse.ai/",
        "grok": "https://grok.com/",
        "gemini": "https://gemini.google.com/",
        "copilot": "https://copilot.microsoft.com/",
    }
    url = sites.get((site or "").strip().lower())
    if not url:
        return "Which AI should I open? Type chatgpt, muse, grok, gemini or copilot."
    webbrowser.open(url)
    if query:
        return (f"Opened {site}. Paste your question there: {query}\n"
                "Note: AI sites need a login, and auto-typing does not "
                "always work, so pasting your question there is better.")
    return f"Opened {site}."


def change_volume(direction):
    """direction: 'up' or 'down'. Uses media keys via pyautogui."""
    try:
        import pyautogui
    except ImportError:
        return "For volume, first install this: pip install pyautogui"
    try:
        key = "volumeup" if direction == "up" else "volumedown"
        pyautogui.press(key)
        return "Volume up." if direction == "up" else "Volume down."
    except Exception:
        return "Could not change the volume. Try your laptop volume buttons."


def change_brightness(action, value=None):
    """action: 'set' with value 0-100, 'up' (+20) or 'down' (-20)."""
    try:
        import screen_brightness_control as sbc
    except ImportError:
        return ("For brightness, first install this: "
                "pip install screen_brightness_control")
    try:
        if action == "set" and value is not None:
            value = max(0, min(100, int(value)))
            sbc.set_brightness(value)
            return f"Brightness set to {value}%."
        current = sbc.get_brightness()
        current = current[0] if isinstance(current, list) and current else 50
        new = max(0, min(100, current + 20 if action == "up" else current - 20))
        sbc.set_brightness(new)
        return f"Brightness set to {new}%."
    except Exception:
        return ("Could not change the brightness. On some laptops this "
                "only works in Windows Settings > Display.")


def shutdown_laptop(confirmed=False):
    """Two-step shutdown. First call returns a confirmation prompt."""
    if not confirmed:
        return ("Are you sure I should shut the laptop down? If yes, type: "
                "power off pakka\n"
                "This step is here so the laptop does not shut down by mistake.")
    try:
        if sys.platform == "win32":
            os.system("shutdown /s /t 5")
        else:
            os.system("shutdown -h +0")
        return "Shutting the laptop down. Goodbye!"
    except Exception:
        return "Could not shut the laptop down."


def whatsapp_message(text):
    """Expected format: whatsapp +923001234567 : apka message
    Needs WhatsApp Web already logged in on the browser."""
    try:
        number, _, message = text.partition(":")
        number = number.replace("whatsapp", "").strip()
        message = message.strip()
        if not number or not message:
            return ("Type it like this: whatsapp +923001234567 : Hello, how are you?\n"
                    "The number needs its country code.")
        try:
            import pywhatkit
        except ImportError:
            return ("For WhatsApp, first install this: "
                    "pip install pywhatkit\n"
                    "Then you need to be logged in to WhatsApp Web in your browser.")
        pywhatkit.sendwhatmsg_instantly(number, message, 15, True, 5)
        return f"WhatsApp message sent to {number}."
    except Exception:
        return ("Could not send the WhatsApp message. Check that WhatsApp Web "
                "is logged in in your browser and that the number is correct.")


def _document_path(kind):
    """A timestamped file in the same folder as tools.py, e.g. assistant_....pdf"""
    from datetime import datetime

    base = os.path.dirname(os.path.abspath(__file__))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(base, f"assistant_{stamp}.{kind}")


def _clean_for_pdf(text):
    """PDF's built-in Helvetica font only handles Latin letters, so
    replace the few fancy characters (curly quotes, long dashes) with
    plain ones. English text is Latin script, so it survives unchanged."""
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u2022": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _escape_pdf_text(text):
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _write_simple_pdf(path, text, title=None):
    """Write a plain text PDF using only Python's standard library.
    No pip install is needed for PDF at all. This deliberately avoids
    fpdf2, whose Pillow dependency pip could not resolve on this
    laptop's Python 3.14 install (see the pip backtracking error)."""
    import textwrap

    lines = []  # (text, font_size, bold)
    if title:
        for line in textwrap.wrap(_clean_for_pdf(title), width=60,
                                  break_long_words=True, break_on_hyphens=False):
            lines.append((line, 16, True))
        lines.append(("", 12, False))
    for paragraph in _clean_for_pdf(text).split("\n"):
        wrapped = textwrap.wrap(paragraph, width=82,
                                break_long_words=True, break_on_hyphens=False)
        if not wrapped:
            lines.append(("", 12, False))
        else:
            for line in wrapped:
                lines.append((line, 12, False))

    # Split lines into A4 pages (595 x 842 points, 50pt margins).
    pages, current, y = [], [], 792
    for line_text, size, bold in lines:
        height = 22 if size >= 16 else 16
        if y - height < 50:
            pages.append(current)
            current, y = [], 792
        current.append((line_text, size, bold, y))
        y -= height
    if current or not pages:
        pages.append(current)

    objects = []  # bytes, without the "N 0 obj ... endobj" wrapper
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    page_ids = []
    next_id = 5
    for _page in pages:
        page_ids.append(next_id)
        next_id += 2
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("latin-1"))
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    for page_lines, pid in zip(pages, page_ids):
        content_id = pid + 1
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
            f"/Contents {content_id} 0 R >>".encode("latin-1"))
        stream_lines = []
        for line_text, size, bold, line_y in page_lines:
            font = "F2" if bold else "F1"
            stream_lines.append(
                f"BT /{font} {size} Tf 50 {line_y} Td "
                f"({_escape_pdf_text(line_text)}) Tj ET")
        stream = "\n".join(stream_lines).encode("latin-1")
        objects.append(
            f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1")
            + stream + b"\nendstream")

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode("latin-1") + body + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode("latin-1")
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode("latin-1")
    out += (f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n").encode("latin-1")
    with open(path, "wb") as f:
        f.write(out)


def save_as_pdf(text, title=None):
    """Save text as a PDF file. No extra install needed for PDF.
    Returns a short English message."""
    text = (text or "").strip()
    if not text:
        return "What should I save in the PDF? Ask me something first, then write: isay pdf banao"
    try:
        path = _document_path("pdf")
        _write_simple_pdf(path, text, title)
        return f"PDF saved: {path}"
    except Exception:
        return "Could not make the PDF. Try again, or check the file name / folder."


def _write_simple_docx(path, text, title=None):
    """Write a minimal, valid .docx using only Python's standard library.
    A .docx is just a ZIP of XML files. This deliberately avoids
    python-docx, whose lxml dependency pip could not resolve on this
    laptop's Python 3.14 install (same backtracking error as fpdf2).
    The file opens in Word, LibreOffice and Google Docs, and unlike
    the PDF writer it keeps full Unicode, so Urdu script works too."""
    import zipfile
    from xml.sax.saxutils import escape

    def paragraph_xml(content, bold=False, size=None):
        run_props = ""
        if bold or size:
            run_props = "<w:rPr>"
            if bold:
                run_props += "<w:b/>"
            if size:
                run_props += f'<w:sz w:val="{size}"/>'
            run_props += "</w:rPr>"
        return (f"<w:p><w:r>{run_props}<w:t xml:space=\"preserve\">"
                f"{escape(content)}</w:t></w:r></w:p>")

    body = []
    if title:
        body.append(paragraph_xml(title, bold=True, size=32))
        body.append(paragraph_xml(""))
    for paragraph in text.split("\n"):
        body.append(paragraph_xml(paragraph))
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body>" + "".join(body) +
        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>'
        "</w:sectPr></w:body></w:document>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )
    doc_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        "</Relationships>"
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/_rels/document.xml.rels", doc_rels)


def save_as_word(text, title=None):
    """Save text as a Word (.docx) file. No extra install needed.
    Returns a short English message."""
    text = (text or "").strip()
    if not text:
        return "What should I save in Word? Ask me something first, then write: isay word banao"
    try:
        path = _document_path("docx")
        _write_simple_docx(path, text, title)
        return f"Word file saved: {path}"
    except Exception:
        return "Could not make the Word file. Try again, or check the file name / folder."


def get_clipboard_text():
    """Return copied text, so the assistant can explain it in simple English."""
    try:
        import pyperclip
        text = pyperclip.paste() or ""
        if text.strip():
            return text.strip()
    except Exception:
        pass
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        return text.strip()
    except Exception:
        return ""
