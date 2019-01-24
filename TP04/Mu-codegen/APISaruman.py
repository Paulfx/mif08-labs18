#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import networkx as nx
import graphviz as gz
import copy

from Operands import (Condition, Immediate, Char,
                      Offset,
                      TemporaryPool,
                      AllocationError, Register, SP, Indirect, Temporary,
                      GP_REGS)
from Instruction3A import Instruction, Instru3A, Comment, Label, regset_to_string
from Allocations import replace_reg, replace_mem, replace_smart

from LibGraphes import Graph  # For Graph coloring utility functions

"""
MIF08, CAP, CodeGeneration, SARUMAN API
 Classes for a SARUMAN program: constructors, allocation, dump.
"""


def interfere(t1, t2, mapout, defined):
    """Interfere function: True if t1 and t2 are in conflit."""
    for key in mapout:
        if ((t1 in mapout[key] and t2 in mapout[key]) or
                (t1 in mapout[key] and t2 in defined[key]) or
                (t2 in mapout[key] and t1 in defined[key])):
            return True
    return False



class SARUMANProg:
    """Representation of a SARUMAN program (i.e. list of
    instructions)."""
    def __init__(self):
        Instruction.count = 0
        self._listIns = []
        self._nbtmp = -1
        self._nblabel = -1
        self._dec = -1
        self._pool = TemporaryPool()
        # CFG Stuff - Lab 5 Only
        self._start = None
        self._end = None
        self._mapin = {}  # will be map block -> set of variables
        self._mapout = {}
        self._mapdef = {}  # block : defined = killed vars in the block
        self._igraph = None  # interference graph

    def add_edge(self, src, dest):
        dest._in.append(src)
        src._out.append(dest)

    def add_instruction(self, i, linkwithsucc=True):
        """Utility function to add an instruction in the program.
        in Lab 4, only add at the end of the instruction list (_listIns)
        in Lab 5, will be used to also add in the CFG structure.
        """
        if not self._listIns:  # empty list: empty prg
            i._isnotStart = False
            self._start = i
        else:
            if self._end is not None:
                self.add_edge(self._end, i)
        self._end = i
        if not linkwithsucc:
            self._end = None
        self._listIns.append(i)
        return i

    def iter_instructions(self, f):
        """Iterate over instructions.

        For each real instruction (not label or comment), call f,
        which must return either None or a list of instruction. If it
        returns None, nothing happens. If it returns a list, then the
        instruction is replaced by this list.

        """
        i = 0
        while i < len(self._listIns):
            old_i = self._listIns[i]
            if not old_i.is_instruction():
                i += 1
                continue
            new_i_list = f(old_i)
            if new_i_list is None:
                i += 1
                continue
            del self._listIns[i]
            self._listIns.insert(i, Comment(str(old_i)))
            i += 1
            for new_i in new_i_list:
                self._listIns.insert(i, new_i)
                i += 1
            self._listIns.insert(i, Comment("end " + str(old_i)))
            i += 1

    def get_instructions(self):
        return self._listIns

    def new_location(self, three_addr):
        if three_addr:
            return self.new_tmp()
        else:
            return self.new_offset()

    def new_tmp(self):
        """
        Return a new fresh temporary (temp)
        + add in list
        """
        return self._pool.new_tmp()

    def printTempList(self):
        print(self._pool._all_temps)

    def new_offset(self, base):
        """
        Return a new offset in the memory stack
        """
        self._dec = self._dec + 1
        return Offset(base, self._dec)

    def new_label(self, name):
        """
        Return a new label
        """
        self._nblabel = self._nblabel + 1
        return Label(name + "_" + str(self._nblabel))

    def new_label_while(self):
        self._nblabel = self._nblabel + 1
        return (Label("l_while_begin_" + str(self._nblabel)),
                Label("l_while_end_" + str(self._nblabel)))

    def new_label_cond(self):
        self._nblabel = self._nblabel + 1
        return (Label("l_cond_neg_" + str(self._nblabel)),
                Label("l_cond_end_" + str(self._nblabel)))

    def new_label_if(self):
        self._nblabel = self._nblabel + 1
        return (Label("l_if_false_" + str(self._nblabel)),
                Label("l_if_end_" + str(self._nblabel)))

    # each instruction has its own "add in list" version
    def addLabel(self, s):
        return self.add_instruction(s)

    def addComment(self, s):
        self.add_instruction(Comment(s))

    def addInstructionPRINT(self, expr):
        """Print integer value, followed by newline."""
        # a print instruction generates the temp it prints.
        ins = Instru3A("print signed", expr)
        if isinstance(expr, Temporary):
            # tests if the temp prints a temporary
            ins._gen.add(expr)
        self.add_instruction(ins)
        self.add_instruction(Instru3A("print char", Char("'\\n'")))

    # test and cond jumps.
    def addInstructionJUMP(self, label):
        assert isinstance(label, Label)
        i = Instru3A("jump", label)
        # add in list but do not link with the following node
        self.add_instruction(i, linkwithsucc=False)
        self.add_edge(i, label)
        return i

    # Useful meta instruction for conditional jump
    def addInstructionCondJUMP(self, label, op1, c, op2):
        assert isinstance(label, Label)
        assert isinstance(c, Condition)
        ins = Instru3A("cond_jump", args=[label, op1, c, op2])
        if isinstance(op1,Temporary):
            ins._gen.add(op1)
        if isinstance(op2,Temporary):
            ins._gen.add(op2)
        self.add_instruction(ins)
        self.add_edge(ins, label)
        return ins

    def addInstructionADD(self, dr, sr1, sr2orimm7):
        if isinstance(sr2orimm7, Immediate):
            ins = Instru3A("add3i", dr, sr1, sr2orimm7)
        else:
            ins = Instru3A("add3", dr, sr1, sr2orimm7)
        self.addGenKillSr2orimm(ins,dr,sr1,sr2orimm7)
        self.add_instruction(ins)

    def addInstructionSUB(self, dr, sr1, sr2orimm7):
        if isinstance(sr2orimm7, Immediate):
            ins = Instru3A("sub3i", dr, sr1, sr2orimm7)
        else:
            ins = Instru3A("sub3", dr, sr1, sr2orimm7)
        self.addGenKillSr2orimm(ins,dr,sr1,sr2orimm7)
        self.add_instruction(ins)

    def addInstructionAND(self, dr, sr1, sr2orimm7):
        ins = Instru3A("and3", dr, sr1, sr2orimm7)
        self.addGenKillSr2orimm(ins,dr,sr1,sr2orimm7)
        self.add_instruction(ins)

    def addInstructionOR(self, dr, sr1, sr2orimm7):
        ins = Instru3A("or3", dr, sr1, sr2orimm7)
        self.addGenKillSr2orimm(ins,dr,sr1,sr2orimm7)
        self.add_instruction(ins)

    # Copy values (immediate or in register)
    def addInstructionLETI(self, dr, imm7):
        ins = Instru3A("leti", dr, imm7)
        ins._kill.add(dr)
        self.add_instruction(ins)

    def addInstructionLET(self, dr, sr):
        ins = Instru3A("let", dr, sr)
        self.addGenKillSr2orimm(ins,dr,sr)
        self.add_instruction(ins)

    def addInstructionRMEM(self, dr, sr):
        if isinstance(sr, Register):
            # Accept plain register where we expect an indirect
            # addressing mode.
            sr = Indirect(sr)
        ins = Instru3A("rmem", dr, sr)
        # TODO ADD GEN KILL INIT IF REQUIRED
        self.add_instruction(ins)

    def addInstructionWMEM(self, dr, sr):
        if isinstance(sr, Register):
            # Accept plain register where we expect an indirect
            # addressing mode.
            sr = Indirect(sr)
        ins = Instru3A("wmem", dr, sr)
        # TODO ADD GEN KILL INIT IF REQUIRED
        self.add_instruction(ins)

    def addGenKillSr2orimm(self, ins, dr, sr, sr2orimm7=None):
        ins._kill.add(dr)
        ins._gen.add(sr)
        if isinstance(sr2orimm7, Temporary):
            ins._gen.add(sr2orimm7)
        #Remove occurence of kill that we found in gen
        ins._kill = ins._kill.difference(ins._gen)

    # Allocation functions
    def naive_alloc(self):
        """ Allocate all temporaries to registers.
        Fail if there are too many temporaries."""
        regs = list(GP_REGS)  # Get a writable copy
        reg_allocation = dict()
        for tmp in self._pool._all_temps:
            try:
                reg = regs.pop()
            except IndexError:
                raise AllocationError(
                    "Too many temporaries ({}) for the naive allocation, sorry"
                    .format(len(self._pool._all_temps)))
            reg_allocation[tmp] = reg
        self._pool.set_reg_allocation(reg_allocation)
        self.iter_instructions(replace_reg)

    def alloc_to_mem(self):
        """Allocate all temporaries to memory. Hypothesis:
        - Expanded instructions can use r0 (to compute addresses), r1 and
        r2 (to store the values of temporaries before the actual
        instruction).
        """
        self._pool.set_reg_allocation(
            {temp: self.new_offset(SP) for temp in self._pool._all_temps})
        self.iter_instructions(replace_mem)

    def do_smart_alloc(self, basename, debug=False):
        """Perform all steps related to smart register allocation:

        - Dataflow analysis to compute liveness range of each
          temporary.

        - Interference graph construction

        - Graph coloring

        - Substitution of temporaries by actual locations in the
          3-address code.
        """
        # prints the CFG as a dot file
        if debug:
            self.printDot(basename + ".dot")
            print("CFG generated in " + basename + ".dot.pdf")

        # TODO: Move the print&return statements below down as you progress
        # TODO: in the lab. They must be removed from the final version.
        #print("do_smart_alloc: stopping here for now")
        #return

        # dataflow
        if debug:
            self.printGenKill()

        mapin, mapout = self.doDataflow()
        if debug:
            self.printMapInOut()

        # conflict graph
        igraph = self.doInterfGraph()

        if debug:
            print("printing the conflict graph")
            igraph.print_dot(basename + "_conflicts.dot")
        
        # Smart Alloc via graph coloring
        self.smart_alloc(debug, basename + "_colored.dot")

    def smart_alloc(self, debug, outputname):
        """Allocate all temporaries with graph coloring
        also prints the colored graph if debug.

        Precondition: the interference graph (_igraph) must have been
        initialized.
        """
        if not self._igraph:
            raise Exception("hum, the interference graph seems to be empty")
        # Temporary -> Operand (register or offset) dictionary,
        # specifying where a given Temporary should be allocated:
        alloc_dict = {temp: None for temp in self._pool._all_temps}

        def replaceValueDictOfTemporary(key_str, value):
            for key in alloc_dict.keys():
                if str(key) == key_str:
                    alloc_dict[key] = value

        # TODO :  color the graph with appropriate nb of colors,
        # and get back the (partial) coloring (see Libgraphes.py)
        # if appropriate, relaunch the coloring for spilled variables.
        # Then, construct a dict register -> Register or Offset.
        # My version is 27 lines including debug log.
        # Be careful, the registers names in the graph are now strings,
        # at some point there should be an explicit
        # str_temp = str(temp) conversion before accessing the associated color.
        
        coloring, is_total, colored_nodes = self._igraph.color(6, [])

        for node in colored_nodes:
            #alloc_dict[node] = GP_REGS[int(coloring[node])]
            replaceValueDictOfTemporary(node, GP_REGS[int(coloring[node])])

        if not is_total:
            nbNotColored = len(self._igraph.vertices()) - len(colored_nodes)
            # We recolor only not colored nodes
            coloring, is_total, colored_nodes = self._igraph.color(nbNotColored, colored_nodes)
            assert is_total is True
            assert nbNotColored == len(colored_nodes)
            # We add them as offset
            for node in colored_nodes:
                #alloc_dict[node] = Offset(SP, int(coloring[node]))
                replaceValueDictOfTemporary(node, Offset(SP, int(coloring[node])))


        self._pool.set_reg_allocation(alloc_dict)
        self.iter_instructions(replace_smart)

    def printGenKill(self):
        print("Dataflow Analysis, Initialisation")
        i = 0
        # this should be an iterator
        while i < len(self._listIns):
            self._listIns[i].printGenKill()
            i += 1

    def printMapInOut(self):  # Prints in/out sets, useful for debug!
        print("In: {" + ", ".join(str(x) + ": " + regset_to_string(self._mapin[x])
                                  for x in self._mapin.keys()) + "}")
        print("Out: {" + ", ".join(str(x) + ": " + regset_to_string(self._mapout[x])
                                   for x in self._mapout.keys()) + "}")

    def doDataflow(self):
        print("Dataflow Analysis")
        countit = 0
        # initialisation of all mapout,mapin sets, and def = kill
        for i in range(len(self._listIns)):
            self._mapin[i] = set()
            self._mapout[i] = set()
        stable = False
        while not stable:
            # Iterate until fixpoint :
            # make calls to self._start.do_dataflow_onestep (in Instruction3A.py)

            countit = countit + 1
            saveoldout = copy.copy(self._mapout)
            saveoldin = copy.copy(self._mapin)  # structure copy
            self._start.do_dataflow_onestep(self._mapin, self._mapout, set())
            stable = True
            for i in range(len(self._listIns)):
                # print("considering node number "+str(i))
                # sets are growing.
                # print (self._mapout[i])
                if (self._mapout[i] > saveoldout[i] or
                        self._mapin[i] > saveoldin[i]):
                    stable = False
        print("finished in " + str(countit) + " iterations")
        # print(self._mapin)
        # print(self._mapout)

        return (self._mapin, self._mapout)

    def doInterfGraph(self):
        self._start.update_defmap(self._mapdef, set())
        self._igraph = Graph()
        # self.printTempList()
        if not self._mapout and not self._mapin:
            raise Exception("hum, dataflow sets need to be initialised")
        else:
            t = self._pool._all_temps
            for v in t:
                # print("add vertex "+str(v))
                self._igraph.add_vertex(str(v))
            tpairs = [(p1, p2) for p1 in t for p2 in t]
            # print(tpairs)
            for (t1, t2) in tpairs:
                if interfere(t1, t2, self._mapout, self._mapdef):
                    # print("add edge "+str(t1)+" - "+str(t2))
                    self._igraph.add_edge((str(t1), str(t2)))

        return(self._igraph)

    # Dump code
    def printCode(self, filename, comment=None):
        # dump generated code on stdout or file.
        output = open(filename, 'w') if filename else sys.stdout
        output.write(
            ";;Automatically generated TARGET code, MIF08 & CAP 2018\n")
        if comment is not None:
            output.write(";;{} version\n".format(comment))
        # Stack in SARUMAN is managed with SP
        for i in self._listIns:
            i.printIns(output)
        output.write("\n\n;;postlude\n")
        output.write("end:\n	jump end\n")
        if output is not sys.stdout:
            output.close()

    def printDot(self, filename, view=False):
        # Only used in Lab 5
        graph = nx.DiGraph()
        self._start.printDot(graph, set())
        graph.graph['graph'] = dict()
        graph.graph['graph']['overlap'] = 'false'
        nx.drawing.nx_agraph.write_dot(graph, filename)
        gz.render('dot', 'pdf', filename)
        if view:
            gz.view(filename + '.pdf')
