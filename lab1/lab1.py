
ROMANIAN_ALPHABET = "AĂÂBCDEFGHIÎJKLMNOPQRSȘTȚUVWXYZ"

LETTER_VARIANTS = str.maketrans({"Ş": "Ș", "ş": "ș", "Ţ": "Ț", "ţ": "ț"})


def validate_key(key):
    if not isinstance(key, int) or isinstance(key, bool) or not 1 <= key <= 30:
        raise ValueError("Key must be an integer from 1 to 30.")


def normalize_text(text, allow_spaces=True, field_name="Text"):
    if not isinstance(text, str):
        raise ValueError(f"{field_name} must be a string.")

    normalized = text.translate(LETTER_VARIANTS).upper()
    result = []
    for character in normalized:
        if character == " " and allow_spaces:
            continue
        if character not in ROMANIAN_ALPHABET:
            raise ValueError(
                f"Invalid character {character!r} in {field_name}. "
                "Use only Romanian alphabet letters."
            )
        result.append(character)
    return "".join(result)


def caesar_cipher(key, text, decrypt=False, alphabet=ROMANIAN_ALPHABET):
    validate_key(key)
    normalized_text = normalize_text(text)
    index_by_letter = {letter: index for index, letter in enumerate(alphabet)}
    shift = -key if decrypt else key

    return "".join(
        alphabet[(index_by_letter[character] + shift) % len(alphabet)]
        for character in normalized_text
    )


def build_permuted_alphabet(keyword):
    normalized_keyword = normalize_text(
        keyword, allow_spaces=False, field_name="Keyword"
    )
    if len(normalized_keyword) < 7:
        raise ValueError("Keyword must contain at least 7 Romanian letters.")

    unique_keyword = "".join(dict.fromkeys(normalized_keyword))
    remaining_letters = "".join(
        letter for letter in ROMANIAN_ALPHABET if letter not in unique_keyword
    )
    return unique_keyword + remaining_letters


def keyword_caesar_cipher(key, keyword, text, decrypt=False):
    permuted_alphabet = build_permuted_alphabet(keyword)
    return caesar_cipher(key, text, decrypt=decrypt, alphabet=permuted_alphabet)


def read_key():
    while True:
        raw_key = input("Key (1-30): ")
        try:
            key = int(raw_key)
            validate_key(key)
            return key
        except ValueError:
            print("Invalid key. Enter an integer from 1 to 30.")


def read_keyword():
    while True:
        keyword = input("Keyword (at least 7 Romanian letters): ")
        try:
            return keyword, build_permuted_alphabet(keyword)
        except ValueError as error:
            print(error)


def read_operation():
    while True:
        operation = input("Operation: [E]ncrypt or [D]ecrypt: ").strip().upper()
        if operation in {"E", "ENCRYPT"}:
            return False
        if operation in {"D", "DECRYPT"}:
            return True
        print("Invalid operation. Enter E for encrypt or D for decrypt.")


def main():
    print("Romanian Caesar Cipher")
    while True:
        task = input("Choose task: [1] simple Caesar, [2] keyword Caesar: ").strip()
        if task in {"1", "2"}:
            break
        print("Invalid choice. Enter 1 or 2.")

    decrypt = read_operation()
    key = read_key()
    keyword = None
    if task == "2":
        keyword, permuted_alphabet = read_keyword()
        print(f"Permuted alphabet: {permuted_alphabet}")

    while True:
        text = input("Text: ")
        try:
            if keyword is None:
                result = caesar_cipher(key, text, decrypt=decrypt)
            else:
                result = keyword_caesar_cipher(key, keyword, text, decrypt=decrypt)
            print(f"Result: {result}")
            return
        except ValueError as error:
            print(error)


if __name__ == "__main__":
    main()
