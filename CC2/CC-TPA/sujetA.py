#! /usr/bin/env python3
"""
Usage:
    python3 sujetA.py <filename>
"""

from antlr4 import CommonTokenStream, FileStream

# include to use the generated lexer and parser
from PalinLexer import PalinLexer
from PalinParser import PalinParser

import argparse


def main(inputname):
    lexer = PalinLexer(FileStream(inputname))
    stream = CommonTokenStream(lexer)
    parser = PalinParser(stream)
    parser.prog()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Palin CCA')
    parser.add_argument('filename', type=str,
                        help='Source file.')
    args = parser.parse_args()
    main(args.filename)
