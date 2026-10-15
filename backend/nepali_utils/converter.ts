/**
 * Preeti to Unicode Converter and Devanagari Normalizer (TypeScript)
 * Ensures Unicode UTF-8 compliance and accurate ligature rendering for Nepali text.
 * Handles: क्ष, त्र, ज्ञ, श्री, र्य and all matras.
 */

const PREETI_MAPPINGS: [string, string][] = [
  ['cf]', 'ओ'],
  ['cf}', 'औ'],
  ['cf', 'आ'],
  ['c}', 'ऐ'],
  ['c]', 'ए'],
  ['c', 'अ'],
  ['O{', 'ई'],
  ['O', 'इ'],
  ['pm', 'ऊ'],
  ['p', 'उ'],
  ['P}', 'ऐ'],
  ['P', 'ए'],
  ['C', 'ऋ'],

  // Complex conjuncts
  ['If', 'क्षी'],
  ['I', 'क्ष'],
  ['q', 'त्र'],
  ['1', 'ज्ञ'],
  ['>', 'श्र'],
  ['?', 'रु'],
  ['¿', 'रू'],

  // Compounds
  ['km', 'फ'],
  ['Qm', 'फ्'],
  ['km\\', 'फ्'],
  ['k\\', 'फ्'],
  ['e|m', 'भ्र'],
  ['e|', 'भ्र'],
  ['e\\', 'भ्'],
  ['u|', 'ग्र'],
  ['s|', 'क्र'],
  ['k|', 'प्र'],
  ['q|', 'त्र'],
  ['w|', 'ध्र'],
  ['b|', 'द्र'],
  ['b\\', 'द्'],
  ['b\'', 'द्व'],
  ['b\\w', 'ध्व'],
  ['b\\b', 'द्द'],
  ['b\\w', 'द्ध'],
  ['h\\', 'ज्'],
  ['H~', 'ज्ञ'],
  ['s\\', 'क्'],
  ['t\\', 'त्'],
  ['g\\', 'न्'],
  ['d\\', 'म्'],
  ['l\\', 'स्'],
  ['n\\', 'ल्'],
  ['r\\', 'च्'],
  ['v\\', 'ख्'],
  ['y\\', 'थ्'],
  ['w\\', 'ध्'],
  ['z\\', 'श्'],
  ['Z', 'श्'],

  // Numbers
  ['!', '१'],
  ['@', '२'],
  ['$', 'द्ध'],
  ['%', 'छ'],
  ['^', 'ट'],
  ['&', 'ठ'],
  ['*', 'ड'],
  ['(', 'ढ'],
  [')', 'ण'],

  // Digits
  ['0', '०'],
  ['2', '२'],
  ['3', 'घ'],
  ['4', '४'],
  ['5', '५'],
  ['6', '६'],
  ['7', '७'],
  ['8', '८'],
  ['9', '९'],

  // Consonants
  ['s', 'क'],
  ['v', 'ख'],
  ['u', 'ग'],
  ['ª', 'ङ'],
  ['r', 'च'],
  ['h', 'ज'],
  ['e', 'भ'],
  ['~', 'ञ'],
  ['t', 'त'],
  ['y', 'थ'],
  ['b', 'द'],
  ['w', 'ध'],
  ['g', 'न'],
  ['k', 'प'],
  ['a', 'ब'],
  ['d', 'म'],
  ['o', 'य'],
  ['o|', 'य्र'],
  ['/', 'र'],
  ['n', 'ल'],
  ['j', 'व'],
  ['z', 'श'],
  ['i', 'ष'],
  ['l', 'स'],
  ['x', 'ह'],

  // Halves
  ['S', 'क्'],
  ['V', 'ख्'],
  ['U', 'ग्'],
  ['#', 'घ्'],
  ['R', 'च्'],
  ['H', 'ज्'],
  ['E', 'भ्'],
  ['T', 'त्'],
  ['Y', 'थ्'],
  ['B', 'द्'],
  ['W', 'ध्'],
  ['G', 'न्'],
  ['K', 'प्'],
  ['A', 'ब्'],
  ['D', 'म्'],
  ['L', 'स्'],
  ['N', 'ल्'],
  ['J', 'व्'],
  ['Q', 'त्त्'],

  // Matras
  ['f', 'ा'],
  ['f]', 'ो'],
  ['f}', 'ौ'],
  [']', 'े'],
  ['}', 'ै'],
  ['\'', 'ु'],
  ['"', 'ू'],
  ['m', '्'],
  ['+', 'ं'],
  ['F', 'ँ'],
  [';', 'ः'],

  // Punctuation
  ['.', '।'],
];

export function preetiToUnicode(text: string): string {
  if (!text) return '';

  let processed = '';
  const chars = Array.from(text);
  const n = chars.length;
  let idx = 0;

  while (idx < n) {
    const ch = chars[idx];
    if (ch === 'i' && idx + 1 < n) {
      if (idx + 3 < n && chars[idx + 2] === 'm') {
        processed += chars[idx + 1] + chars[idx + 2] + chars[idx + 3] + 'i';
        idx += 4;
        continue;
      } else if (idx + 2 < n && 'SKTGBWDNLA'.includes(chars[idx + 1]) && !' \t\n.,'.includes(chars[idx + 2])) {
        processed += chars[idx + 1] + chars[idx + 2] + 'i';
        idx += 3;
        continue;
      } else {
        processed += chars[idx + 1] + 'i';
        idx += 2;
        continue;
      }
    }
    processed += ch;
    idx++;
  }

  let out = processed;
  // Handle reph '{' -> र्
  out = out.replace(/([a-zA-Z0-9~>/?!@#$%^&*()]+)\{/g, 'र्$1');

  for (const [p, u] of PREETI_MAPPINGS) {
    out = out.split(p).join(u);
  }

  out = out.split('i').join('ि');
  out = out.split('{').join('र्');
  out = out.split('ाे').join('ो');
  out = out.split('ाै').join('ौ');

  return out.normalize('NFC');
}

export function isLikelyPreeti(text: string): boolean {
  if (!text) return false;
  for (let i = 0; i < text.length; i++) {
    const code = text.charCodeAt(i);
    if (code >= 0x0900 && code <= 0x097f) {
      return false; // Already has Devanagari Unicode
    }
  }
  const preetiSigs = ['g]kfn', 'sf7', 'cf]', 'cf}', 'df', 'sf', 'g\\', 'k|'];
  return preetiSigs.some((sig) => text.includes(sig));
}

export function normalizeDevanagari(text: string): string {
  if (!text) return '';
  if (isLikelyPreeti(text)) {
    return preetiToUnicode(text);
  }
  return text.normalize('NFC');
}
