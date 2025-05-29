import spacy
from spacy.lang.ja import JapaneseTokenizer
from pykakasi import kakasi
from typing import List, Dict
from functools import lru_cache

# Testing Models
# ja_ginza_electra
# ja_core_news_trf

class NLPService:
    def __init__(self,
                 spacy_model: str = "ja_core_news_trf",
                 split_mode: str = "A"):
        spacy.prefer_gpu()
        self.nlp = spacy.load(spacy_model)
        self.nlp.tokenizer = JapaneseTokenizer(self.nlp.vocab,
                                               split_mode=split_mode)
        self.fallback = kakasi()

        self._convert_cache = lru_cache(maxsize=10000)(self._convert_reading)

    def _convert_reading(self, surface: str) -> str:
        fb = self.fallback.convert(surface)
        return ''.join(item["kana"] for item in fb) if fb else None

    def _token_to_dict(self, token) -> Dict:
        surface = token.text
        reading = token.morph.get("Reading")
        if reading:
            reading = reading[0]
        if surface == reading:
            reading = self._convert_cache(surface)
        return {
            "surface":  surface,
            "reading":  reading,
            "lemma":    token.lemma_,
            "pos":      token.pos_,
            "tag":      token.tag_,
            "dep":      token.dep_,
            "head":     token.head.text,
            "morph":    token.morph.to_dict(),
            "offset":   token.idx,
            "ent_iob":  token.ent_iob_,
            "ent_type": token.ent_type_,
        }

    def tokenize_batch(self, texts: List[str]) -> List[List[Dict]]:
        docs = self.nlp.pipe(texts, batch_size=len(texts))
        return [
            [self._token_to_dict(tok) for tok in doc]
            for doc in docs
        ]