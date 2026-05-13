import json
import os
import re

def parse_javidic_glossary(glossary_list):
    if not glossary_list:
        return "", [], [], []
    
    text = glossary_list[0]
    lines = text.split('\n')
    
    reading = ""
    pos = []
    glosses = []
    examples = []
    
    current_line_idx = 0
    
    # 1. Reading extraction
    if lines[current_line_idx].startswith('「') and lines[current_line_idx].endswith('」'):
        reading = lines[current_line_idx][1:-1]
        current_line_idx += 1
    
    # 2. POS extraction
    if current_line_idx < len(lines):
        line = lines[current_line_idx]
        # Match 〘...〙 or comma-separated tags like "n, iK"
        pos_match = re.search(r'〘(.*?)〙', line)
        if pos_match:
            pos = [p.strip() for p in pos_match.group(1).split(',')]
            current_line_idx += 1
        elif re.match(r'^[a-zA-Z, ]+$', line):
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
            # Example followed by translation on next line
            japanese = line[:-1].strip()
            i += 1
            if i < len(lines):
                vietnamese = lines[i].strip()
                examples.append((japanese, vietnamese))
            else:
                # If no next line, treat it as a gloss
                glosses.append(line)
        elif ':' in line:
            # Example and translation on same line
            parts = line.split(':', 1)
            examples.append((parts[0].strip(), parts[1].strip()))
        else:
            glosses.append(line)
        i += 1
            
    return reading, pos, glosses, examples

def test_parse():
    path = 'dict-data/term_bank_1.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for entry in data[:10]:
        kanji = entry[0]
        reading_field = entry[1]
        glossary = entry[5]
        
        extracted_reading, pos, glosses, examples = parse_javidic_glossary(glossary)
        
        final_reading = reading_field if reading_field else extracted_reading
        
        print(f"Kanji: {kanji}")
        print(f"Reading: {final_reading}")
        print(f"POS: {pos}")
        print(f"Glosses: {glosses}")
        print(f"Examples: {examples}")
        print("-" * 20)

if __name__ == "__main__":
    test_parse()
