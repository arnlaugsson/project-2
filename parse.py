# Compilers - Project 2
# Reykjavik University, Spring 2010
# Haukur Jonasson, Skuli Arnlaugsson

#
# -*- coding: utf-8 -*-
import sys
from scanner import Scanner
from token import *
import token
from synchronizingSets import syncsets

class Error:
    """ An instance of the Error class is a parser error encountered during parsing.
        It has three attributes:
            lineno, charnum and the error message.
    """
    def __init__(self, lineno, columnno, message):
        self.lineno = lineno
        self.columnno = columnno
        self.message = message
    def __repr__(self):
        return 'Line %d:%d: \t%s'%(self.lineno,self.columnno,self.message)
    def pointPrint(self):
        print "\t   "+" "*(self.columnno-2) + "^--- " + self.message

class Parser:
    def __init__(self,input):
        self.__scanner = Scanner(input)
        self.__currentToken = None
        self.__foundError = False
        self.__errorInFunction = ''
        self.errors = []

        
    def parse(self):
        """
        This is the accesible parse function.
        """
        self.__currentToken = self.__scanner.nextToken()
        self.__Program()
        self.__match('tc_EOF')

    def __callersname(self):
        # Simply returns the parent function name. Used to find the correct follow set.
        return sys._getframe(2).f_code.co_name

    def __addError(self,token,message):
        # Simply appends a new instance of the error class to the error list.
        self.errors.append(Error(token.lineno,token.columnno,message))

    def __recover(self):
        # If we find a token in the follow set, we do not skip
        skip = True

        for tc in syncsets[self.__errorInFunction]:
            if self.__currentToken.TokenCode != tc:
                self.__currentToken = self.__scanner.nextToken()
            else:
                # Token found in sync set
                skip = False
                break

        if skip:
            self.__currentToken = self.__scanner.nextToken()
        
        # Reset after recovery
        self.__foundError = False
        self.__errorInFunction = ''

    def __match(self,expectedIn):
        if self.__foundError: return
        if self.__currentToken.TokenCode != expectedIn:
            callFunc = self.__callersname()
            recTC = self.__currentToken.TokenCode
            message = 'Expected %s not %s while in %s'%(expectedIn[3:],recTC[3:],callFunc)
            self.__addError(self.__currentToken,message)
            self.__foundError = True
            self.__errorInFunction = callFunc

        self.__currentToken = self.__scanner.nextToken()

    def __Program(self):

        self.__ProgramDefinition()
        if self.__foundError: self.__recover()

        self.__match('tc_SEMICOL')


        self.__Declarations()
        if self.__foundError: self.__recover()


        self.__SubprogramDeclarations()
        if self.__foundError: self.__recover()


        self.__CompoundStatement()
        if self.__foundError: self.__recover()

        self.__match('tc_DOT')

    def __ProgramDefinition(self):
        self.__match('tc_PROGRAM')
        self.__match('tc_ID')
        self.__match('tc_LPAREN')
        self.__IdentifierList()
        if self.__foundError: self.__recover()
        self.__match('tc_RPAREN')

    def __IdentifierList(self):
        self.__match('tc_ID')
        self.__IdentifierListRest()

    def __IdentifierListRest(self):
        if self.__currentToken.TokenCode == 'tc_COMMA':
            self.__match('tc_COMMA')
            self.__match('tc_ID')
            self.__IdentifierListRest()

    def __Declarations(self):
        self.__match('tc_VAR')
        self.__IdentifierList()
        if self.__foundError: self.__recover()
        self.__match('tc_COLON')
        self.__Type()
        if self.__foundError: self.__recover()
        self.__match('tc_SEMICOL')
        self.__DeclarationsRest()

    def __DeclarationsRest(self):
        if self.__currentToken.TokenCode == 'tc_VAR':
            self.__Declarations()
            if self.__foundError: self.__recover()

    def __Type(self):
        if self.__currentToken.TokenCode == 'tc_ARRAY':
            self.__match('tc_ARRAY')
            self.__match('tc_LBRACKET')
            self.__match('tc_NUMBER')
            self.__match('tc_DOTDOT')
            self.__match('tc_NUMBER')
            self.__match('tc_RBRACKET')
            self.__match('tc_OF')
        self.__StandardType()
        if self.__foundError: self.__recover()

    def __StandardType(self):
        if self.__currentToken.TokenCode == 'tc_INTEGER':
            self.__match('tc_INTEGER')
        else:
            self.__match('tc_REAL')

    def __SubprogramDeclarations(self):
        if self.__currentToken.TokenCode == 'tc_FUNCTION':
            self.__SubprogramDeclaration()
            if self.__foundError: self.__recover()
            self.__match('tc_SEMICOL')
            self.__SubprogramDeclarations()
            if self.__foundError: self.__recover()
        elif self.__currentToken.TokenCode == 'tc_PROCEDURE':
            self.__SubprogramDeclaration()
            if self.__foundError: self.__recover()
            self.__match('tc_SEMICOL')
            self.__SubprogramDeclarations()
            if self.__foundError: self.__recover()

    def __SubprogramDeclaration(self):
        self.__SubprogramHead()
        if self.__foundError: self.__recover()
        self.__Declarations()
        if self.__foundError: self.__recover()
        self.__CompoundStatement()
        if self.__foundError: self.__recover()

    def __SubprogramHead(self):
        if self.__currentToken.TokenCode == 'tc_FUNCTION':
            self.__match('tc_FUNCTION')
            self.__match('tc_ID')
            self.__Arguments()
            if self.__foundError: self.__recover()
            self.__match('tc_COLON')
            self.__StandardType()
            if self.__foundError: self.__recover()
        elif self.__currentToken.TokenCode == 'tc_PROCEDURE':
            self.__match('tc_PROCEDURE')
            self.__match('tc_ID')
            self.__Arguments()
            if self.__foundError: self.__recover()
        else:
            # Error - must be either one
            pass
        self.__match('tc_SEMICOL')

    def __Arguments(self):
        if self.__currentToken.TokenCode == 'tc_LPAREN':
            self.__match('tc_LPAREN')
            self.__ParameterList()
            if self.__foundError: self.__recover()
            self.__match('tc_RPAREN')

    def __ParameterList(self):
        self.__IdentifierList()
        if self.__foundError: self.__recover()
        self.__match('tc_COLON')
        self.__Type()
        if self.__foundError: self.__recover()
        self.__ParameterListRest()

    def __ParameterListRest(self):
        if self.__currentToken.TokenCode == 'tc_SEMICOL':
            self.__match('tc_SEMICOL')
            self.__IdentifierList()
            if self.__foundError: self.__recover()
            self.__match('tc_COLON')
            self.__Type()
            if self.__foundError: self.__recover()
            self.__ParameterListRest()

    def __CompoundStatement(self):
        self.__match('tc_BEGIN')
        self.__OptionalStatements()
        if self.__foundError: self.__recover()
        self.__match('tc_END')

    def __OptionalStatements(self):
        if self.__currentToken.TokenCode != 'tc_END':
            self.__StatementList()
            if self.__foundError: self.__recover()

    def __StatementList(self):
        self.__Statement()
        if self.__foundError: self.__recover()
        self.__StatementListRest()

    def __StatementListRest(self):
        if self.__currentToken.TokenCode == 'tc_SEMICOL':
            self.__match('tc_SEMICOL')
            self.__StatementList()
            if self.__foundError: self.__recover()

    def __Statement(self):
        if self.__currentToken.TokenCode == 'tc_ID':
            # 'Procedure statement' or 'variable assign-op expression'
            self.__match('tc_ID')
            if self.__currentToken.TokenCode == 'tc_ASSIGNOP':
                self.__match('tc_ASSIGNOP')
                self.__Expression()
                if self.__foundError: self.__recover()
            elif self.__currentToken.TokenCode == 'tc_LBRACKET':
                self.__VariableRest()
                self.__match('tc_ASSIGNOP')
                self.__Expression()
                if self.__foundError: self.__recover()
            elif self.__currentToken.TokenCode == 'tc_LPAREN':
                self.__ProcedureStatementRest()
        elif self.__currentToken.TokenCode == 'tc_BEGIN':
            self.__CompoundStatement()
            if self.__foundError: self.__recover()
        elif self.__currentToken.TokenCode == 'tc_IF':
            self.__match('tc_IF')
            self.__Expression()
            if self.__foundError: self.__recover()
            self.__match('tc_THEN')
            self.__Statement()
            if self.__foundError: self.__recover()
            self.__match('tc_ELSE')
            self.__Statement()
            if self.__foundError: self.__recover()
        elif self.__currentToken.TokenCode == 'tc_WHILE':
            self.__match('tc_WHILE')
            self.__Expression()
            if self.__foundError: self.__recover()
            self.__match('tc_DO')
            self.__Statement()
            if self.__foundError: self.__recover()
        else:
            # Error - should be something above
            pass

    def __Variable(self):
        # Not needed, is implemented in parseStatement, but kept here for completeness.
        self.__match('tc_ID')
        self.__VariableRest()

    def __VariableRest(self):
        if self.__currentToken.TokenCode == 'tc_LBRACKET':
            self.__match('tc_LBRACKET')
            self.__Expression()
            if self.__foundError: self.__recover()
            self.__match('tc_RBRACKET')
            self.__VariableRest()

    def __ProcedureStatement(self):
        # Not needed, is implemented in parseStatement, but kept here for completeness.
        self.__match('tc_ID')
        self.__ProcedureStatementRest()

    def __ProcedureStatementRest(self):
        if self.__currentToken.TokenCode == 'tc_LPAREN':
            self.__match('tc_LPAREN')
            self.__ExpressionList()
            if self.__foundError: self.__recover()
            self.__match('tc_RPAREN')
            self.__ProcedureStatementRest()

    def __ExpressionList(self):
        self.__Expression()
        if self.__foundError: self.__recover()
        self.__ExpressionListRest()

    def __ExpressionListRest(self):
        if self.__currentToken.TokenCode == 'tc_COMMA':
            self.__match('tc_COMMA')
            self.__Expression()
            if self.__foundError: self.__recover()
            self.__ExpressionListRest()

    def __Expression(self):
        self.__SimpleExpression()
        if self.__foundError: self.__recover()
        self.__ExpressionRest()

    def __ExpressionRest(self):
        if self.__currentToken.TokenCode == 'tc_RELOP':
            self.__match('tc_RELOP')
            self.__SimpleExpression()
            if self.__foundError: self.__recover()

    def __SimpleExpression(self):
        if self.__currentToken.TokenCode == 'tc_ADDOP':
            self.__match('tc_ADDOP')
        self.__Term()
        if self.__foundError: self.__recover()
        self.__SimpleExpressionRest()

    def __SimpleExpressionRest(self):
        if self.__currentToken.TokenCode == 'tc_ADDOP':
            self.__match('tc_ADDOP')
            self.__Term()
            if self.__foundError: self.__recover()
            self.__SimpleExpressionRest()

    def __Term(self):
        self.__Factor()
        if self.__foundError: self.__recover()
        self.__TermRest()

    def __TermRest(self):
        if self.__currentToken.TokenCode == 'tc_MULOP':
            self.__match('tc_MULOP')
            self.__Factor()
            if self.__foundError: self.__recover()
            self.__TermRest()

    def __Factor(self):
        if self.__currentToken.TokenCode == 'tc_LPAREN':
            self.__match('tc_LPAREN')
            self.__Expression()
            if self.__foundError: self.__recover()
            self.__match('tc_RPAREN')
        elif self.__currentToken.TokenCode == 'tc_NOT':
            self.__match('tc_NOT')
            self.__Factor()
            if self.__foundError: self.__recover()
        elif self.__currentToken.TokenCode == 'tc_NUMBER':
            self.__match('tc_NUMBER')
        elif self.__currentToken.TokenCode == 'tc_ID':
            self.__match('tc_ID')
            if self.__currentToken.TokenCode == 'tc_LPAREN':
                self.__match('tc_LPAREN')
                self.__ExpressionList()
                if self.__foundError: self.__recover()
                self.__match('tc_RPAREN')
            elif self.__currentToken.TokenCode == 'tc_LBRACKET':
                self.__match('tc_LBRACKET')
                self.__Expression()
                if self.__foundError: self.__recover()
                self.__match('tc_RBRACKET')
                self.__VariableRest()

    def __Sign(self):
        # Not needed, is implemented in parseStatement, but kept here for completeness.
        self.__match('tc_ADDOP')

