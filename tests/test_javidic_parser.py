import unittest
from javidic_parser import JavidicParser
from dictionary import Ortho, Kanji, Reading, VOCAB_ENTRY

class TestJavidicParser(unittest.TestCase):
    def setUp(self):
        self.parser = JavidicParser("dict-data")

    def test_parse_entry_with_reading_in_glossary(self):
        # [kanji, reading, definition_tags, rules, score, glossary, sequence, term_tags]
        entry_data = [
            "0",
            "",
            "",
            "",
            0,
            ["「かんすうじゼロ」\nn, iK\nsố không trong chữ Hán"],
            0,
            ""
        ]
        entry = self.parser.parse_entry(entry_data)
        
        self.assertIsNotNone(entry)
        self.assertEqual(len(entry.orthos), 2)
        self.assertEqual(entry.orthos[0].value, "0")
        self.assertEqual(entry.orthos[1].value, "かんすうじゼロ")
        self.assertEqual(len(entry.readings), 1)
        self.assertEqual(entry.readings[0].reb, "かんすうじゼロ")
        self.assertEqual(len(entry.senses), 1)
        self.assertIn("số không trong chữ Hán", entry.senses[0].gloss[0])

    def test_parse_entry_with_kana_headword(self):
        entry_data = [
            "あいうえお",
            "",
            "",
            "",
            0,
            ["định nghĩa"],
            0,
            ""
        ]
        entry = self.parser.parse_entry(entry_data)
        
        self.assertIsNotNone(entry)
        self.assertEqual(len(entry.orthos), 1)
        self.assertEqual(entry.orthos[0].value, "あいうえお")
        self.assertEqual(len(entry.readings), 1)
        self.assertEqual(entry.readings[0].reb, "あいうえお")

    def test_parse_entry_fallback_reading(self):
        # Entry with no reading in field and no 「...」 in glossary
        entry_data = [
            "110番",
            "",
            "",
            "",
            0,
            ["số 110"],
            0,
            ""
        ]
        entry = self.parser.parse_entry(entry_data)
        
        self.assertIsNotNone(entry)
        self.assertEqual(len(entry.readings), 1)
        self.assertEqual(entry.readings[0].reb, "110番")

    def test_parse_pos_with_brackets(self):
        entry_data = [
            "辞書",
            "じしょ",
            "",
            "",
            0,
            ["「じしょ」\n〘n〙\ntừ điển"],
            0,
            ""
        ]
        entry = self.parser.parse_entry(entry_data)
        self.assertEqual(entry.senses[0].gloss[0], "「じしょ」\n〘n〙\ntừ điển")
        # Check if POS was extracted for inflection purposes (though not displayed in gloss)
        # Note: mapped_pos is internal, but we can check if it affected inflections
        # Since 'n' doesn't have inflections, we check another one
        
    def test_map_pos(self):
        self.assertEqual(self.parser.map_pos(['n'], '辞書'), ['n'])
        self.assertEqual(self.parser.map_pos(['adj-i'], 'おいしい'), ['adj-i'])
        self.assertEqual(self.parser.map_pos(['v5'], '笑う'), ['v5u'])
        self.assertEqual(self.parser.map_pos(['v5'], '行く'), ['v5k'])
        self.assertEqual(self.parser.map_pos(['v5'], '死ぬ'), ['v5n'])
        self.assertEqual(self.parser.map_pos(['vs'], '勉強'), ['vs-i'])

    def test_preserve_newlines(self):
        entry_data = [
            "Test",
            "",
            "",
            "",
            0,
            ["Line 1\nLine 2\nLine 3"],
            0,
            ""
        ]
        entry = self.parser.parse_entry(entry_data)
        self.assertEqual(entry.senses[0].gloss[0], "Line 1\nLine 2\nLine 3")

if __name__ == '__main__':
    unittest.main()
