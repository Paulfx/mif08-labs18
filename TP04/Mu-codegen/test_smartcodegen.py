#! /usr/bin/env python3

import os
import sys
import pytest
import glob
import subprocess
from test_expect_pragma import TestExpectPragmas

"""
Usage:
    python3 test_smartcodegen.py
(or make tests)
"""

"""
MIF08 and CAP, 2018
Unit test infrastructure for testing code generation:
1) compare the actual output to the expected one (in comments)
2) compare the actual output to the one obtained by simulation
3) for different allocation algorithms
"""

HERE = os.path.dirname(os.path.realpath(__file__))
if HERE == os.path.realpath('.'):
    HERE = '.'
TEST_DIR = HERE
IMPLEM_DIR = HERE
MU_COMPILE = os.path.join(IMPLEM_DIR, "Main.py")

withEval = True  # change here if your evaluator is too buggy.

print("HERE=", HERE)

# change here for your own test files
ALL_FILES = glob.glob('tests/*/*.mu')

HERE = os.path.dirname(os.path.realpath(__file__))

TARGETM = os.path.join(HERE, '..', '..', 'saruman')

ASM = os.path.join(TARGETM, 'asm.py')
SIMU = os.path.join(TARGETM, 'emu', 'emu')

MU_EVAL = os.path.join(
HERE, '..', '..', 'TP03', 'Mu-evalntype', 'Main.py')


class TestCodeGen(TestExpectPragmas):

    def evaluate(self, file):
        return subprocess.check_output([
            'python3',
            MU_EVAL,
            file],
            timeout=60).decode("utf-8", "strict")

    def smart_alloc(self, file):
        return self.compile_and_simulate(file)

    def compile_and_simulate(self, file):
        basename, rest = os.path.splitext(file)
        print("Compiling (smart alloc) ...")
        output_name = basename + '.s'
        self.remove(output_name)
        try:
            self.run_command([
                'python3', MU_COMPILE, file,
                "--reg-alloc=smart"
            ])
        except subprocess.CalledProcessError:
            raise Exception("Compilation failed.")
        assert(os.path.isfile(output_name))
        print("Compiling ... OK")
        sys.stderr.write("Assembling " + output_name + " ... ")
        self.remove(basename + '.bin')
        cmd = [
            'python3', ASM, '-b', output_name,
            '-o', basename + '.bin'
        ]
        subprocess.check_output(cmd, timeout=60)
        assert(os.path.isfile(basename + '.bin'))
        sys.stderr.write("Assembling ... OK\n")
        try:
            return subprocess.check_output(
                [SIMU, '-r', basename + '.bin'],
                timeout=10).decode("utf-8", "strict")
        except subprocess.TimeoutExpired:
            self.fail()

    @pytest.mark.parametrize('filename', ALL_FILES)
    @pytest.mark.skipif(not withEval, reason='withEval is True')
    def test_expect(self, filename):
        """Test the EXPECTED annotations in test files by launching the
        interpreter."""
        expect = self.get_expect(filename).output
        evalval = self.evaluate(filename)
        if expect:
            assert evalval == expect

    @pytest.mark.parametrize('filename', ALL_FILES)
    def test_compile_and_simulate(self, filename):
        """Generate code with default allocation, i.e. the smart
        allocation."""
        expect = self.get_expect(filename).output
        actual = self.smart_alloc(filename)
        if expect:
            assert actual == expect


if __name__ == '__main__':
    pytest.main(sys.argv)
