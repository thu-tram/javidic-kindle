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
        "-d",
        "--dict-dir",
        default="dict-data",
        help="Directory containing the Yomichan dictionary files (default: dict-data)",
    )
    arg_parser.add_argument(
        "-n",
        "--name",
        default="javidic",
        help="Base name for the generated files (default: javidic)",
    )
    arg_parser.add_argument(
        "-t",
        "--title",
        default="Từ điển Nhật-Việt Javidic",
        help="Display title of the dictionary",
    )
    arg_parser.add_argument(
        "-l",
        "--lang",
        default="vi",
        help="Output language of the dictionary (default: vi)",
    )
    arg_parser.add_argument(
        "-f",
        "--frontmatter",
        default="javidic-frontmatter.html",
        help="Frontmatter HTML file used in the OPF manifest (default: javidic-frontmatter.html)",
    )
    # existing creator arg
    arg_parser.add_argument(
        "-c",
        "--creator",
        default="Javidic (converted to Kindle)",
        help="Creator/Copyright metadata",
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

    sys.stderr.write(f"Parsing dictionary from {args.dict_dir}...\n")
    parser = JavidicParser(args.dict_dir)
    entries = parser.parse()
    
    if args.pronunciation:
        sys.stderr.write("Adding pronunciations...\n")
        ac = Pronunciation()
        count = ac.addPronunciation(entries)
        sys.stderr.write(f"added {count} pronunciations\n")
        
    sys.stderr.write(f"Created {len(entries)} entries\n")

    sys.stderr.write(f"Creating files for {args.title}...\n")
    write_index(
        entries,
        args.name,
        args.title,
        sys.stdout,
        default_index=VOCAB_INDEX,
        add_entry_info=args.info,
        out_language=args.lang,
        creator=args.creator,
        frontmatter=args.frontmatter
    )
    sys.stderr.write("Done!\n")

if __name__ == "__main__":
    main()
