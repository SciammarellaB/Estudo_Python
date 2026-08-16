"""Inferência do classificador TinyML quantizado."""

from model_data import BIASES, LABELS, MIN_MARGIN, VOCABULARY, WEIGHTS
from text_processing import make_features


def _signed(byte_value):
    return byte_value - 256 if byte_value > 127 else byte_value


class TinyIntentClassifier:
    """Classificador log-odds quantizado, treinado fora e inferido na Pico."""

    def __init__(self):
        self._lookup = {}
        for index, token in enumerate(VOCABULARY):
            self._lookup[token] = index
        self._label_count = len(LABELS)

    def predict(self, text):
        scores = list(BIASES)
        used_indexes = set()

        for token in make_features(text):
            token_index = self._lookup.get(token)
            if token_index is None or token_index in used_indexes:
                continue

            used_indexes.add(token_index)
            offset = token_index * self._label_count
            for label_index in range(self._label_count):
                scores[label_index] += _signed(WEIGHTS[offset + label_index])

        if not used_indexes:
            return {
                "intent": "desconhecido",
                "margin": 0,
                "known_features": 0,
            }

        best_index = 0
        second_index = 1
        if scores[second_index] > scores[best_index]:
            best_index, second_index = second_index, best_index

        for index in range(2, len(scores)):
            if scores[index] > scores[best_index]:
                second_index = best_index
                best_index = index
            elif scores[index] > scores[second_index]:
                second_index = index

        margin = scores[best_index] - scores[second_index]
        intent = LABELS[best_index]

        if intent != "desconhecido" and margin < MIN_MARGIN:
            intent = "desconhecido"

        return {
            "intent": intent,
            "margin": margin,
            "known_features": len(used_indexes),
        }
