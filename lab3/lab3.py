ALPHABET = "AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ"
LATIN = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
N = len(ALPHABET)
IDX = {c: i for i, c in enumerate(ALPHABET)}
MIN_KEY = 7
ROWS, COLS = 4, 8
FILLER = "_"
NORMALIZE = str.maketrans({"Ş": "Ș", "ş": "ș", "Ţ": "Ț", "ţ": "ț"})


def normalize(text):
    return "".join(text.translate(NORMALIZE).split()).upper()


def invalid_chars(text, allowed):
    return sorted({c for c in text if c not in allowed})


def vigenere(text, key, decrypt=False):
    sign = -1 if decrypt else 1
    return "".join(
        ALPHABET[(IDX[c] + sign * IDX[key[i % len(key)]]) % N]
        for i, c in enumerate(text)
    )


def build_square(key):
    cells = []
    for c in key + ALPHABET:
        if c not in cells:
            cells.append(c)
    cells.append(FILLER)
    return cells


def prepare_pairs(text):
    pairs = []
    i = 0
    while i < len(text):
        a = text[i]
        b = text[i + 1] if i + 1 < len(text) else None
        if b is None or a == b:
            pairs.append(a + ("Q" if a == "X" else "X"))
            i += 1
        else:
            pairs.append(a + b)
            i += 2
    return pairs


def transform_pair(pair, square, pos, step):
    a, b = pair
    ra, ca = divmod(pos[a], COLS)
    rb, cb = divmod(pos[b], COLS)
    if ra == rb:
        return (
            square[ra * COLS + (ca + step) % COLS]
            + square[rb * COLS + (cb + step) % COLS]
        )
    if ca == cb:
        return (
            square[((ra + step) % ROWS) * COLS + ca]
            + square[((rb + step) % ROWS) * COLS + cb]
        )
    return square[ra * COLS + cb] + square[rb * COLS + ca]


def playfair(text, key, decrypt=False):
    square = build_square(key)
    pos = {c: i for i, c in enumerate(square)}
    if decrypt:
        if len(text) % 2:
            raise ValueError("Ciphertext length must be even.")
        pairs = [text[i:i + 2] for i in range(0, len(text), 2)]
        if any(p[0] == p[1] for p in pairs):
            raise ValueError("Ciphertext contains a pair of identical letters.")
    else:
        pairs = prepare_pairs(text)
    step = -1 if decrypt else 1
    return "".join(transform_pair(p, square, pos, step) for p in pairs)


def show_square(key):
    square = build_square(key)
    return "\n".join(
        " ".join(square[r * COLS:(r + 1) * COLS]) for r in range(ROWS)
    )


def read_text(prompt, allowed, label, min_len=0):
    while True:
        text = normalize(input(prompt))
        bad = invalid_chars(text, allowed)
        if bad:
            print(f"Invalid characters in {label}: {' '.join(bad)}")
            print("Allowed range: 'A'-'Z' and 'a'-'z' only.")
            continue
        if not text:
            print(f"The {label} must not be empty.")
            continue
        if len(text) < min_len:
            print(f"The {label} must contain at least {min_len} letters.")
            continue
        return text


def choose(prompt, options):
    while True:
        value = input(prompt).strip()
        if value in options:
            return value
        print(f"Enter one of: {', '.join(options)}")


def main():
    print("1 - Playfair (task 3.1)")
    print("2 - Vigenere (task 3.2)")
    algo = choose("Algorithm: ", ("1", "2"))
    print("1 - Encrypt")
    print("2 - Decrypt")
    op = choose("Operation: ", ("1", "2"))
    decrypt = op == "2"
    key = read_text("Key (min 7 letters): ", LATIN, "key", MIN_KEY)
    allowed = set(ALPHABET) if decrypt else LATIN
    label = "ciphertext" if decrypt else "message"
    text = read_text(f"Enter {label}: ", allowed, label)
    try:
        if algo == "1":
            print("Matrix:")
            print(show_square(key))
            result = playfair(text, key, decrypt)
        else:
            result = vigenere(text, key, decrypt)
    except ValueError as e:
        print(e)
        return
    print("Result:", result)


if __name__ == "__main__":
    main()
