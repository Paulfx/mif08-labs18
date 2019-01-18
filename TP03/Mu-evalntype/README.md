Mu eval + typing

# Authors

Laure Gonnord, Serge Guelton, Matthieu Moy, and al for CAP and MIF08

Lafoix Paul: file MuEvalVisitor.py

# Contents

../ex contains example files.

make run TESTFILE=../ex/test01.mu for a single run
make tests to test all the file in ex/ according to EXPECTED results (you can select the files you want to test by modifying the variable ALL\_FILES in test\_evaluator.py)

make tests COV=true to launch coverage (pytest --cov) on the working directory

make tar to tar your example files.
