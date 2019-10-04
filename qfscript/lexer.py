"""
Custom lexer for QFScript language 

@author: Martino Ferrari
@email: manda.mgf@gmail.com
"""
from rply import LexerGenerator

class Lexer():
    """
    Manages all the lexer definitions for tokenize QFScripts.
    """
    def __init__(self):
        # init lexer generator
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        """inits all tokens."""

        # comments
        self.lexer.add('COMMENT', r'//.*\n') # in line only for the moment

        # types
        self.lexer.add('FLOAT', r'(\s-)?\d?\.\d+e?-\d+|(\s-)?\d+e?-\d+|(\s-)?\d+\.\d+')  
        self.lexer.add('INT', r'(\s-)?\d+')        
        self.lexer.add('STRING', r'(\"([^\\\n]|(\\.))*?\")|(\'([^\\\n]|(\\.))*?\')')
        self.lexer.add('BOOLEAN', r"true|false")

        # increment and decrement shortcut
        self.lexer.add('++', r'\+\+')
        self.lexer.add('--', r'\-\-')

        # operators
        self.lexer.add('PLUS', r'\+')
        self.lexer.add('MINUS', r'-')
        self.lexer.add('MUL', r'\*')
        self.lexer.add('DIV', r'/')
        self.lexer.add('AND', r"\&\&(?!\w)")
        self.lexer.add('OR', r"\|\|(?!\w)")
        self.lexer.add('NOT', r"\!(?!\w)")
        self.lexer.add('==', '==')
        self.lexer.add('!=', '!=')
        self.lexer.add('>=', '>=')
        self.lexer.add('<=', '<=')
        self.lexer.add('>', '>')
        self.lexer.add('<', '<')

        # reflective operators
        self.lexer.add('+=', r'\+\=')
        self.lexer.add('-=', r'\-\=')
        self.lexer.add('/=', r'\/\=')
        self.lexer.add('*=', r'\*\=')

        # parentesis
        self.lexer.add('LP', r'\(')
        self.lexer.add('RP', r'\)')
        self.lexer.add('LB', r'\{')
        self.lexer.add('RB', r'\}')
        self.lexer.add('LS', r'\[')
        self.lexer.add('RS', r'\]')
        
        # special symbols
        self.lexer.add('EQ', r'=')
        self.lexer.add(',', r'\,')
        self.lexer.add('DOT', r'\.')
        self.lexer.add('SEMI', r';')
        self.lexer.add('COLON', r':')

        # generic keywords
        self.lexer.add('FUNCTION', r'func(?!\w)')
        self.lexer.add('PROCEDURE', r'proc(?!\w)')
        self.lexer.add('TEST', r'test(?!\w)')
        self.lexer.add('LET', r'let(?!\w)')

        self.lexer.add('IF', r'if(?!\w)')
        self.lexer.add('ELSE', r'else(?!\w)')

        self.lexer.add('WHILE', r'while(?!\w)')
        self.lexer.add('FOR', r'for(?!\w)')

        #built in function
        self.lexer.add('PRINT', r'print')
        self.lexer.add('READ', r'read')
        self.lexer.add('2STRING', r'str')
        self.lexer.add('2INT', r'int')
        self.lexer.add('2FLOAT', r'float')
        self.lexer.add('2BOOL', r'bool')

        #QFTest specific
        self.lexer.add('CONNECT', r'connect(?!\w)')
        self.lexer.add('CLICK', r'click(?!\w)')
        self.lexer.add('MENU', r'menu(?!\w)')

        # other keywords
        self.lexer.add('RETURN', r'return(?!\w)')
        self.lexer.add('IMPORT', r'import(?!\w)')
        self.lexer.add('AS', r'as(?!\w)')
        self.lexer.add('IDENTIFIER', r"[a-zA-Z_][a-zA-Z0-9_]*")
        self.lexer.add('HEADER_IDENTIFIER', r"\@[a-zA-Z_][a-zA-Z0-9_]*")
        self.lexer.add('EXTERNAL_VARIABLE', r"\$[a-zA-Z_][a-zA-Z0-9_]*")

        # ignore white spaces
        self.lexer.ignore(r'\s+')


    def get_lexer(self):
        """retrives a QFScript ready lexer."""
        self._add_tokens()
        return self.lexer.build()
