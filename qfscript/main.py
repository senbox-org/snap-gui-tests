"""
Execute a QFS script using custom lexer and parser.

@author: Martino Ferrari
@email: manda.mgf@gmail.com
"""
from lexer import Lexer
from parser import Parser
from rply import ParsingError
import utils
import sys

# check arguments
args = sys.argv[1:]
if len(args) != 1:
    print("Source file needed")
    sys.exit(3)

# open and read source file
with open(args[0],'r') as f:
    code = f.read()
    try:
        # prepare lexer and parser
        lexer = Lexer().get_lexer()
        parser = Parser().get_parser()
        # generate AST from code
        ast = parser.parse(lexer.lex(code))
        # evaluate AST
        ast.eval()
    except ParsingError as e:
        utils.print_error(code, e.source_pos)