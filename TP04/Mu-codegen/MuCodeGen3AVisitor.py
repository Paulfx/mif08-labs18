from MuVisitor import MuVisitor
from MuParser import MuParser
from APISaruman import (SARUMANProg, Condition)
from antlr4.tree.Trees import Trees

"""
CAP, MIF08, three-address code generation + simple alloc
This visitor constructs an object of type "SARUMANProg"
and the corresponding CFG
"""


class MuCodeGen3AVisitor(MuVisitor):

    def __init__(self, debug, parser):
        super().__init__()
        self._parser = parser
        self._debug = debug
        self._memory = dict()
        # 3-address code generation
        self._prog = SARUMANProg()
        self._lastlabel = ""
        self.ctx_stack = []  # useful for nested ITE

    def get_prog(self):
        return self._prog

    def printRegisterMap(self):
        print("--variables to memory map--")
        for keys, values in self._memory.items():
            print(keys + '-->' + str(values))

    # handle variable decl

    def visitVarDecl(self, ctx):
        vars_l = self.visit(ctx.id_l())
        for name in vars_l:
            if name in self._memory:
                print("Warning, variable %s has already been declared", name)
            else:
                self._memory[name] = self._prog.new_tmp()
        return

    def visitIdList(self, ctx):
        t = self.visit(ctx.id_l())
        t.append(ctx.ID().getText())
        return t

    def visitIdListBase(self, ctx):
        return [ctx.ID().getText()]

    # expressions

    def visitParExpr(self, ctx):
        return self.visit(ctx.expr())

    def visitNumberAtom(self, ctx):
        return self.processNumber(ctx.getText())

    def visitBooleanAtom(self, ctx):
        # true is 1 false is 0
        return self.processNumber(ctx.getText() == "true")

    # Not generated
    def processNumber(self, n):
        try:
            val = int(n)
            # this is valid for val beetween -2^15 and 2^15 -1
            dr = self._prog.new_tmp()
            self._prog.addInstructionLETI(dr, val)
            return dr
        except ValueError:
            raise NotImplementedError("float value")

    def visitIdAtom(self, ctx):
        try:
            # get the register or the shift(dec) associated to id
            regval = self._memory[ctx.getText()]
            return regval
        except KeyError:
            raise Exception("Undefined variable, this should have failed to typecheck.")

    def visitStringAtom(self, ctx):
        raise NotImplementedError("string atom")

    # now visit expressions : TODO

    def visitAtomExpr(self, ctx):
        # An atom can be a number (int only)
        # a boolean or an id (string not implemented) 
        return self.visit(ctx.atom())

    def visitAdditiveExpr(self, ctx):
        t1 = self.visit(ctx.expr()[0])
        t2 = self.visit(ctx.expr()[1])
        dr = self._prog.new_tmp()
        if ctx.myop.type == MuParser.PLUS:
            self._prog.addInstructionADD(dr, t1, t2)
        elif ctx.myop.type == MuParser.MINUS :
            self._prog.addInstructionSUB(dr, t1, t2)
        else :
            raise Exception("Unknown additive operator '%s'" % ctx.myop)
        return dr

    def visitOrExpr(self, ctx):
        dr = _prog.new_tmp()
        tmpl = self.visit(ctx.expr()[0])
        tmpr = self.visit(ctx.expr()[1])
        self._prog.addInstructionOR(dr, tmpl, tmpr)
        return dr

    def visitAndExpr(self, ctx):
        dr = _prog.new_tmp()
        tmpl = self.visit(ctx.expr()[0])
        tmpr = self.visit(ctx.expr()[1])
        self._prog.addInstructionAND(dr, tmpl, tmpr)
        return dr

    def visitEqualityExpr(self, ctx):
        # Rule equalityExpr works like relationalExpr (condition created with myop)
        return self.visitRelationalExpr(ctx)

    def visitRelationalExpr(self, ctx):
        if self._debug:
            print("relational expression:")
            print(Trees.toStringTree(ctx, None, self._parser))
        # get the tmp register that store the value of the evaluation of exprs
        tmpl = self.visit(ctx.expr(0))
        tmpr = self.visit(ctx.expr(1))
        # Generate a new tmp register to store result
        dr = self._prog.new_tmp()
        # Create the condition for the condjump
        c = Condition(ctx.myop.type)
        endrel = self._prog.new_label("endrel")
        self._prog.addInstructionLETI(dr,1)
        #If tmpl is COND tmpr
        #Then don't change value of dr (already true=1) -> jump to end
        self._prog.addInstructionCondJUMP(endrel, tmpl, c, tmpr)
        #else store false(0) in dr
        self._prog.addInstructionLETI(dr,0)
        self._prog.addLabel(endrel)
        return dr

    def visitMultiplicativeExpr(self, ctx):
        raise NotImplementedError("multexpr")

    def visitNotExpr(self, ctx):
        reg = self.visit(ctx.expr())
        dr = self._prog.new_tmp()
        endnot = self._prog.new_label("endnot")
        #Init dr at false
        self._prog.addInstructionLETI(dr,0)
        #If value stored in reg is not false
        #Let dr at false(0) and return dr
        self._prog.addInstructionCondJUMP(endnot, reg, Condition(MuParser.NEQ), dr)
        #else return true
        self._prog.addInstructionLETI(dr,1)
        self._prog.addLabel(endnot)
        return dr

    def visitUnaryMinusExpr(self, ctx):
        reg = self.visit(ctx.expr())
        dr = self._prog.new_tmp()
        #Substract value of reg and 0 and store in dr
        self._prog.addInstructionSUB(dr,0,reg)
        return dr

# statements
    def visitProgRule(self, ctx):
        self.visit(ctx.vardecl_l())
        self.visit(ctx.block())
        if self._debug:
            self.printRegisterMap()

    def visitAssignStat(self, ctx):
        if self._debug:
            print("assign statement, rightexpression is:")
            print(Trees.toStringTree(ctx.expr(), None, self._parser))
        reg4expr = self.visit(ctx.expr())
        name = ctx.ID().getText()
        # find in table
        if name in self._memory:
            self._prog.addInstructionLET(self._memory[name], reg4expr)
        else:
            raise Exception("Variable is not declared")

    def visitCondBlock(self, ctx):
        if self._debug:
            print("condblockstatement, condition is:")
            print(Trees.toStringTree(ctx.expr(), None, self._parser))
            print("and block is:")
            print(Trees.toStringTree(ctx.stat_block(), None, self._parser))
        end_if = self.ctx_stack[-1]  # get the label for the end!
        raise NotImplementedError()

    def visitIfStat(self, ctx):
        if self._debug:
            print("if statement")
        # invent a new label, then push in the label stack
        if_ctx_end_if = self._prog.new_label("end_if")
        self.ctx_stack.append(if_ctx_end_if)
        raise NotImplementedError()
        # At the end, put the label and pop!
        self._prog.addLabel(if_ctx_end_if)
        popped = self.ctx_stack.pop()
        assert popped is if_ctx_end_if

    def visitWhileStat(self, ctx):
        if self._debug:
            print("while statement, condition is:")
            print(Trees.toStringTree(ctx.expr(), None, self._parser))
            print("and block is:")
            print(Trees.toStringTree(ctx.stat_block(), None, self._parser))
        raise NotImplementedError()

    def visitLogStat(self, ctx):
        expr_loc = self.visit(ctx.expr())
        if self._debug:
            print("log statement, expression is:")
            print(Trees.toStringTree(ctx.expr(), None, self._parser))
        self._prog.addInstructionPRINT(expr_loc)

    def visitStatList(self, ctx):
        for stat in ctx.stat():
            self._prog.addComment(Trees.toStringTree(stat, None, self._parser))
            self.visit(stat)
