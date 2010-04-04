# Compilers - Project 2
# Reykjavik University, Spring 2010
# Haukur Jonasson, Skuli Arnlaugsson

# This is the lexical analyser file as requested in part 5 of the assignment.
# -*- coding: utf-8 -*-
import sys
from ply.lex import lex
from parser import Parser

def main(*args):
    # Generate our parser, with the given input

    if len(sys.argv) > 1:
        inputFile = sys.argv[1]
        if len(sys.argv) > 2:
            option = True
        else:
            option = False
    else:
        inputFile = 'pas_syntax_ok'
        option = False

    filename = 'input/'+inputFile
    print '  -------------------------------'
    print '  Using input "%s"'%inputFile
    print '  -------------------------------'
    parser = Parser(filename)

    # Start parsing!
    parser.parse(option)

    fileHandler = open(filename)
    pointer = 0

    if not option:
        while True:
            pointer += 1
            line = fileHandler.readline()
            if not line: break
            if pointer < 10: print ' %d:\t%s'%(pointer,line),
            else: print '%d:\t%s'%(pointer,line),
            for error in parser.errors:
                if error.lineno == pointer:
                    print error.pointPrint()
                    # With break only the first error in the line will be displayed
                    #break

        print
        print '  -------------------------------'

    if len(parser.errors) == 0:
        print '  No errors were detected.'
    else:
        print '  %d errors were encountered.'%len(parser.errors)
    print

if __name__ == '__main__':
	sys.exit(main(*sys.argv))