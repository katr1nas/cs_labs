from lab1 import build_permuted_alphabet, caesar_cipher, keyword_caesar_cipher


def assert_raises(function, *args, contains=None, **kwargs):
    try:
        function(*args, **kwargs)
    except ValueError as error:
        if contains is not None:
            assert contains in str(error)
    else:
        raise AssertionError("ValueError was expected")


def test_basic_encryption():
    assert caesar_cipher(1, "ABC") == "ĂCD"


def test_decryption_round_trip():
    encrypted = caesar_cipher(7, "CIFRUL CEZAR")
    assert caesar_cipher(7, encrypted, decrypt=True) == "CIFRULCEZAR"


def test_wraparound():
    assert caesar_cipher(1, "Z") == "A"
    assert caesar_cipher(30, "A") == "Z"


def test_romanian_letters_and_cedilla_variants():
    assert caesar_cipher(1, "ĂÂÎȘȚ") == "ÂBJTU"
    assert caesar_cipher(1, "ŞŢ") == "TU"


def test_lowercase_and_spaces_are_normalized():
    assert caesar_cipher(1, "a b c") == "ĂCD"


def test_invalid_key():
    for key in (0, 31, -1, "1"):
        assert_raises(caesar_cipher, key, "ABC", contains="1 to 30")


def test_invalid_character_reports_character():
    assert_raises(caesar_cipher, 1, "ABC1", contains="'1'")


def test_permuted_alphabet_contains_all_romanian_letters_once():
    alphabet = build_permuted_alphabet("criptare")
    assert alphabet.startswith("CRIPTAE")  # repeated R appears only once
    assert len(alphabet) == 31
    assert len(set(alphabet)) == 31


def test_keyword_must_have_at_least_seven_letters():
    assert_raises(build_permuted_alphabet, "cheie", contains="at least 7")


def test_keyword_caesar_round_trip():
    encrypted = keyword_caesar_cipher(9, "criptare", "Mesaj Științific")
    assert keyword_caesar_cipher(9, "criptare", encrypted, decrypt=True) == "MESAJȘTIINȚIFIC"


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_") and callable(test):
            test()
    print("All tests passed!")
