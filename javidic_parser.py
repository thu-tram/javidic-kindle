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

    def parse(self):
        term_banks = [f for f in os.listdir(self.dict_dir) if f.startswith('term_bank_') and f.endswith('.json')]
        term_banks.sort()

        entries_dict = {}

        for bank_file in term_banks:
            path = os.path.join(self.dict_dir, bank_file)
            sys.stderr.write(f"Parsing {bank_file}...\n")
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for entry_data in data:
                    entry = self.parse_entry(entry_data)
                    if entry:
                        # Create a key to deduplicate
                        # Normalized kanjis and readings
                        k_vals = sorted([k.keb for k in entry.kanjis])
                        r_vals = sorted([r.reb for r in entry.readings])
                        key = (tuple(k_vals), tuple(r_vals))
                        
                        if key not in entries_dict:
                            entries_dict[key] = entry
                        else:
                            # Keep the one with longer glossary
                            if len(entry.senses[0].gloss[0]) > len(entries_dict[key].senses[0].gloss[0]):
                                entries_dict[key] = entry
        
        return list(entries_dict.values())

    def parse_entry(self, entry_data):
        # Yomichan format: [kanji, reading, definition_tags, rules, score, glossary, sequence, term_tags]
        kanji_val = entry_data[0]
        reading_val = entry_data[1]
        glossary_list = entry_data[5]

        if not glossary_list:
            return None
            
        full_text = glossary_list[0]
        lines = full_text.split('\n')
        
        extracted_reading = ""
        pos_list = []
        
        if lines and lines[0].startswith('「') and lines[0].endswith('」'):
            extracted_reading = lines[0][1:-1]
        
        if len(lines) > 1:
            line = lines[1].strip()
            pos_match = re.search(r'〘(.*?)〙', line)
            if pos_match:
                pos_list = [p.strip() for p in pos_match.group(1).split(',')]
            elif re.match(r'^[a-zA-Z, ]+$', line) and line:
                pos_list = [p.strip() for p in line.split(',')]

        final_reading = reading_val if reading_val else extracted_reading
        
        kanjis = []
        readings = []
        orthos = []

        # Logic to separate kanji and kana correctly
        if is_kana(kanji_val):
            readings.append(Reading(kanji_val, 0, None, None))
            orthos.append(Ortho(kanji_val, 0, {}))
        else:
            kanjis.append(Kanji(kanji_val, 0))
            orthos.append(Ortho(kanji_val, 0, {}))

        if final_reading and final_reading != kanji_val:
            if is_kana(final_reading):
                if Reading(final_reading, 0, None, None) not in readings:
                    readings.append(Reading(final_reading, 0, None, None))
                    orthos.append(Ortho(final_reading, 0, {}))
            else:
                if Kanji(final_reading, 0) not in kanjis:
                    kanjis.append(Kanji(final_reading, 0))
                    orthos.append(Ortho(final_reading, 0, {}))

        if not readings:
            # Still need at least one reading for dictionary.py
            readings.append(Reading(kanji_val, 0, None, None))

        word_for_inflection = readings[0].reb
        mapped_pos = self.map_pos(pos_list, word_for_inflection)
        
        for ortho in orthos:
            if not is_katakana(ortho.value):
                for pos in mapped_pos:
                    try:
                        infl_dict = inflect(ortho.value, pos)
                    except InflectionError:
                        pass
                    except Exception:
                        pass
                    else:
                        if infl_dict:
                            ortho.inflgrps[pos] = set(infl_dict.values())

        senses = [Sense([], [], [full_text], [], [])]

        return Entry(senses, orthos, kanjis, readings, sentences=[], entry_type=VOCAB_ENTRY)

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
