import spacy
from typing import List, Dict

class NLPService:
    def __init__(self, spacy_model: str = 'ja_ginza_electra'):
        self.nlp = spacy.load(spacy_model)

    def tokenize(self, text: str) -> List[Dict]:
        """
        Japanese tokenization and reading processing of the texts using GiNZA.
        :param text: The Japanese text to tokenize.
        :return: The tokenized text as a list of dictionaries with 'surface' and 'reading'.
        """
        results = []
        parsed_text = self.nlp(text)
        for token in parsed_text:
            reading = token.morph.get("Reading")
            results.append({
                "surface": token.text,
                "reading": reading[0] if reading else None
            })
        return results
