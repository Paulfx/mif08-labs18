#! /usr/bin/env python3
import pytest
import glob
import os
import sys
from test_expect_pragma import TestExpectPragmas, cat

HERE = os.path.dirname(os.path.realpath(__file__))
if HERE == os.path.realpath('.'):
    HERE = '.'
TEST_DIR = HERE
IMPLEM_DIR = HERE


ALL_FILES = []
# tests for typing AND evaluation
# change here to also include bad_def tests.
ALL_FILES += glob.glob(TEST_DIR + '/ex/*.mu')
ALL_FILES += glob.glob(TEST_DIR + '/ex-types/*.mu')


# Path setting
if 'TEST_FILES' in os.environ:
    ALL_FILES = glob.glob(os.environ['TEST_FILES'], recursive=True)
MU_EVAL = os.path.join(IMPLEM_DIR, 'Main.py')


class TestEval(TestExpectPragmas):

    def evaluate(self, file):
        return self.run_command(['python3', MU_EVAL, file])

    @pytest.mark.parametrize('filename', ALL_FILES)
    def test_eval(self, filename):
        cat(filename)  # For diagnosis
        expect = self.get_expect(filename)
        eval = self.evaluate(filename)
        if expect:
            assert(eval == expect)


if __name__ == '__main__':
    pytest.main(sys.argv)
