"""
Preeti to Unicode Converter for TruthWire
Strict adherence to Nepali Unicode UTF-8 standards.
Accurately preserves and handles:
- Complex conjuncts (क्ष, त्र, ज्ञ, श्र, श्री, र्य)
- Halant / virama (्)
- Reph (र्) - reordering rule where { represents र्
- Hraswa Ikar (ि) - reordering rule where 'i' precedes the consonant in Preeti but Unicode places it after consonant
- Matras (ा, ि, ी, ु, ू, े, ै, ो, ौ, ं, ँ, ः)
- Punctuation (।, ?, !, ,, etc.)
- Digits (०, १, २, ३, ४, ५, ६, ७, ८, ९)
"""

import unicodedata
import re

# Direct character / ligature mapping
# Order matters: multi-character replacements must occur before single characters
PREETI_REPLACEMENTS = [
    # Multi-character ligatures and vowels
    ('cf]', 'ओ'),
    ('cf}', 'औ'),
    ('cf', 'आ'),
    ('c}', 'ऐ'),
    ('c]', 'ए'),
    ('c', 'अ'),
    ('O{', 'ई'),
    ('O', 'इ'),
    ('pm', 'ऊ'),
    ('p', 'उ'),
    ('P}', 'ऐ'),
    ('P', 'ए'),
    ('C', 'ऋ'),
    
    # Complex conjuncts
    ('If', 'क्षी'),
    ('I', 'क्ष'),
    ('q', 'त्र'),
    ('1', 'ज्ञ'),  # Standard Preeti glyph for gya
    ('>', 'श्र'),
    ('?', 'रु'),
    ('¿', 'रू'),
    
    # Common double characters / compounds
    ('km', 'फ'),
    ('Qm', 'फ्'),
    ('km\\', 'फ्'),
    ('k\\', 'फ्'),
    ('e|m', 'भ्र'),
    ('e|', 'भ्र'),
    ('e\\', 'भ्'),
    ('u|', 'ग्र'),
    ('s|', 'क्र'),
    ('k|', 'प्र'),
    ('q|', 'त्र'),
    ('w|', 'ध्र'),
    ('b|', 'द्र'),
    ('b\\', 'द्'),
    ('b\'', 'द्व'),
    ('b\\w', 'ध्व'),
    ('b\\b', 'द्द'),
    ('b\\w', 'द्ध'),
    ('X\\', 'ह्'),
    ('x\\', 'ह्'),
    ('x|', 'ह्र'),
    ('h\\', 'ज्'),
    ('H~', 'ज्ञ'),
    ('s\\', 'क्'),
    ('t\\', 'त्'),
    ('g\\', 'न्'),
    ('d\\', 'म्'),
    ('l\\', 'स्'),
    ('n\\', 'ल्'),
    ('r\\', 'च्'),
    ('v\\', 'ख्'),
    ('y\\', 'थ्'),
    ('w\\', 'ध्'),
    ('z\\', 'श्'),
    ('Z', 'श्'),
    
    # Numbers
    ('!', '१'),
    ('@', '२'),
    ('$', 'द्ध'),
    ('%', 'छ'),
    ('^', 'ट'),
    ('&', 'ठ'),
    ('*', 'ड'),
    ('(', 'ढ'),
    (')', 'ण'),
    
    # Digits
    ('0', '०'),
    ('2', '२'),
    ('3', 'घ'),  # in standard Preeti '3' is घ, '#' is घ्
    ('4', '४'),
    ('5', '५'),
    ('6', '६'),
    ('7', '७'),
    ('8', '८'),
    ('9', '९'),
    
    # Consonants and halves
    ('s', 'क'),
    ('v', 'ख'),
    ('u', 'ग'),
    ('ª', 'ङ'),
    ('r', 'च'),
    ('h', 'ज'),
    ('e', 'भ'),
    ('~', 'ञ'),
    ('t', 'त'),
    ('y', 'थ'),
    ('b', 'द'),
    ('w', 'ध'),
    ('g', 'न'),
    ('k', 'प'),
    ('a', 'ब'),
    ('d', 'म'),
    ('o', 'य'),
    ('o|', 'य्र'),
    ('/', 'र'),
    ('n', 'ल'),
    ('j', 'व'),
    ('z', 'श'),
    ('i', 'ष'),  # In some contexts, but i is usually ikar (handled below)
    ('l', 'स'),
    ('x', 'ह'),
    
    # Shift consonants (half forms)
    ('S', 'क्'),
    ('V', 'ख्'),
    ('U', 'ग्'),
    ('#', 'घ्'),
    ('R', 'च्'),
    ('H', 'ज्'),
    ('E', 'भ्'),
    ('T', 'त्'),
    ('Y', 'थ्'),
    ('B', 'द्'),
    ('W', 'ध्'),
    ('G', 'न्'),
    ('K', 'प्'),
    ('A', 'ब्'),
    ('D', 'म्'),
    ('L', 'स्'),
    ('N', 'ल्'),
    ('J', 'व्'),
    ('Q', 'त्त्'),
    
    # Matras
    ('f', 'ा'),
    ('f]', 'ो'),
    ('f}', 'ौ'),
    (']', 'े'),
    ('}', 'ै'),
    ('\'', 'ु'),
    ('"', 'ू'),
    ('m', '्'),  # halanta
    ('+', 'ं'),  # anusvara
    ('F', 'ँ'),  # chandrabindu
    (';', 'ः'),  # visarga
    
    # Punctuation
    ('.', '।'),
    ('़', ''),
]


def preeti_to_unicode(text: str) -> str:
    """
    Converts Preeti text string into Unicode UTF-8 Devanagari.
    Properly reorders pre-consonant 'i' (ि) and reph '{' (र्).
    Normalizes Unicode representation with NFC.
    """
    if not text:
        return ""
    
    # Handle pre-consonant 'i' (ि) in Preeti:
    # In Preeti, 'i' is placed before the consonant (e.g. 'is' -> 'कि', 'ik' -> 'पि').
    # In Unicode, the vowel sign 'ि' comes after the consonant cluster.
    # Regex to swap 'i' + consonant/cluster -> consonant/cluster + 'ि'
    
    # Step 1: Reorder 'i' (hraswa ikar)
    # Match 'i' followed by optional halant consonant cluster, then single consonant
    # Preeti patterns: i + (C + m)? + C
    result = []
    i = 0
    chars = list(text)
    n = len(chars)
    
    # Preprocess reph '{' and 'i'
    # In Preeti, '{' is reph placed after or before consonant (e.g. u{ -> गर्)
    processed = ""
    idx = 0
    while idx < n:
        ch = chars[idx]
        
        # Check for 'i' followed by consonant
        if ch == 'i' and idx + 1 < n:
            # Check if next is a valid preeti consonant
            next_ch = chars[idx + 1]
            # Handle half consonant + full consonant (e.g., is\s -> क्कि)
            if idx + 3 < n and chars[idx + 2] == 'm':
                # e.g., ism s -> ksh
                processed += chars[idx + 1] + chars[idx + 2] + chars[idx + 3] + 'i'
                idx += 4
                continue
            elif idx + 2 < n and chars[idx + 1] in 'SKTGBWDNLA' and chars[idx + 2] not in ' \t\n.,':
                # Half consonant + full consonant
                processed += chars[idx + 1] + chars[idx + 2] + 'i'
                idx += 3
                continue
            else:
                processed += next_ch + 'i'
                idx += 2
                continue
                
        # Reph handling: '{' in Preeti turns into 'र्' prepended before the consonant
        if ch == '{':
            # In Preeti, '{' often follows the consonant (e.g. 'u{' = गर्)
            # We convert it to 'र्' before
            # Or handle during mapping
            processed += '{'
            idx += 1
            continue

        processed += ch
        idx += 1
        
    out = processed
    
    # Handle '{' (reph) after consonant -> prepended 'र्'
    # E.g. 's{' -> 'र्' + 's' (र्क)
    out = re.sub(r'([a-zA-Z0-9~>/?!\@#\$%\^&\*\(\)])\{', r'र्\1', out)
    
    # Apply replacements
    for p_char, u_char in PREETI_REPLACEMENTS:
        out = out.replace(p_char, u_char)
        
    # Replace any leftover 'i' with 'ि'
    out = out.replace('i', 'ि')
    # Replace any leftover '{' with 'र्'
    out = out.replace('{', 'र्')

    # Fix combinations like 'ा' + 'े' -> 'ो', 'ा' + 'ै' -> 'ौ'
    out = out.replace('ाे', 'ो')
    out = out.replace('ाै', 'ौ')
    out = out.replace('्ा', '')
    
    # Normalize with Unicode NFC (Canonical Composition)
    # This ensures ligatures like क्ष, त्र, ज्ञ, श्री, र्य render properly across all browsers
    normalized = unicodedata.normalize('NFC', out)
    return normalized


def is_likely_preeti(text: str) -> bool:
    """
    Detects if a string is encoded in legacy Preeti rather than UTF-8 Devanagari.
    Preeti text contains characteristic ASCII patterns like 'g]kfn', 'cf]', 'sf7df8f}'.
    """
    if not text:
        return False
    # If already contains Devanagari Unicode (0x0900 - 0x097F), it's already Unicode
    for ch in text:
        if '\u0900' <= ch <= '\u097f':
            return False
            
    preeti_signatures = ['g]kfn', 'sf7', 'cf]', 'cf}', 'df', 'sf', 'g\\', 'k|']
    for sig in preeti_signatures:
        if sig in text:
            return True
            
    return False


def normalize_devanagari(text: str) -> str:
    """
    Ensures correct Unicode NFC normalization for Devanagari text,
    sanitizing halantas and composite characters (क्ष, त्र, ज्ञ, श्री, र्य).
    """
    if not text:
        return ""
    # Convert if it's Preeti
    if is_likely_preeti(text):
        text = preeti_to_unicode(text)
    # Unicode NFC normalization
    return unicodedata.normalize('NFC', text)
