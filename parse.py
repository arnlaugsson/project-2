# Compilers - Project 2
# Reykjavik University, Spring 2010
# Haukur Jonasson, Skuli Arnlaugsson

#
# -*- coding: utf-8 -*-
import sys
from scanner import Scanner
from token import *
import token

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
        print "\tE  "+" "*(self.columnno-2) + "^--- " + self.message #+ " (at line %s column %s)"%(self.lineno,self.columnno)

def error(classInstance,token,nonTerminal):
    classInstance.errors.append()

class Parser:
    def __init__(self,input):
        self.scanner = Scanner(input)
        self.currentToken = None
        self.errors = []
        self.readTokens = []

    def callersname(self):
        return sys._getframe(2).f_code.co_name

    def error(self,token,message):
        self.errors.append(Error(token.lineno,token.columnno,message))

    def recover(self):
        # Todo: add error recovery
        pass

    def match(self,expectedInput):
        if self.currentToken.TokenCode != expectedInput:
            message = 'Expected %s but got %s while in %s'%(expectedInput,self.currentToken.TokenCode,self.callersname())
            self.error(self.currentToken,message)
            self.recover()
        self.currentToken = self.scanner.nextToken()

    def parse(self):
        self.currentToken = self.scanner.nextToken()
        self.parseProgram()
        self.match('tc_EOF')

    def parseProgram(self):
        self.parseProgramDefinition()
        self.match('tc_SEMICOL')
        self.parseDeclarations()
        self.parseSubprogramDeclarations()
        self.parseCompoundStatement()
        self.match('tc_DOT')

    def parseProgramDefinition(self):
        self.match('tc_PROGRAM')
        self.match('tc_ID')
        self.match('tc_LPAREN')
        self.parseIdentifierList()
        self.match('tc_RPAREN')

    def parseIdentifierList(self):
        self.match('tc_ID')
        self.parseIdentifierListRest()

    def parseIdentifierListRest(self):
        if self.currentToken.TokenCode == 'tc_COMMA':
            self.match('tc_COMMA')
            self.match('tc_ID')
            self.parseIdentifierListRest()

    def parseDeclarations(self):
        self.match('tc_VAR')
        self.parseIdentifierList()
        self.match('tc_COLON')
        self.parseType()
        self.match('tc_SEMICOL')
        self.parseDeclarationsRest()

    def parseDeclarationsRest(self):
        if self.currentToken.TokenCode == 'tc_VAR':
            self.parseDeclarations()

    def parseType(self):
        if self.currentToken.TokenCode == 'tc_ARRAY':
            self.match('tc_ARRAY')
            self.match('tc_LBRACKET')
            self.match('tc_NUMBER')
            self.match('tc_DOTDOT')
            self.match('tc_NUMBER')
            self.match('tc_RBRACKET')
            self.match('tc_OF')
        self.parseStandardType()

    def parseStandardType(self):
        if self.currentToken.TokenCode == 'tc_INTEGER':
            self.match('tc_INTEGER')
        else:
            self.match('tc_REAL')

    def parseSubprogramDeclarations(self):
        if self.currentToken.TokenCode == 'tc_FUNCTION':
            self.parseSubprogramDeclaration()
            self.match('tc_SEMICOL')
            self.parseSubprogramDeclarations()
        elif self.currentToken.TokenCode == 'tc_PROCEDURE':
            self.parseSubprogramDeclaration()
            self.match('tc_SEMICOL')
            self.parseSubprogramDeclarations()

    def parseSubprogramDeclaration(self):
        self.parseSubprogramHead()
        self.parseDeclarations()
        self.parseCompoundStatement()

    def parseSubprogramHead(self):
        if self.currentToken.TokenCode == 'tc_FUNCTION':
            self.match('tc_FUNCTION')
            self.match('tc_ID')
            self.parseArguments()
            self.match('tc_COLON')
            self.parseStandardType()
        elif self.currentToken.TokenCode == 'tc_PROCEDURE':
            self.match('tc_PROCEDURE')
            self.match('tc_ID')
            self.parseArguments()
        else:
            # Error - must be either one
            pass
        self.match('tc_SEMICOL')

    def parseArguments(self):
        if self.currentToken.TokenCode == 'tc_LPAREN':
            self.match('tc_LPAREN')
            self.parseParameterList()
            self.match('tc_RPAREN')

    def parseParameterList(self):
        self.parseIdentifierList()
        self.match('tc_COLON')
        self.parseType()
        self.parseParameterListRest()

    def parseParameterListRest(self):
        if self.currentToken.TokenCode == 'tc_SEMICOL':
            self.match('tc_SEMICOL')
            self.parseIdentifierList()
            self.match('tc_COLON')
            self.parseType()
            self.parseParameterListRest()

    def parseCompoundStatement(self):
        self.match('tc_BEGIN')
        self.parseOptionalStatements()
        self.match('tc_END')

    def parseOptionalStatements(self):
        if self.currentToken.TokenCode != 'tc_END':
            self.parseStatementList()

    def parseStatementList(self):
        self.parseStatement()
        self.parseStatementListRest()

    def parseStatementListRest(self):
        if self.currentToken.TokenCode == 'tc_SEMICOL':
            self.match('tc_SEMICOL')
            self.parseStatementList()

    def parseStatement(self):
        if self.currentToken.TokenCode == 'tc_ID':
            # 'Procedure statement' or 'variable assign-op expression'
            self.match('tc_ID')
            if self.currentToken.TokenCode == 'tc_ASSIGNOP':
                self.match('tc_ASSIGNOP')
                self.parseExpression()
            elif self.currentToken.TokenCode == 'tc_LBRACKET':
                self.parseVariableRest()
                self.match('tc_ASSIGNOP')
                self.parseExpression()
            elif self.currentToken.TokenCode == 'tc_LPAREN':
                self.parseProcedureStatementRest()
        elif self.currentToken.TokenCode == 'tc_BEGIN':
            self.parseCompoundStatement()
        elif self.currentToken.TokenCode == 'tc_IF':
            self.match('tc_IF')
            self.parseExpression()
            self.match('tc_THEN')
            self.parseStatement()
            self.match('tc_ELSE')
            self.parseStatement()
        elif self.currentToken.TokenCode == 'tc_WHILE':
            self.match('tc_WHILE')
            self.parseExpression()
            self.match('tc_DO')
            self.parseStatement()
        else:
            # Error - should be something above
            pass

    def parseVariable(self):
        # Not needed, is implemented in parseStatement, but kept here for completeness.
        self.match('tc_ID')
        self.parseVariableRest()

    def parseVariableRest(self):
        if self.currentToken.TokenCode == 'tc_LBRACKET':
            self.match('tc_LBRACKET')
            self.parseExpression()
            self.match('tc_RBRACKET')
            self.parseVariableRest()

    def parseProcedureStatement(self):
        # Not needed, is implemented in parseStatement, but kept here for completeness.
        self.match('tc_ID')
        self.parseProcedureStatementRest()

    def parseProcedureStatementRest(self):
        if self.currentToken.TokenCode == 'tc_LPAREN':
            self.match('tc_LPAREN')
            self.parseExpressionList()
            self.match('tc_RPAREN')
            self.parseProcedureStatementRest()

    def parseExpressionList(self):
        self.parseExpression()
        self.parseExpressionListRest()

    def parseExpressionListRest(self):
        if self.currentToken.TokenCode == 'tc_COMMA':
            self.match('tc_COMMA')
            self.parseExpression()
            self.parseExpressionListRest()

    def parseExpression(self):
        self.parseSimpleExpression()
        self.parseExpressionRest()

    def parseExpressionRest(self):
        if self.currentToken.TokenCode == 'tc_RELOP':
            self.match('tc_RELOP')
            self.parseSimpleExpression()

    def parseSimpleExpression(self):
        if self.currentToken.TokenCode == 'tc_ADDOP':
            self.match('tc_ADDOP')
        self.parseTerm()
        self.parseSimpleExpressionRest()

    def parseSimpleExpressionRest(self):
        if self.currentToken.TokenCode == 'tc_ADDOP':
            self.match('tc_ADDOP')
            self.parseTerm()
            self.parseSimpleExpressionRest()

    def parseTerm(self):
        self.parseFactor()
        self.parseTermRest()

    def parseTermRest(self):
        if self.currentToken.TokenCode == 'tc_MULOP':
            self.match('tc_MULOP')
            self.parseFactor()
            self.parseTermRest()

    def parseFactor(self):
        if self.currentToken.TokenCode == 'tc_LPAREN':
            self.match('tc_LPAREN')
            self.parseExpression()
            self.match('tc_RPAREN')
        elif self.currentToken.TokenCode == 'tc_NOT':
            self.match('tc_NOT')
            self.parseFactor()
        elif self.currentToken.TokenCode == 'tc_NUMBER':
            self.match('tc_NUMBER')
        elif self.currentToken.TokenCode == 'tc_ID':
            self.match('tc_ID')
            if self.currentToken.TokenCode == 'tc_LPAREN':
                self.match('tc_LPAREN')
                self.parseExpressionList()
                self.match('tc_RPAREN')
            elif self.currentToken.TokenCode == 'tc_LBRACKET':
                self.match('tc_LBRACKET')
                self.parseExpression()
                self.match('tc_RBRACKET')
                self.parseVariableRest()

    def parseSign(self):
        # Not needed, is implemented in parseStatement, but kept here for completeness.
        self.match('tc_ADDOP')

