"""Automated tests for lab2.py. Run: python3 -m unittest -v lab2_tests.py"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

import lab2


class Lab2Tests(unittest.TestCase):
    def test_single_letter_frequencies_ignore_case_and_punctuation(self):
        self.assertEqual(lab2.frequencies('Aa, b! 123'), {'A': 2, 'B': 1})

    def test_bigrams_do_not_cross_word_boundaries(self):
        self.assertEqual(lab2.frequencies('AB AB!', 2), {'AB': 2})

    def test_trigrams(self):
        self.assertEqual(lab2.frequencies('THE THE', 3), {'THE': 2})

    def test_short_words_produce_no_trigrams(self):
        self.assertFalse(lab2.frequencies('A BC', 3))

    def test_frequency_guess_is_complete_bijection(self):
        guess = lab2.frequency_guess('AAAA BBB CC D')
        self.assertEqual(set(guess), set(lab2.ALPHABET))
        self.assertEqual(set(guess.values()), set(lab2.ALPHABET))
        self.assertEqual(guess['A'], lab2.ENGLISH_ORDER[0])

    def test_decode_preserves_case_and_punctuation(self):
        self.assertEqual(lab2.decode('Ab! B-a 42', {'A': 'T', 'B': 'H'}), 'Th! H-t 42')

    def test_decode_unknown_letters(self):
        self.assertEqual(lab2.decode('ABC', {'A': 'T'}), 'T__')
        self.assertEqual(lab2.decode('AbC', {'A': 'T'}, unknown='?'), 'T??')

    def test_set_pair_normalizes_lowercase(self):
        mapping = {}
        lab2.set_pair(mapping, 'w', 't')
        self.assertEqual(mapping, {'W': 'T'})

    def test_set_pair_rejects_invalid_characters(self):
        for c, p in [('1', 'A'), ('A', '?'), ('AB', 'C'), ('A', 'BC')]:
            with self.subTest(cipher=c, plain=p):
                with self.assertRaises(ValueError):
                    lab2.set_pair({}, c, p)

    def test_set_pair_rejects_duplicate_plaintext_letter(self):
        mapping = {'A': 'T'}
        with self.assertRaises(ValueError):
            lab2.set_pair(mapping, 'B', 'T')
        self.assertEqual(mapping, {'A': 'T'})

    def test_set_pair_can_change_existing_assignment(self):
        mapping = {'A': 'T'}
        lab2.set_pair(mapping, 'A', 'H')
        self.assertEqual(mapping, {'A': 'H'})

    def test_v2_key_is_permutation(self):
        self.assertEqual(len(lab2.V2_KEY), 26)
        self.assertEqual(set(lab2.V2_KEY), set(lab2.ALPHABET))

    def test_v2_decrypt_known_opening(self):
        self.assertEqual(lab2.decrypt_v2('Wqv tooxwxng nc pvhivhf'),
                         'The addition of secrecy')

    def test_v2_preserves_nonletters(self):
        self.assertEqual(lab2.decrypt_v2('Wqv, 123!'), 'The, 123!')

    def test_statistics_runs_on_valid_input(self):
        output = StringIO()
        with patch('sys.stdout', output):
            lab2.show_statistics('THE THE')
        self.assertIn('Letters analyzed: 6', output.getvalue())
        self.assertIn('Top 2-grams:', output.getvalue())
        self.assertIn('Top 3-grams:', output.getvalue())

    def test_saved_v2_mapping_matches_key(self):
        path = Path(__file__).with_name('v2_mapping.txt')
        if not path.exists():
            self.skipTest('v2_mapping.txt is not available')
        mapping = {}
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.strip() and not line.lstrip().startswith('#'):
                c, p = line.split('=', 1)
                lab2.set_pair(mapping, c.strip(), p.strip())
        self.assertEqual(''.join(mapping[c] for c in lab2.ALPHABET), lab2.V2_KEY)


if __name__ == '__main__':
    unittest.main(verbosity=2)
