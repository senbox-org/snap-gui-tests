from rply import ParserGenerator, ParsingError
import ast
import builtin


__ops__ = {
    '+': ast.Add,
    '-': ast.Sub,
    '*': ast.Mul,
    '/': ast.Div,
    '>': ast.Gt,
    '<': ast.Lt,
    '>=' : ast.GEt,
    '<=' : ast.LEt,
    '==' : ast.Eq,
    '!=' : ast.NEq,
    'AND': ast.And,
    'OR' : ast.Or,
    '+=' : ast.Add,
    '-=' : ast.Sub,
    '*=' : ast.Mul,
    '/=' : ast.Div
}

__conv__ = {
    'float' : ast.NumFloat,
    'int' : ast.NumInt,
    'str' : ast.TypString,
    'bool' : ast.TypBool
}

class Parser:
  
    def __init__(self):
        self.pg = ParserGenerator(
            # A list of all token names, accepted by the parser.
            ['LP','RP','INT', 'PRINT', 'READ', '2FLOAT', '2INT', '2BOOL', '2STRING', 'SEMI', 'COMMENT', 'LB', 'RB', 'LET', 'IDENTIFIER', 'EQ',
            'FLOAT','PLUS', 'MINUS', 'MUL', 'DIV', ',', 'FUNCTION', 'BOOLEAN', 'STRING', 'RETURN', "IF", "ELSE",
            '==', '!=', '>=', '<=', '>', '<', 'AND', 'OR', 'NOT', 'WHILE', 'FOR', 'IMPORT', 'AS', 'COLON', 'CONNECT', 'PROCEDURE','TEST',
            '+=', '-=', '*=', '/=', '++', '--', 'CLICK', 'MENU', 'EXTERNAL_VARIABLE'
            ],
            # A list of precedence rules with ascending precedence, to
            # disambiguate ambiguous production rules.
            precedence=[ 
                ('left', ['line']), 
                ('left', ['block']),
                ('left', ['RETURN', 'IDENTIFIER']),
                ('left', ['exp', 'identifier']),
                ('left', ['VAR', 'var','f_call', 'EXTERNAL_VARIABLE']),
                ('left', ['EQ', 'IF', '+=','-=','*=','/=','++','--','arg','exp_list']),
                ('left', ['ELSE']),
                ('left', ['AND', 'OR']),
                ('left', ['==','!=']),
                ('left', ['>','>=','<','<=']),
                ('left', ['PLUS', 'MINUS', 'NOT']),
                ('left', ['MUL', 'DIV'])]
        )


    def __init_parse__(self):
        @self.pg.production('main : line')
        def main_ml(p):
            return builtin.Main(p[0])

        @self.pg.production('exp : RETURN exp')
        def exp_return(p):
            return ast.Return(p[1])

        @self.pg.production('exp : var')
        @self.pg.production('exp : f_call')
        def exp_var(p):
            return p[0]

        @self.pg.production('exp : STRING')
        def exp_str(p):
            return ast.TypString(p[0].getstr())

        @self.pg.production('exp : BOOLEAN')
        def exp_bool(p):
            return ast.TypBool(p[0].getstr())


        @self.pg.production('exp : INT')
        def exp_int(p):
            return ast.NumInt(p[0].getstr())

        @self.pg.production('exp : FLOAT')
        def exp_float(p):
            return ast.NumFloat(p[0].getstr())

        @self.pg.production('f_call : PRINT arg')
        def fprint(p):
            return ast.Print(p[1])

        @self.pg.production('f_call : READ arg')
        def fread(p):
            return ast.Read()

        @self.pg.production('f_call : CONNECT arg')
        def fconnect(p):
            return builtin.ClientConnect(p[1])

        @self.pg.production('f_call : MENU arg')
        def fmenu(p):
            return builtin.Menu(p[1][0], p[1][1])

        @self.pg.production('f_call : CLICK arg')
        def fclcik(p):
            return builtin.Click(p[1][0])

        @self.pg.production('exp_list : exp , exp')
        def exp_list(p):
            return [p[0], p[2]]

        @self.pg.production('exp_list : exp_list , exp')
        def ext_exp_list(p):
            x = p[0].append(p[2])
            print(x)
            return x
            
        @self.pg.production('arg : LP exp RP')
        def arg(p):
            return [p[1]]

        @self.pg.production('arg : LP exp_list RP')
        def args(p):
            return p[1]

        @self.pg.production('arg : LP RP')
        def noarg(p):
            return []

        @self.pg.production('skip : COMMENT')
        def skip_cmnt(p):
            return ast.Comment(p[0].getstr())

        @self.pg.production('line : exp SEMI')
        @self.pg.production('line : skip')
        @self.pg.production('line : f_def')
        @self.pg.production('line : block')
        def expression_line(p):
            return ast.Line(p[0])

        @self.pg.production('line : line exp SEMI')
        @self.pg.production('line : line skip')
        @self.pg.production('line : line block')
        @self.pg.production('line : line f_def')
        def line_line(p):
            return p[0].extend(p[1])

        @self.pg.production('block : LB line RB')
        def block(p):
            return ast.Block(p[1])

        @self.pg.production('block : LB RB')
        def empty_block(p):
            return ast.Block(None)

        @self.pg.production('var : IDENTIFIER')
        def variable(p):
            return ast.Variable(p[0].getstr())

        @self.pg.production('var : LET var')
        def let_variable(p):
            p[1].let=True
            return p[1]

        @self.pg.production('f_def : FUNCTION f_call block')
        def f_def(p):
            return ast.FDefine(p[1].name, p[1].args, p[2])

        @self.pg.production('f_def : PROCEDURE f_call block')
        def p_def(p):
            return builtin.DefProcedure(p[1].name, p[1].args, p[2])

        @self.pg.production('block : TEST arg block')
        def t_def(p):
            name = p[1][0]
            desc = p[1][1]
            body = p[2]
            return builtin.DefTest(name, desc, body) 

        @self.pg.production('f_call : IDENTIFIER arg')
        def f_call(p):
            return ast.FCall(p[0].getstr(), p[1])

        @self.pg.production('f_call : identifier COLON f_call')
        def id_fcall(p):
            p[2].set_namespace(p[0])
            return p[2]

        @self.pg.production('identifier : IDENTIFIER COLON IDENTIFIER')
        def id_id(p):
            return [p[0].getstr(), p[2].getstr()]

        @self.pg.production('identifier : identifier COLON IDENTIFIER ')
        def mid_id(p):
            return p[0] + [p[2].getstr()]

     

        @self.pg.production('exp : var EQ exp')
        def set_variable(p):
            return ast.Assignment(p[0], p[2])

        @self.pg.production('exp : var += exp')
        @self.pg.production('exp : var -= exp')
        @self.pg.production('exp : var *= exp')
        @self.pg.production('exp : var /= exp')
        def set_op(p):
            op = p[1].getstr()
            return ast.Assignment(p[0], __ops__[op](p[0], p[2]))

        @self.pg.production('exp : var ++')
        def set_pp(p):
            return ast.Assignment(p[0], ast.Add(p[0], ast.NumInt(1)))

        @self.pg.production('exp : var --')
        def set_mm(p):
            return ast.Assignment(p[0], ast.Sub(p[0], ast.NumInt(1)))


        @self.pg.production('exp : exp PLUS exp')
        @self.pg.production('exp : exp MINUS exp')
        @self.pg.production('exp : exp MUL exp')
        @self.pg.production('exp : exp DIV exp')
        @self.pg.production('exp : exp > exp')
        @self.pg.production('exp : exp < exp')
        @self.pg.production('exp : exp >= exp')
        @self.pg.production('exp : exp <= exp')
        @self.pg.production('exp : exp == exp')
        @self.pg.production('exp : exp != exp')
        @self.pg.production('exp : exp OR exp')
        @self.pg.production('exp : exp AND exp')
        def expression_binop(p):
            left = p[0]
            right = p[2]
            return __ops__[p[1].getstr()](left, right)


        @self.pg.production('exp : 2INT LP exp RP')
        @self.pg.production('exp : 2FLOAT LP exp RP')
        @self.pg.production('exp : 2BOOL LP exp RP')
        @self.pg.production('exp : 2STRING LP exp RP')
        def exp_conv(p):
            op = __conv__[p[0].getstr()]
            return op(p[2])

        @self.pg.production('exp : NOT exp')
        def exp_not(p):
            return ast.Not(p[1])

        @self.pg.production('block : IF exp block')
        def exp_if(p):
            return ast.IfElse(p[1], p[2])

        @self.pg.production('block : IF exp block else')
        def exp_ifelse(p):
            return ast.IfElse(p[1], p[2], p[3])

        @self.pg.production('else : ELSE block')
        def b_else(p):
            return p[1]

        @self.pg.production('block : WHILE exp block')
        def b_while(p):
            return ast.While(p[1], p[2])

        @self.pg.production('block : FOR LP exp , exp , exp RP block')
        def b_for(p):
            return ast.For(p[2], p[4], p[6], p[8])

        @self.pg.production('line : IMPORT IDENTIFIER AS IDENTIFIER')
        def l_import_id(p):
            return ast.Line(ast.Import(p[1].getstr(), p[3].getstr()))

        @self.pg.production('line : IMPORT IDENTIFIER')
        def l_import(p):
            return ast.Line(ast.Import(p[1].getstr()))

        @self.pg.production('exp : EXTERNAL_VARIABLE')
        def ext_var(p):
            return ast.ExternalVariable(p[0].getstr())
        


       

    def get_parser(self):
        self.__init_parse__()
        return self.pg.build()