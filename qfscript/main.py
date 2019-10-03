from lexer import Lexer
from parser import Parser
from rply import ParsingError
import utils
import sys

args = sys.argv[1:]
if len(args) != 1:
    print("pass the source code!")
    sys.exit(3)

with open(args[0],'r') as f:
    code = f.read()
    try:
        lexer = Lexer().get_lexer()
        parser = Parser().get_parser()
        ast = parser.parse(lexer.lex(code))
        ast.eval()
    except ParsingError as e:
        utils.print_error(code, e.source_pos)