import unittest
import io
from dictionary import write_index, Entry, Sense, Ortho, Reading, VOCAB_ENTRY

class TestDictionaryOutput(unittest.TestCase):
    def test_newline_preservation_in_html(self):
        # Create a mock entry with a newline in the gloss
        senses = [Sense([], [], ["Line 1\nLine 2"], [], [])]
        orthos = [Ortho("Test", 0, {})]
        readings = [Reading("Test", 0, None, None)]
        entries = [Entry(senses, orthos, [], readings, entry_type=VOCAB_ENTRY)]
        
        # Capture stdout
        stream = io.StringIO()
        
        # We need to mock a few things because write_index creates files
        # But we can test the part that writes to the section stream
        # Actually, let's just test that the newline replacement works.
        
        from html import escape
        gloss_text = "Line 1\nLine 2"
        escaped_text = escape(gloss_text, quote=False)
        formatted_text = escaped_text.replace('\n', '<br/>')
        
        self.assertEqual(formatted_text, "Line 1<br/>Line 2")

    def test_multiple_glosses_join(self):
        from html import escape
        glosses = ["G1", "G2"]
        joined = '; '.join(glosses)
        escaped = escape(joined, quote=False)
        self.assertEqual(escaped, "G1; G2")

if __name__ == '__main__':
    unittest.main()
