PACKAGE = Mu
DIR = $(shell basename $(PWD))
MAINFILE = Main
TESTFILE?=tests/step1/test01.mu
ASM=$(TESTFILE:%.mu=%.s)
OBJ=$(TESTFILE:%.mu=%.obj)
TRACE=$(TESTFILE:%.mu=%.trace)
SIMU = ../../saruman/emu/emu
ASSEMBLER=../../../saruman/asm2017/asm.py
MYNAME=Lafoix_Paul
# To change the allocation strategy, use e.g.:
# make ALLOC=all_in_mem run
ALLOC=none

ifndef ANTLR4
$(error variable ANTLR4 is not set)
endif


all: antlr run

antlr: $(PACKAGE).g4 
	$(ANTLR4) $< -Dlanguage=Python3 -visitor -no-listener

.PHONY: run $(ASM)
run: $(ASM)
$(ASM): ${wildcard *.py} $(TESTFILE)
	python3 $(MAINFILE).py --reg-alloc=$(ALLOC) $(TESTFILE)

$(OBJ): $(ASM)
	python3 $(ASSEMBLER) $<

.PHONY: trace
trace: $(TRACE)
	cat $<
$(TRACE): $(OBJ) $(SIMU)
	$(SIMU) q $(OBJ) >$@

$(SIMU):
	cd $(dir $(SIMU)) && $(MAKE)

clean:
	rm -rf *~ $(PACKAGE)Lexer* $(PACKAGE)Parser* *.pyc *.tokens  __pycache* .cache/ *.interp
	rm -f tests/*.s tests/*.dot tests/*.dot.pdf tests/*.obj
	rm -f testsdataflow/*.s testsdataflow/*.dot testsdataflow/*.bin
	rm -f testsdataflow/*.dot.pdf testsdataflow/*.obj
	rm -f tests/step1/*.s tests/step1/*.bin
	rm -f tests/step2/*.s tests/step2/*.bin
	rm -f tests/mine/*.s tests/mine/*.bin


../../TP03/Mu-evalntype/MuParser.py:
	make -C ../../TP03/Mu-evalntype/

tests: ../../TP03/Mu-evalntype/MuParser.py $(SIMU) antlr
	python3 -m pytest -v -rs ./test_codegen.py
	python3 -m pytest -v -rs ./test_smartcodegen.py


tar: clean
	cd ..; tar cvfz $(DIR)-$(MYNAME).tgz $(DIR) --transform 's/$(DIR)/$(DIR)-$(MYNAME)/'
	@echo "Created ../$(DIR)-$(MYNAME).tgz"
