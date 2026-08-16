"""Treina um classificador log-odds e exporta pesos quantizados para MicroPython."""

from collections import Counter, defaultdict
from math import log
from pathlib import Path
import argparse
import sys


PROJECT_DIR = Path(__file__).resolve().parents[1]
FIRMWARE_DIR = PROJECT_DIR / "firmware"
sys.path.insert(0, str(FIRMWARE_DIR))

from text_processing import make_features  # noqa: E402
from dataset import EXAMPLES  # noqa: E402


SCALE = 8
ALPHA = 1.0
MIN_MARGIN = 2


def train(examples):
    labels = sorted({label for _, label in examples})
    document_counts = Counter()
    token_counts = defaultdict(Counter)
    vocabulary = set()

    for text, label in examples:
        features = set(make_features(text))
        document_counts[label] += 1
        token_counts[label].update(features)
        vocabulary.update(features)

    vocabulary = sorted(vocabulary)
    total_documents = len(examples)
    label_count = len(labels)

    biases = [0] * label_count
    weights = []

    for token in vocabulary:
        for label in labels:
            in_class = token_counts[label][token]
            outside_class = sum(
                token_counts[other_label][token]
                for other_label in labels
                if other_label != label
            )
            probability_in = (in_class + ALPHA) / (
                document_counts[label] + 2 * ALPHA
            )
            probability_out = (outside_class + ALPHA) / (
                total_documents - document_counts[label] + 2 * ALPHA
            )
            quantized = round(log(probability_in / probability_out) * SCALE)
            quantized = max(-128, min(127, quantized))
            weights.append(quantized)

    return labels, vocabulary, biases, weights


def score_text(text, labels, vocabulary, biases, weights):
    lookup = {token: index for index, token in enumerate(vocabulary)}
    scores = list(biases)
    used = set()

    for token in make_features(text):
        token_index = lookup.get(token)
        if token_index is None or token_index in used:
            continue
        used.add(token_index)
        offset = token_index * len(labels)
        for label_index in range(len(labels)):
            scores[label_index] += weights[offset + label_index]

    if not used:
        return "desconhecido", 0

    order = sorted(range(len(scores)), key=scores.__getitem__, reverse=True)
    margin = scores[order[0]] - scores[order[1]]
    label = labels[order[0]]
    if label != "desconhecido" and margin < MIN_MARGIN:
        label = "desconhecido"
    return label, margin


def format_tuple(values):
    return repr(tuple(values))


def export_model(output, labels, vocabulary, biases, weights):
    encoded_weights = [value if value >= 0 else value + 256 for value in weights]
    lines = [
        '"""Arquivo gerado por training/train.py. Não edite manualmente."""',
        "",
        "LABELS = " + format_tuple(labels),
        "VOCABULARY = " + format_tuple(vocabulary),
        "BIASES = " + format_tuple(biases),
        "SCALE = " + str(SCALE),
        "MIN_MARGIN = " + str(MIN_MARGIN),
        "WEIGHTS = (",
    ]

    # Literal binário: evita construir uma tupla com milhares de inteiros
    # temporários durante o import no heap pequeno do MicroPython.
    width = 32
    for index in range(0, len(encoded_weights), width):
        chunk = encoded_weights[index:index + width]
        literal = "".join("\\x{:02x}".format(value) for value in chunk)
        lines.append('    b"' + literal + '"')
    lines.extend((")", ""))

    output.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=FIRMWARE_DIR / "model_data.py",
        help="Destino do modelo MicroPython.",
    )
    args = parser.parse_args()

    labels, vocabulary, biases, weights = train(EXAMPLES)
    export_model(args.output, labels, vocabulary, biases, weights)

    correct = 0
    mistakes = []
    for text, expected in EXAMPLES:
        predicted, margin = score_text(
            text, labels, vocabulary, biases, weights
        )
        if predicted == expected:
            correct += 1
        else:
            mistakes.append((text, expected, predicted, margin))

    accuracy = correct / len(EXAMPLES)
    print("Modelo exportado para:", args.output)
    print("Classes:", len(labels))
    print("Vocabulário:", len(vocabulary))
    print("Pesos int8:", len(weights), "bytes")
    print("Acurácia no conjunto de treino: {:.1%}".format(accuracy))
    if mistakes:
        print("Erros de treino:")
        for mistake in mistakes:
            print("  ", mistake)


if __name__ == "__main__":
    main()
