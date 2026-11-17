import argparse
from collections import Counter
from pathlib import Path
import re

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ENGLISH = dict(zip(ALPHABET, (
    8.17, 1.49, 2.78, 4.25, 12.70, 2.23, 2.01, 6.09, 6.97,
    0.15, 0.77, 4.03, 2.41, 6.75, 7.51, 1.93, 0.09, 5.99,
    6.33, 9.06, 2.76, 0.98, 2.36, 0.15, 1.97, 0.07,
)))
ENGLISH_ORDER = "".join(sorted(ALPHABET, key=lambda c: (-ENGLISH[c], c)))

V2_KEY = "BQFUJYNCRGVKZODSHWLAPETIXM"
V2_MAPPING = dict(zip(ALPHABET, V2_KEY))


def frequencies(text, n=1):
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValueError("n must be a positive integer")
    if n == 1:
        return Counter(c for c in text.upper() if c in ALPHABET)
    result = Counter()
    for word in re.findall(r"[A-Za-z]+", text.upper()):
        result.update(word[i:i + n] for i in range(len(word) - n + 1))
    return result


def frequency_guess(text):
    counts = frequencies(text)
    ranked = sorted(ALPHABET, key=lambda c: (-counts[c], c))
    return dict(zip(ranked, ENGLISH_ORDER))


def set_pair(mapping, cipher, plain):
    cipher, plain = cipher.upper(), plain.upper()
    if len(cipher) != 1 or len(plain) != 1 or cipher not in ALPHABET or plain not in ALPHABET:
        raise ValueError("Use two English letters, e.g. W T")
    if any(k != cipher and v == plain for k, v in mapping.items()):
        raise ValueError(f"Plaintext letter {plain} is already assigned")
    mapping[cipher] = plain


def decode(text, mapping, unknown="_"):
    result = []
    for char in text:
        if char.upper() not in ALPHABET or len(char) != 1:
            result.append(char)
        else:
            translated = mapping.get(char.upper(), unknown)
            result.append(translated.lower() if char.islower() else translated)
    return "".join(result)


def decrypt_v2(ciphertext):
    return decode(ciphertext, V2_MAPPING)


def load_mapping(path):
    mapping = {}
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.count("=") != 1:
            raise ValueError(f"Invalid mapping at line {line_number}: {line!r}")
        cipher, plain = (part.strip() for part in line.split("=", 1))
        try:
            set_pair(mapping, cipher, plain)
        except ValueError as exc:
            raise ValueError(f"Line {line_number}: {exc}") from exc
    return mapping


def save_mapping(path, mapping):
    Path(path).write_text(
        "".join(f"{c}={mapping[c]}\n" for c in sorted(mapping)), encoding="utf-8"
    )


def show_key(mapping):
    print("Cipher:", ALPHABET)
    print("Plain: ", "".join(mapping.get(c, "_") for c in ALPHABET))
    print(f"Known letters: {len(mapping)}/26")


def show_statistics(text):
    counts = frequencies(text)
    total = sum(counts.values())
    print(f"Letters analyzed: {total}")
    print("Letter | Count | Percentage | English expected")
    for c, count in counts.most_common():
        percentage = 100 * count / total if total else 0
        print(f"   {c}   | {count:5d} | {percentage:8.2f}% | {ENGLISH[c]:6.2f}%")
    for n in (2, 3):
        top = frequencies(text, n).most_common(12)
        print(f"Top {n}-grams:", ", ".join(f"{item}:{count}" for item, count in top))
    single_words = re.findall(r"(?<![A-Za-z])[A-Za-z](?![A-Za-z])", text)
    print("One-letter words:", Counter(c.upper() for c in single_words).most_common())
    print("Frequency-only candidate (NOT a reliable final solution):")
    print(decode(text, frequency_guess(text))[:500])


def interactive(text, initial_mapping=None):
    mapping = dict(initial_mapping or {})
    show_statistics(text)
    print("\nCommands: set C P | remove C | guess | show | key | save PATH | quit")
    while True:
        try:
            parts = input("cryptanalysis> ").strip().split()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not parts:
            continue
        action = parts[0].lower()
        try:
            if action in ("quit", "exit") and len(parts) == 1:
                break
            if action == "set" and len(parts) == 3:
                set_pair(mapping, parts[1], parts[2])
                print(decode(text, mapping))
            elif action == "remove" and len(parts) == 2:
                mapping.pop(parts[1].upper(), None)
                print(decode(text, mapping))
            elif action == "guess" and len(parts) == 1:
                print("Frequency-only suggestion:", frequency_guess(text))
            elif action == "show" and len(parts) == 1:
                print(decode(text, mapping))
            elif action == "key" and len(parts) == 1:
                show_key(mapping)
            elif action == "save" and len(parts) == 2:
                save_mapping(parts[1], mapping)
                print("Mapping saved.")
            else:
                print("Unknown command or wrong number of arguments.")
        except (ValueError, OSError) as exc:
            print("Error:", exc)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ciphertext", type=Path, help="UTF-8 file containing ciphertext")
    parser.add_argument("--decrypt-v2", action="store_true", help="decrypt variant V2 with its recovered key")
    parser.add_argument("--mapping", type=Path, help="load a C=P mapping file")
    parser.add_argument("--output", type=Path, help="save decoded text (with --mapping or --decrypt-v2)")
    args = parser.parse_args(argv)
    if args.output and not (args.mapping or args.decrypt_v2):
        parser.error("--output requires --mapping or --decrypt-v2")
    if args.mapping and args.decrypt_v2:
        parser.error("--mapping cannot be combined with --decrypt-v2")
    try:
        text = args.ciphertext.read_text(encoding="utf-8")
        if args.decrypt_v2:
            plaintext = decrypt_v2(text)
            print(plaintext)
            if args.output:
                args.output.write_text(plaintext, encoding="utf-8")
        else:
            mapping = load_mapping(args.mapping) if args.mapping else {}
            if args.output:
                args.output.write_text(decode(text, mapping), encoding="utf-8")
                print(f"Decrypted text saved to {args.output}")
            else:
                interactive(text, mapping)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
