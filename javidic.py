#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
from dictionary import write_index, VOCAB_INDEX
from javidic_parser import JavidicParser

def get_args():
    arg_parser = argparse.ArgumentParser(
        description="Build the Javidic Dictionary for Kindle",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    arg_parser.add_argument(
        "-p",
        "--pronunciation",
        action="store_true",
        default=False,
        help="If this flag is set pronunciations will be added.",
    )
    arg_parser.add_argument(
        "-i",
        "--info",
        action="store_true",
        default=False,
        help="If this flag is set additional entry information will be added.",
    )
    return arg_parser.parse_args()

from pronunciation import Pronunciation

def main():
    args = get_args()

    sys.stderr.write("Parsing Javidic data...\n")
    parser = JavidicParser("dict-data")
    entries = parser.parse()
    
    if args.pronunciation:
        sys.stderr.write("Adding pronunciations...\n")
        ac = Pronunciation()
        count = ac.addPronunciation(entries)
        sys.stderr.write(f"added {count} pronunciations\n")
        
    sys.stderr.write(f"Created {len(entries)} entries\n")

    sys.stderr.write("Creating files for Javidic Kindle Dictionary...\n")
    # Output to stdout or a file? jmdict.py uses sys.stdout for some reason but write_index opens its own files.
    # write_index(entries, dictionary_name, title, stream, ...)
    write_index(
        entries,
        "javidic",
        "Từ điển Nhật-Việt Javidic",
        sys.stdout,
        default_index=VOCAB_INDEX,
        add_entry_info=args.info,
        out_language="vi",
        creator="Javidic (converted to Kindle)"
    )
    sys.stderr.write("Done!\n")

if __name__ == "__main__":
    main()
