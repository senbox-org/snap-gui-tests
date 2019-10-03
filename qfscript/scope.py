from rply.token import BaseBox
import qftxml
from lxml import etree

__current__ = None


def __init_scope__():
    global __current__
    __current__ = Scope(None)
    

def scope():
    global __current__
    if __current__ is None:
        __init_scope__()
    return __current__


def set_scope(sc):
    global __current__
    __current__ = sc


def load_scope(res):
    with open(res+'.qfs','r') as f:
        import lexer
        import parser
        code = f.read()
        l = lexer.Lexer().get_lexer()
        p = parser.Parser().get_parser()
        ast = p.parse(l.lex(code))
        old_scope = scope()
        new_scope = Scope(None, imported=True)
        set_scope(new_scope)
        ast.imported = True
        ast.eval()
        set_scope(old_scope)
        return new_scope
    return None

class Scope:
    def __init__(self, parent, imported=None):
        self.parent = parent
        self.functions = {}
        self.variables = {}
        self.imports = {}
        self.objects = {}
        self.tests = []
        if imported is None:
            self.imported = parent.imported if parent is not None else False
        else:
            self.imported = imported
    
    def var(self, name):
        if name in self.variables:
            return self.variables[name]
        elif self.parent is not None:
            return self.parent.var(name)
        raise NameError("Variable `"+name+"` is note defined")
        
    def fn(self, namespace, name, args):
        if namespace is None:
            if name in self.functions:
                return self.functions[name].eval(args)
            elif self.parent is not None:
                return self.parent.fn(name, args)
        else:
            return self.__eval_namespace__(namespace, name, args)
        raise NameError("Function `"+name+"` is not defined")
    
    def __eval_namespace__(self, ns, fname, args):
        if ns[0] == 'std':
            qftxml.std_procedure(ns[1:], fname, args)
            return None
        mod = self.mod(ns[0])
        if mod is None:
            raise NameError(f"Module `{mod}` is not imported")
        set_scope(mod)
        v = mod.fn(fname, args)
        set_scope(self)
        return v

    def def_fn(self, name, args, body):
        self.functions[name] = Function(args, body)

    def def_proc(self, name, args, body):
        self.functions[name] = Procedure(name, args, body)
    
    def has_var(self, name):
        if name in self.variables:
            return True
        elif self.parent is not None:
            return self.parent.has_var(name)
        return False
    
    def set_var(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        elif self.parent is not None:
            self.parent.set_var(name, value)
        return None
        
    def let_var(self, name):
        self.variables[name] = None

    def import_scope(self, name, scope):
        self.imports[name] = scope
        
    def mod(self, name):
        if name in self.imports:
            return self.imports[name]
        elif self.parent is not None:
            return self.parent.mod(name)
        return None

    def obj(self, id):
        if id in self.objects:
            return self.objects[id]
        if self.parent is not None:
            return self.parent.obj(id)
        raise NameError(f"Object `{id}` not found!")

    def is_testable(self):
        return not self.imported

    

            
class Function(BaseBox):
    def __init__(self, args, body):
        self.args = args
        self.block = body
    
    def eval(self, args):
        set_scope(Scope(scope()))
        for (var, value) in zip(self.args, args):
            name = var.name
            scope().let_var(name)
            scope().set_var(name, value)
        res = self.block.body.eval()
        set_scope(scope().parent)
        if isinstance(res, RetValue):
            return res.value
        return None

    
class Procedure(BaseBox):
    def __init__(self, name, args, body):
        self.args = args
        self.name = name
        self.block = body
        self.written = False
    
    def eval(self, args):
        if not self.written:
            self.__write_def__()
        self.__write_call__()

    def __write_call__(self):
        el = etree.SubElement(qftxml.current(), "ProcedureCall") 
        qftxml.set_id(el)
        el.set("procedure", self.name)
        pass

    def __write_def__(self):
        proc = etree.SubElement(qftxml.package, "Procedure")
        qftxml.set_id(proc)
        proc.set("name", self.name)
        old_current = qftxml.current()
        qftxml.set_current(proc)
        self.block.eval()
        qftxml.set_current(old_current)
        self.written = True


class RetValue(BaseBox):
    def __init__(self, value):
        self.value = value
        
    def eval(self):
        return self.value

