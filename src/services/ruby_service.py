import html
import jaconv
import re
from typing import List, Dict
from .nlp_service import NLPService

KANJI_RE = re.compile(r'[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]')

# --- helpers ---------------------------------------------------------------

def _is_kana(ch: str) -> bool:
    """
    Check if a character is a Kana character (Hiragana or Katakana).
    :param ch: The character to check.
    :return: A boolean indicating if the character is Kana.
    """
    return '\u3040' <= ch <= '\u30FF'

def _split_okurigana(token: str):
    """
    Split <prefix_kana><kanji_core><suffix_kana> -->
           (prefix, kanji_core, suffix)

    Either prefix or suffix can be "".
    """
    # strip prefix kana
    i = 0
    while i < len(token) and _is_kana(token[i]):
        i += 1
    prefix = token[:i]

    # strip suffix kana
    j = len(token)
    while j > i and _is_kana(token[j - 1]):
        j -= 1
    suffix = token[j:]
    core = token[i:j]           # may be 1-char kanji, or multi-kanji string

    return prefix, core, suffix

def _add_reading(surface: str, reading: str) -> str:
    """
    Annotate one token (`surface`) with its GiNZA reading (`reading`).

    Handles arbitrary mixes of kanji / kana by consuming reading syllables
    until the next kana in *surface* (or the end of the token).
    """
    reading_hira = jaconv.kata2hira(reading)
    out, kanji_buf = [], []
    s_idx = r_idx = 0

    def flush(up_to: int):
        """Emit the buffered kanji + their reading slice [r_idx : up_to)."""
        nonlocal kanji_buf, r_idx
        if kanji_buf:
            core = ''.join(kanji_buf)
            out.append(
                f"<ruby><rb>{html.escape(core)}</rb>"
                f"<rt>{html.escape(reading_hira[r_idx:up_to])}</rt></ruby>"
            )
            kanji_buf.clear()
            r_idx = up_to

    while s_idx < len(surface):
        ch = surface[s_idx]

        if KANJI_RE.match(ch):
            kanji_buf.append(ch)
            s_idx += 1
            continue

        next_pos = reading_hira.find(jaconv.kata2hira(ch), r_idx)
        if next_pos == -1:
            next_pos = len(reading_hira)

        flush(next_pos)
        out.append(html.escape(ch))
        r_idx = next_pos + 1
        s_idx += 1

    flush(len(reading_hira))
    return ''.join(out)


# --- main class ------------------------------------------------------------

# TODO : Add a docstring, Filters for omitting words.
class RubyService(NLPService):
    """
    RubyService is a subclass of NLPService that provides focuses on
    functionality for handling Ruby (reading) information.
    """
    def __init__(self, spacy_model: str = 'ja_ginza_electra'):
        super().__init__(spacy_model)
        self._mode = "hiragana"


    def annotate_html(self, text: str) -> str:
        """
        Wrap each Kanji‐containing token in <ruby> tags with its reading
        and leave all other tokens (Hiragana, Katakana, numbers…) untouched.
        :param text: The Japanese text to annotate.
        :return: An HTML string with ruby annotations.
        """
        tokenized_text = self.tokenize(text)
        parts: List[str] = []

        for token in tokenized_text:
            surface = token['surface']
            reading = token['reading']

            if not KANJI_RE.search(surface):
                parts.append(html.escape(surface))
                continue

            parts.append(_add_reading(surface, reading))

        return ''.join(parts)

    def set_mode(self, mode: str):
        """
        Set the reading mode for the RubyService.
        :param mode: The reading mode to set ('hiragana' or 'romaji').
        """
        if mode == "hiragana" or mode == "romaji" or mode == "katakana":
            self._mode = mode
        else:
            raise ValueError("Invalid mode. Use 'hiragana' or 'romaji'.")
