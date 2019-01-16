#! /usr/bin/env python3
"""
Usage:
    python3 sujetB.py <filename>
"""

from antlr4 import CommonTokenStream, FileStream

# include to use the generated lexer and parser
from TutuLexer import TutuLexer
from TutuParser import TutuParser

import argparse


def main(inputname):
    lexer = TutuLexer(FileStream(inputname))
    stream = CommonTokenStream(lexer)
    parser = TutuParser(stream)
    parser.prog()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tutu CCA')
    parser.add_argument('filename', type=str,
                        help='Source file.')
    args = parser.parse_args()
    main(args.filename)
