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

# --- main class ------------------------------------------------------------

# TODO : Add a docstring, Filters for omitting words.
class RubyService(NLPService):
    """
    RubyService is a subclass of NLPService that provides focuses on
    functionality for handling Ruby (reading) information.
    """
    def __init__(self, spacy_model: str = 'ja_ginza_electra'):
        super().__init__(spacy_model)


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

            reading_hira = jaconv.kata2hira(reading)
            prefix, core, suffix = _split_okurigana(surface)

            if core and reading_hira.startswith(jaconv.hira2kata(prefix)) and reading_hira.endswith(suffix):
                core_reading = reading_hira[len(prefix):len(reading_hira) - len(suffix)]
            else:
                prefix = ""
                core = surface
                suffix = ""
                core_reading = reading_hira

            if prefix:
                parts.append(html.escape(prefix))

            parts.append(
                f"<ruby><rb>{html.escape(core)}</rb>"
                f"<rt>{html.escape(core_reading)}</rt></ruby>"
            )

            if suffix:
                parts.append(html.escape(suffix))

        return ''.join(parts)
