MAINFILE = sujetB
PACKAGE = Tutu
MYNAME = JohnDoe

ifndef ANTLR4
abort:
	$(error variable ANTLR4 is not set)
endif

$(PACKAGE)Listener.py $(PACKAGE)Lexer.py $(PACKAGE)Lexer.tokens $(PACKAGE)Parser.py $(PACKAGE).tokens: $(PACKAGE).g4
	$(ANTLR4) $< -Dlanguage=Python3


tar: clean
	cd ..; tar cvfz $(MYNAME).tgz CC-TPB/ --transform 's/CC-TPB/$(MYNAME)/'

clean:
	rm -rf *~ $(PACKAGE)*.py $(PACKAGE)*.pyc *.tokens  __pycache* .cache *.interp
