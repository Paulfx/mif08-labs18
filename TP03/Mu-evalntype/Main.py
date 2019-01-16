from MuLexer import MuLexer
from MuParser import MuParser
from MuEvalVisitor import MuEvalVisitor, MuRuntimeError, MuInternalError
from MuTypingVisitor import MuTypingVisitor, MuTypeError

import argparse
import antlr4
from antlr4.error.ErrorListener import ErrorListener


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


enable_typing = True


def main():
    # command line
    parser = argparse.ArgumentParser(description='Exec/Type mu files.')
    parser.add_argument('path', type=str,
                        help='file to exec and type')
    args = parser.parse_args()

    # lex and parse
    input_s = antlr4.FileStream(args.path, encoding='utf8')
    lexer = MuLexer(input_s)
    counter = CountErrorListener()
    lexer._listeners.append(counter)
    stream = antlr4.CommonTokenStream(lexer)
    parser = MuParser(stream)
    parser._listeners.append(counter)
    tree = parser.prog()
    if counter.count > 0:
        exit(1)  # Syntax or lexicography errors occured, don't try to go further.

    # typing Visitor - This is given to you
    if enable_typing:
        visitor1 = MuTypingVisitor()
        try:
            visitor1.visit(tree)
        except MuTypeError as e:
            print(e.args[0])
            exit(1)

    # eval Visitor - You have some TODOS in this file!
    visitor2 = MuEvalVisitor()
    try:
        visitor2.visit(tree)
    except MuRuntimeError as e:
        print(e.args[0])
        exit(1)
    except MuInternalError as e:
        print(e.args[0])
        exit(2)


if __name__ == '__main__':
    main()
