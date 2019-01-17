#! /usr/bin/env python3
"""
Code generation lab, main file. Code Generation with Smart IRs.
Usage:
    python3 Main.py <filename>
    python3 Main.py --help
"""
from MuLexer import MuLexer
from MuParser import MuParser
from MuCodeGen3AVisitor import MuCodeGen3AVisitor
from ExpandJump import replace_all_meta

import argparse

from antlr4 import FileStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener

import os


class CountErrorListener(ErrorListener):
    """Count number of errors.

    Parser provides getNumberOfSyntaxErrors(), but the Lexer
    apparently doesn't provide an easy way to know if an error occured
    after the fact. Do the counting ourserves with a listener.
    """

    def __init__(self):
        super(CountErrorListener, self).__init__()
        self.count = 0

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.count += 1


debug = False  # Should be False in your final version+make tests


def main(inputname, reg_alloc, stdout=False, output_name=None):
    (basename, rest) = os.path.splitext(inputname)
    if stdout:
        output_name = None
        print("Code will be generated on standard output")
    elif output_name is None:
        output_name = basename + ".s"
        print("Code will be generated in file " + output_name)

    input_s = FileStream(inputname)
    lexer = MuLexer(input_s)
    counter = CountErrorListener()
    lexer._listeners.append(counter)
    stream = CommonTokenStream(lexer)
    parser = MuParser(stream)
    parser._listeners.append(counter)
    tree = parser.prog()
    if counter.count > 0:
        exit(1)  # Syntax or lexicography errors occured, don't try to go further.

    # Codegen 3@ CFG Visitor, first argument is debug mode
    visitor3 = MuCodeGen3AVisitor(debug, parser)

    visitor3.visit(tree)
    prog = visitor3.get_prog()

    # Allocation part
    if reg_alloc == "naive":
        prog.naive_alloc()
        comment = "naive allocation"
    elif reg_alloc == "all_in_mem":
        prog.alloc_to_mem()
        comment = "all-in-memory allocation"
    elif reg_alloc == "smart":
        prog.do_smart_alloc(basename)
        comment = "smart allocation with graph coloring"
    elif reg_alloc == "none":
        comment = "non executable 3-Address instructions"
    else:
        raise ValueError("Invalid allocation strategy:" + reg_alloc)

    replace_all_meta(prog)  # replace conditional jump in the 3@code
    prog.printCode(output_name, comment=comment)
    if debug:
        visitor3.printRegisterMap()  # print allocation


# command line management
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate code for .mu file')
    parser.add_argument('filename', type=str,
                        help='Source file.')
    parser.add_argument('--reg-alloc', type=str,
                        required=True,
                        choices=['none', 'naive', 'all_in_mem', 'smart'],
                        help='Allocation to perform')
    parser.add_argument('--stdout', action='store_true',
                        help='Generate code to stdout')
    parser.add_argument('--output', type=str,
                        help='Generate code to outfile')

    args = parser.parse_args()
    main(args.filename, args.reg_alloc, args.stdout, args.output)
