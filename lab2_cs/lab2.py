"""Lab 2: interactive monoalphabetic substitution cryptanalysis (English)."""
import argparse
from collections import Counter
from pathlib import Path
import re

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ENGLISH = dict(zip(ALPHABET, [8.17,1.49,2.78,4.25,12.70,2.23,2.01,6.09,6.97,0.15,0.77,4.03,2.41,6.75,7.51,1.93,0.09,5.99,6.33,9.06,2.76,0.98,2.36,0.15,1.97,0.07]))
ENGLISH_ORDER = ''.join(sorted(ALPHABET, key=lambda c: -ENGLISH[c]))

def frequencies(text, n=1):
    if n == 1:
        items = [c for c in text.upper() if c in ALPHABET]
    else:
        items = []
        for word in re.findall(r'[A-Za-z]+', text.upper()):
            items.extend(word[i:i+n] for i in range(len(word)-n+1))
    return Counter(items)

def frequency_guess(text):
    ranked = sorted(ALPHABET, key=lambda c: (-frequencies(text)[c], c))
    return dict(zip(ranked, ENGLISH_ORDER))

def decode(text, mapping, unknown='_'):
    return ''.join((mapping.get(c.upper(), unknown).lower() if c.islower() else mapping.get(c, unknown)) if c.upper() in ALPHABET else c for c in text)

def set_pair(mapping, cipher, plain):
    cipher, plain = cipher.upper(), plain.upper()
    if len(cipher) != 1 or len(plain) != 1 or cipher not in ALPHABET or plain not in ALPHABET:
        raise ValueError('Use two English letters, e.g. W T')
    if any(k != cipher and v == plain for k, v in mapping.items()):
        raise ValueError(f'Plaintext letter {plain} is already assigned')
    mapping[cipher] = plain

def show_statistics(text):
    counts = frequencies(text)
    total = sum(counts.values())
    print(f'Letters analyzed: {total}')
    print('Letter | Count | Percentage | English expected')
    for c, count in counts.most_common():
        print(f'   {c}   | {count:5d} | {100*count/total:8.2f}% | {ENGLISH[c]:6.2f}%')
    for n in (2, 3):
        print(f'Top {n}-grams:', ', '.join(f'{x}:{k}' for x,k in frequencies(text,n).most_common(12)))
    print('One-letter words:', frequencies(' '.join(re.findall(r'\b[A-Za-z]\b', text))).most_common())
    print('Frequency-only candidate (NOT a reliable final solution):')
    print(decode(text, frequency_guess(text))[:500])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ciphertext', type=Path, help='UTF-8 file containing the assigned ciphertext')
    parser.add_argument('--mapping', type=Path, help='Optional saved substitution key (C=P per line)')
    args = parser.parse_args()
    text = args.ciphertext.read_text(encoding='utf-8')
    mapping = {}
    if args.mapping and args.mapping.exists():
        for line in args.mapping.read_text(encoding='utf-8').splitlines():
            if line.strip() and not line.lstrip().startswith('#'):
                c, p = line.split('=', 1)
                set_pair(mapping, c.strip(), p.strip())
    show_statistics(text)
    print('\nCommands: set C P | remove C | guess | show | key | save PATH | quit')
    while True:
        try:
            cmd = input('cryptanalysis> ').strip().split()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not cmd: continue
        try:
            if cmd[0] == 'quit': break
            elif cmd[0] == 'set' and len(cmd) == 3: set_pair(mapping, cmd[1], cmd[2])
            elif cmd[0] == 'remove' and len(cmd) == 2: mapping.pop(cmd[1].upper(), None)
            elif cmd[0] == 'guess':
                print('Suggested cipher-to-plain mappings:', frequency_guess(text))
            elif cmd[0] == 'key':
                print('Cipher:', ALPHABET)
                print('Plain: ', ''.join(mapping.get(c, '_') for c in ALPHABET))
            elif cmd[0] == 'save' and len(cmd) == 2:
                Path(cmd[1]).write_text('\n'.join(f'{k}={v}' for k,v in sorted(mapping.items()))+'\n', encoding='utf-8')
                print('Mapping saved.')
            elif cmd[0] != 'show': print('Unknown command.')
            if cmd[0] in ('set','remove','show'):
                print(decode(text, mapping)[:3500])
        except ValueError as e: print('Error:', e)

if __name__ == '__main__': main()

# Variant V2: fully recovered substitution (cipher alphabet -> plaintext alphabet).
V2_KEY = 'BQFUJYNCRGVKZODSHWLAPETIXM'

def decrypt_v2(ciphertext):
    """Decrypt V2 while preserving case and all non-letter characters."""
    return decode(ciphertext, dict(zip(ALPHABET, V2_KEY)))
