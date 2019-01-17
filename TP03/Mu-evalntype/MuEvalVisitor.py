from MuVisitor import MuVisitor
from MuParser import MuParser

# Visitor to *interpret* Mu files


class MuRuntimeError(Exception):
    pass


class MuInternalError(Exception):
    pass


class MuEvalVisitor(MuVisitor):

    def __init__(self):
        self._memory = dict()  # store all variable ids and values.

    # visitors for variable declarations

    def visitVarDecl(self, ctx):
        # Initialise all variables in self._memory (toto |-> None)
        vars_l = self.visit(ctx.id_l())
        for var in vars_l:
            self._memory[var] = None #TODO DEMANDER
        return

    def visitIdList(self, ctx):
        listeID = self.visit(ctx.id_l())
        name = ctx.ID().getText()
        return listeID.append(name)

    def visitIdListBase(self, ctx):
        return [ctx.ID().getText()]

    # visitors for atoms --> value
    # this code is given to students except for idatoms !

    def visitParExpr(self, ctx):
        return self.visit(ctx.expr())

    def visitNumberAtom(self, ctx):
        s = ctx.getText()
        try:
            return int(s)
        except ValueError:
            return float(s)

    def visitBooleanAtom(self, ctx):
        return ctx.getText() == "true"

    def visitIdAtom(self, ctx):
        name = ctx.ID().getText()
        value = self._memory[name]
        if value == None :
            raise MuRuntimeError(name + " has no value yet!")
        return value

    def visitStringAtom(self, ctx):
        return ctx.getText()[1:-1]

    # visit expressions
    # this code is given to students
    def visitAtomExpr(self, ctx):
        return self.visit(ctx.atom())

    def visitOrExpr(self, ctx):
        lval = self.visit(ctx.expr(0))
        rval = self.visit(ctx.expr(1))
        return lval | rval

    def visitAndExpr(self, ctx):
        lval = self.visit(ctx.expr(0))
        rval = self.visit(ctx.expr(1))
        return lval & rval

    def visitEqualityExpr(self, ctx):
        lval = self.visit(ctx.expr(0))
        rval = self.visit(ctx.expr(1))
        # be careful for float equality
        if ctx.myop.type == MuParser.EQ:
            return lval == rval
        else:
            return lval != rval

    def visitRelationalExpr(self, ctx):
        lval = self.visit(ctx.expr(0))
        rval = self.visit(ctx.expr(1))
        if ctx.myop.type == MuParser.LT:
            return lval < rval
        elif ctx.myop.type == MuParser.LTEQ:
            return lval <= rval
        elif ctx.myop.type == MuParser.GT:
            return lval > rval
        elif ctx.myop.type == MuParser.GTEQ:
            return lval >= rval
        else:
            raise MuInternalError("Unknown comparison operator '%s'" % ctx.myop)

    def visitAdditiveExpr(self, ctx):
        lval = self.visit(ctx.expr(0))
        rval = self.visit(ctx.expr(1))
        if ctx.myop.type == MuParser.PLUS:
            if any(isinstance(x, str) for x in (lval, rval)):
                return '{}{}'.format(lval, rval)
            else:
                return lval + rval
        elif ctx.myop.type == MuParser.MINUS:
            return lval - rval
        else:
            raise MuInternalError("Unknown additive operator '%s'" % ctx.myop)

    def visitMultiplicativeExpr(self, ctx):
        lval = self.visit(ctx.expr(0))
        rval = self.visit(ctx.expr(1))
        if ctx.myop.type == MuParser.MULT:
            return lval * rval
        elif ctx.myop.type == MuParser.DIV:
            if rval == 0:
                raise MuRuntimeError("Division by 0")
            if isinstance(lval, int):
                return lval // rval
            else:
                return lval / rval
        elif ctx.myop.type == MuParser.MOD:
            return lval % rval
        else:
            raise MuInternalError("Unknown multiplication operator '%s'"
                                  % ctx.myop)

    def visitNotExpr(self, ctx):
        return not self.visit(ctx.expr())

    def visitUnaryMinusExpr(self, ctx):
        return -self.visit(ctx.expr())

    # visit statements

    def visitLogStat(self, ctx):
        val = self.visit(ctx.expr())
        if isinstance(val, bool):
            val = '1' if val else '0'
        if isinstance(val, float):
            val = "%.2f" % val
        print(val)

    def visitAssignStat(self, ctx):
        name = ctx.ID().getText()
        value = self.visit(ctx.expr())
        self._memory[name] = value


    def visitCondBlock(self, ctx):
        cond = self.visit(ctx.expr())
        if cond :
            self.visit(ctx.stat_block())
            return True
        return False

    def visitIfStat(self, ctx):
        for cond in ctx.condition_block() :
            if (self.visit(cond)) :
                break
        else :
            self.visit(ctx.stat_block())

    def visitWhileStat(self, ctx):
        while self.visit(ctx.expr()) :
            self.visit(ctx.stat_block())