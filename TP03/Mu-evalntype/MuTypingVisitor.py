from MuVisitor import MuVisitor
from MuParser import MuParser

from enum import Enum


class MuTypeError(Exception):
    pass


class BaseType(Enum):
    Float, Integer, Boolean, String = range(4)

    def printBaseType(self):
        print(self)


class ArrayType():
    def __init__(self, content):
        self.content = content

    def __eq__(self, other):
        if not isinstance(other, ArrayType):
            return False
        return self.content == other.content


# Basic Type Checking for Mu programs.
class MuTypingVisitor(MuVisitor):

    def __init__(self):
        self._memorytypes = dict()  # id-> types

    def _raise(self, ctx, for_what, *types):
        raise MuTypeError(
            'Line {} col {}: invalid type for {}: {}'.format(
                ctx.start.line, ctx.start.column, for_what,
                ' and '.join(t.name.lower() for t in types)))

    # type declaration

    def visitVarDecl(self, ctx):
        vars_l = self.visit(ctx.id_l())
        tt = self.visit(ctx.typee())
        for name in vars_l:
            if name in self._memorytypes:
                raise MuTypeError("Variable {} already declared".format(name))
            self._memorytypes[name] = tt
        return


    def visitBasicType(self, ctx):
        if ctx.mytype.type == MuParser.INTTYPE:
            return BaseType.Integer
        elif ctx.mytype.type == MuParser.FLOATTYPE:
            return BaseType.Float
        elif ctx.mytype.type == MuParser.BOOLTYPE:
            return BaseType.Boolean
        elif ctx.mytype.type == MuParser.STRINGTYPE:
            return BaseType.String
        else:
            raise Exception("Type not implemented")



    def visitIdList(self, ctx):
        t = self.visit(ctx.id_l())
        t.append(ctx.ID().getText())
        return t


    def visitIdListBase(self, ctx):
        return [ctx.ID().getText()]


    # typing visitors for expressions, statements !

    # visitors for atoms --> value
    def visitParExpr(self, ctx):
        return self.visit(ctx.expr())

    def visitNumberAtom(self, ctx):
        s = ctx.getText()
        try:
            int(s)
            return BaseType.Integer
        except ValueError:
            try:
                float(s)
                return BaseType.Float
            except ValueError:
                raise MuTypeError("Invalid number atom")

    def visitBooleanAtom(self, ctx):
        return BaseType.Boolean


    def visitIdAtom(self, ctx):
        try:
            valtype = self._memorytypes[ctx.getText()]
            return valtype
        except KeyError:
            raise MuTypeError("Undefined variable {}".format(ctx.getText()))

    def visitStringAtom(self, ctx):
        return BaseType.String

    # now visit expr

    def visitAtomExpr(self, ctx):
        return self.visit(ctx.atom())

    def visitOrExpr(self, ctx):
        lvaltype = self.visit(ctx.expr(0))
        rvaltype = self.visit(ctx.expr(1))
        if (BaseType.Boolean == lvaltype) and (BaseType.Boolean == rvaltype):
            return BaseType.Boolean
        else:
            self._raise(ctx, 'boolean operands', lvaltype, rvaltype)


    def visitAndExpr(self, ctx):
        lvaltype = self.visit(ctx.expr(0))
        rvaltype = self.visit(ctx.expr(1))
        if (BaseType.Boolean == lvaltype) and (BaseType.Boolean == rvaltype):
            return BaseType.Boolean
        else:
            self._raise(ctx, 'boolean operands', lvaltype, rvaltype)


    def visitEqualityExpr(self, ctx):
        lvaltype = self.visit(ctx.expr(0))
        rvaltype = self.visit(ctx.expr(1))

        if lvaltype != rvaltype:
            self._raise(ctx, 'equality operands', lvaltype, rvaltype)

        return BaseType.Boolean


    def visitRelationalExpr(self, ctx):
        lvaltype = self.visit(ctx.expr(0))
        rvaltype = self.visit(ctx.expr(1))

        if lvaltype != rvaltype:
            self._raise(ctx, 'relational operands', lvaltype, rvaltype)

        if lvaltype not in (BaseType.Integer, BaseType.Float):
            self._raise(ctx, 'relational operands', lvaltype)

        return BaseType.Boolean


    def visitAdditiveExpr(self, ctx):
        lvaltype = self.visit(ctx.expr(0))
        rvaltype = self.visit(ctx.expr(1))

        if lvaltype != rvaltype:
            self._raise(ctx, 'additive operands', lvaltype, rvaltype)
        if lvaltype not in (BaseType.Integer, BaseType.Float, BaseType.String):
            self._raise(ctx, 'additive operands', lvaltype, rvaltype)
        if ctx.myop.type != MuParser.PLUS and lvaltype == BaseType.String:
            self._raise(ctx, 'additive operands', lvaltype, rvaltype)

        return lvaltype


    def visitMultiplicativeExpr(self, ctx):
        lvaltype = self.visit(ctx.expr(0))
        rvaltype = self.visit(ctx.expr(1))

        if lvaltype != rvaltype:
            self._raise(ctx, 'multiplicative operands', lvaltype, rvaltype)

        if lvaltype not in (BaseType.Integer, BaseType.Float):
            self._raise(ctx, 'multiplicative operands', lvaltype, rvaltype)

        return lvaltype


    def visitNotExpr(self, ctx):
        etype = self.visit(ctx.expr())
        if etype != BaseType.Boolean:
            self._raise(ctx, 'not expression', etype)
        else:
            return BaseType.Boolean


    def visitUnaryMinusExpr(self, ctx):
        etype = self.visit(ctx.expr())
        if etype not in (BaseType.Integer, BaseType.Float):
            self._raise(ctx, 'unary minus operand', etype)

        return etype


    # statements
    def visitAssignStat(self, ctx):
        valtype = self.visit(ctx.expr())
        name = ctx.ID().getText()
        if name not in self._memorytypes:
            raise MuTypeError("Undefined variable "+name)
        if self._memorytypes[name] != valtype:
            raise MuTypeError("Mismatch types for "+name)


    def visitCondBlock(self, ctx):
        condtype = self.visit(ctx.expr())
        if condtype != BaseType.Boolean:
            self._raise(ctx, 'conditional block', condtype)
        self.visit(ctx.stat_block())


    def visitWhileStat(self, ctx):
        condtype = self.visit(ctx.expr())
        if condtype != BaseType.Boolean:
            self._raise(ctx, 'while condition', condtype)
        self.visit(ctx.stat_block())


    def visitIfStat(self, ctx):
        for cond in ctx.condition_block():
            self.visit(cond)
        if ctx.stat_block() is not None:
            self.visit(ctx.stat_block())


