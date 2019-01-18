# Generated from Mu.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .MuParser import MuParser
else:
    from MuParser import MuParser

# This class defines a complete generic visitor for a parse tree produced by MuParser.

class MuVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MuParser#progRule.
    def visitProgRule(self, ctx:MuParser.ProgRuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#varDeclList.
    def visitVarDeclList(self, ctx:MuParser.VarDeclListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#varDecl.
    def visitVarDecl(self, ctx:MuParser.VarDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#idListBase.
    def visitIdListBase(self, ctx:MuParser.IdListBaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#idList.
    def visitIdList(self, ctx:MuParser.IdListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#statList.
    def visitStatList(self, ctx:MuParser.StatListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#stat.
    def visitStat(self, ctx:MuParser.StatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#assignStat.
    def visitAssignStat(self, ctx:MuParser.AssignStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#ifStat.
    def visitIfStat(self, ctx:MuParser.IfStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#condBlock.
    def visitCondBlock(self, ctx:MuParser.CondBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#stat_block.
    def visitStat_block(self, ctx:MuParser.Stat_blockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#whileStat.
    def visitWhileStat(self, ctx:MuParser.WhileStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#logStat.
    def visitLogStat(self, ctx:MuParser.LogStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#notExpr.
    def visitNotExpr(self, ctx:MuParser.NotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#unaryMinusExpr.
    def visitUnaryMinusExpr(self, ctx:MuParser.UnaryMinusExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#atomExpr.
    def visitAtomExpr(self, ctx:MuParser.AtomExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#orExpr.
    def visitOrExpr(self, ctx:MuParser.OrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#additiveExpr.
    def visitAdditiveExpr(self, ctx:MuParser.AdditiveExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#relationalExpr.
    def visitRelationalExpr(self, ctx:MuParser.RelationalExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#multiplicativeExpr.
    def visitMultiplicativeExpr(self, ctx:MuParser.MultiplicativeExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#equalityExpr.
    def visitEqualityExpr(self, ctx:MuParser.EqualityExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#andExpr.
    def visitAndExpr(self, ctx:MuParser.AndExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#parExpr.
    def visitParExpr(self, ctx:MuParser.ParExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#numberAtom.
    def visitNumberAtom(self, ctx:MuParser.NumberAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#booleanAtom.
    def visitBooleanAtom(self, ctx:MuParser.BooleanAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#idAtom.
    def visitIdAtom(self, ctx:MuParser.IdAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#stringAtom.
    def visitStringAtom(self, ctx:MuParser.StringAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MuParser#basicType.
    def visitBasicType(self, ctx:MuParser.BasicTypeContext):
        return self.visitChildren(ctx)



del MuParser