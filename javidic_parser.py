import json
import os
import re
import sys
from dictionary import Entry, Sense, Ortho, Kanji, Reading, Sentence, VOCAB_ENTRY
from kana import is_kana, is_katakana
from inflections import inflect, InflectionError

class JavidicParser:
    def __init__(self, dict_dir):
        self.dict_dir = dict_dir
        self.entries = []

    def parse(self):
        term_banks = [f for f in os.listdir(self.dict_dir) if f.startswith('term_bank_') and f.endswith('.json')]
        term_banks.sort()

        for bank_file in term_banks:
            path = os.path.join(self.dict_dir, bank_file)
            sys.stderr.write(f"Parsing {bank_file}...\n")
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for entry_data in data:
                    entry = self.parse_entry(entry_data)
                    if entry:
                        self.entries.append(entry)
        
        return self.entries

    def parse_entry(self, entry_data):
        # Yomichan format: [kanji, reading, definition_tags, rules, score, glossary, sequence, term_tags]
        kanji_val = entry_data[0]
        reading_val = entry_data[1]
        glossary_list = entry_data[5]

        extracted_reading, pos_list, glosses, examples = self.parse_glossary(glossary_list)
        
        # Use reading from field if available, otherwise from glossary
        final_reading = reading_val if reading_val else extracted_reading
        if not final_reading:
            final_reading = kanji_val

        # Create Orthos, Kanjis, Readings
        kanjis = []
        readings = []
        orthos = []

        if kanji_val != final_reading:
            kanjis.append(Kanji(kanji_val, 0))
            orthos.append(Ortho(kanji_val, 0, {}))
            
        readings.append(Reading(final_reading, 0, None, None))
        orthos.append(Ortho(final_reading, 0, {}))

        # Map POS for inflections
        mapped_pos = self.map_pos(pos_list, final_reading)
        
        # Aggregate the POS of all senses (in Javidic we usually have one group of senses per entry)
        senses = [Sense(pos_list, [], glosses, [], [])]

        # Handle inflections
        for ortho in orthos:
            if not is_katakana(ortho.value):
                for pos in mapped_pos:
                    try:
                        infl_dict = inflect(ortho.value, pos)
                    except InflectionError:
                        pass
                    except Exception as e:
                        # sys.stderr.write(f"warning: inflection error for {ortho.value} [{pos}]: {e}\n")
                        pass
                    else:
                        if infl_dict:
                            ortho.inflgrps[pos] = set(infl_dict.values())

        # Sentences
        sentences = []
        for jap, vie in examples:
            sentences.append(Sentence(vie, jap, True))

        return Entry(senses, orthos, kanjis, readings, sentences=sentences, entry_type=VOCAB_ENTRY)

    def parse_glossary(self, glossary_list):
        if not glossary_list:
            return "", [], [], []
        
        # Usually Javidic has one large string in glossary_list
        text = glossary_list[0]
        lines = text.split('\n')
        
        reading = ""
        pos = []
        glosses = []
        examples = []
        
        current_line_idx = 0
        
        # 1. Reading extraction 「...」
        if current_line_idx < len(lines) and lines[current_line_idx].startswith('「') and lines[current_line_idx].endswith('」'):
            reading = lines[current_line_idx][1:-1]
            current_line_idx += 1
        
        # 2. POS extraction 〘...〙 or tag lines
        if current_line_idx < len(lines):
            line = lines[current_line_idx].strip()
            pos_match = re.search(r'〘(.*?)〙', line)
            if pos_match:
                pos = [p.strip() for p in pos_match.group(1).split(',')]
                current_line_idx += 1
            elif re.match(r'^[a-zA-Z, ]+$', line) and line:
                pos = [p.strip() for p in line.split(',')]
                current_line_idx += 1
                
        # 3. Definitions and Examples
        i = current_line_idx
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            if line.endswith(':'):
                japanese = line[:-1].strip()
                i += 1
                if i < len(lines):
                    vietnamese = lines[i].strip()
                    examples.append((japanese, vietnamese))
                else:
                    glosses.append(line)
            elif ':' in line:
                parts = line.split(':', 1)
                examples.append((parts[0].strip(), parts[1].strip()))
            else:
                glosses.append(line)
            i += 1
                
        return reading, pos, glosses, examples

    def map_pos(self, javidic_pos, word):
        mapped = []
        for p in javidic_pos:
            p = p.lower()
            if p == 'n':
                mapped.append('n')
            elif p in ('adj-i', 'i-adj', 'adj'):
                mapped.append('adj-i')
            elif p == 'v1':
                mapped.append('v1')
            elif p.startswith('v5'):
                ending = word[-1]
                v5_map = {
                    'う': 'v5u', 'く': 'v5k', 'ぐ': 'v5g', 'す': 'v5s', 'つ': 'v5t',
                    'ぬ': 'v5n', 'ぶ': 'v5b', 'む': 'v5m', 'る': 'v5r'
                }
                mapped.append(v5_map.get(ending, 'v5u'))
            elif p in ('vs', 'suru'):
                mapped.append('vs-i')
            elif p in ('vk', 'kuru'):
                mapped.append('vk')
            else:
                mapped.append(p)
        return mapped
