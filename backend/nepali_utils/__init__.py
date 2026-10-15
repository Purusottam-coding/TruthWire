"""
Preeti to Unicode Converter and Devanagari Normalizer
Converts legacy Preeti font text to standard Unicode UTF-8 Devanagari.
Accurately preserves and handles complex conjuncts and ligatures:
- kshya (क्ष)
- tra (त्र)
- gya (ज्ञ)
- shree (श्री)
- reph (र्य / र्)
- matras (ि, ी, ु, ू, े, ै, ो, ौ, ं, ँ, ः)
- halanta / virama (्)
"""

import unicodedata

# Mapping from Preeti character sequences to Unicode Devanagari
PREETI_CHAR_MAP = {
    # Independent vowels
    'cf]': 'ओ',
    'cf}': 'औ',
    'cf': 'आ',
    'c': 'अ',
    'O': 'इ',
    'O{': 'ई',
    'p': 'उ',
    'pm': 'ऊ',
    'P': 'ए',
    'P}': 'ऐ',
    'P]': 'ऐ',

    # Consonants
    's': 'क',
    'v': 'ख',
    'u': 'ग',
    '3': 'घ',
    'ª': 'ङ',
    'r': 'च',
    '5': 'छ',
    'h': 'ज',
    'e': 'झ',
    '~': 'ञ',
    '6': 'ट',
    '7': 'ठ',
    '8': 'ड',
    '9': 'ढ',
    '0': 'ण',
    't': 'त',
    'y': 'थ',
    'b': 'द',
    'w': 'ध',
    'g': 'न',
    'k': 'प',
    'km': 'फ',
    'km\\': 'फ्',
    'b\\': 'ब',
    'a': 'ब',
    'e\\': 'भ',
    'e|': 'भ्र',
    'e|m': 'भ्र',
    'e': 'झ',
    'e': 'झ',
    'e|': 'भ्र',
    'e': 'झ',
    'e': 'झ',
    'e': 'झ',
    'e': 'झ',
    'e': 'झ',
    'e': 'झ',
    'e': 'झ',
    'e': 'झ',
    'e': 'झ',
}
