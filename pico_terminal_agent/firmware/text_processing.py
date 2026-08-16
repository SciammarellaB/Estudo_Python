"""Processamento de texto compartilhado pelo treino e pela Raspberry Pi Pico."""


_REPLACEMENTS = (
    ("á", "a"), ("à", "a"), ("ã", "a"), ("â", "a"),
    ("é", "e"), ("ê", "e"),
    ("í", "i"),
    ("ó", "o"), ("õ", "o"), ("ô", "o"),
    ("ú", "u"), ("ü", "u"),
    ("ç", "c"),
)

_PUNCTUATION = ".,!?;:()[]{}\"'/-_+=*\r\n\t"

_STOPWORDS = {
    "a", "as", "com", "da", "das", "de", "do", "dos", "e", "em",
    "faca", "me", "mim", "na", "nas", "no", "nos", "o", "os",
    "para", "pode", "por", "quero", "um", "uma",
}


def normalize(text):
    """Converte uma frase para uma representação simples e determinística."""
    text = text.lower().strip()

    for source, target in _REPLACEMENTS:
        text = text.replace(source, target)

    for character in _PUNCTUATION:
        text = text.replace(character, " ")

    return " ".join(text.split())


def make_features(text):
    """Retorna unigramas e bigramas usados pelo classificador."""
    normalized = normalize(text)
    if not normalized:
        return []

    words = []
    for word in normalized.split():
        if word not in _STOPWORDS:
            words.append(word)
    features = list(words)

    for index in range(len(words) - 1):
        features.append(words[index] + "__" + words[index + 1])

    return features
