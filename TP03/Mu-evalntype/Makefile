PACKAGE = Mu
MAINFILE = Main
#change with your own name:
MYNAME = JohnDoe
DIR = $(shell basename $(PWD))

TESTFILE?=ex/test00.mu

COV?=false
OPTPYTEST=
ifeq ($(COV),true)
OPTPYTEST=--cov=$(PWD)
endif

ifndef ANTLR4
abort:
	$(error variable ANTLR4 is not set)
endif

all: run

MuLexer.py MuParser.py: $(PACKAGE).g4
	$(ANTLR4) $< -Dlanguage=Python3 -visitor -no-listener

main-deps: MuLexer.py MuParser.py MuEvalVisitor.py MuTypingVisitor.py

run: $(MAINFILE).py main-deps
	python3  $< $(TESTFILE)

# tests all files in ex/test*.mu
tests: test_evaluator.py main-deps
	TEST_EXTENSIONS=t python3 -m pytest $(OPTPYTEST) -v --failed-first $< 


tar: clean
	cd ..; tar cvfz $(DIR)-$(MYNAME).tgz $(DIR) --transform 's/$(DIR)/$(DIR)-$(MYNAME)/'
	@echo "Created ../$(DIR)-$(MYNAME).tgz"

clean:
	rm -rf *~ $(PACKAGE)Parser.py $(PACKAGE)Lexer.py $(PACKAGE)Visitor.py *.pyc *.tokens  __pycache* ex/*~ .cache* ex-types/*~ *.interp .pytest*
