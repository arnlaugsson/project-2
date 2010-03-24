# Compilers - Project 2
# Reykjavik University, Spring 2010
# Haukur Jonasson, Skuli Arnlaugsson

# This is the lexical analyser file as requested in part 5 of the assignment.
# -*- coding: utf-8 -*-
import sys
from ply.lex import lex
from parse import Parser

def main(*args):
    # Generate our parser, with the given input

    inputFile = 'pas_syntax_ok'
    filename = 'input/'+inputFile
    print '  -------------------------------'
    print '  Using input "%s"'%inputFile
    print '  -------------------------------'
    print '   Ln\t|  Code'
    print '  -------------------------------'
    parser = Parser(filename)

    # Start parsing!
    parser.parseProgram()

    fileHandler = open(filename)
    pointer = 1

    while True:
        line = fileHandler.readline()
        if not line: break
        print '   %d\t|  %s'%(pointer,line),
        for error in parser.errors:
            if error.lineno == pointer:
                error.pointPrint()
                break
        pointer += 1

    print
    print '  -------------------------------'

    if len(parser.errors) == 0:
        print '  No errors were detected.'
    else:
        print '  %d errors were encoutered.'%len(parser.errors)
    print

if __name__ == '__main__':
	sys.exit(main(*sys.argv))