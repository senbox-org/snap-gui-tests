"""
It manages the scopes during the executions as well as 
the function definitions, calls, variable assignements and namespaces.

@author: Martino Ferrari
@email: manda.mgf@gmail.com 
"""
from rply.token import BaseBox
import qftxml
from lxml import etree
import lexer
import parser

# current scope. I know is a global variable... :(
__current__ = None


def __init_scope__():
    global __current__
    __current__ = Scope(None)
    

def scope():
    """gets current scope."""
    global __current__
    if __current__ is None:
        __init_scope__()
    return __current__


def set_scope(sc):
    """sets current scope."""
    global __current__
    __current__ = sc


def load_scope(res):
    """opens a qfs script and imports all its functions."""
    with open(res+'.qfs','r') as f:
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
    """class representing a execution scope."""
    def __init__(self, parent, imported=None):
        """
        Parameters
        ----------
        - parent: parent scope
        - imported: imported flag (avoid executation of tests and main function)
        """
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
    
    def var(self, name, namespace=[]):
        """retrives variable from current scope or parent scopes."""
        if len(namespace) > 0:
            if namespace[0] == 'std':
                return qftxml.std_var(namespace[1:], name)
        if name in self.variables:
            return self.variables[name]
        elif self.parent is not None:
            return self.parent.var(name)
        raise NameError("Variable `"+name+"` is note defined")
        
    def fn(self, namespace, name, args):
        """
        executes function defined in current scope or parents scopes.
        
        Paramters
        ---------
        - namespace: function namespace (can be None if no namespace is defined) 
        - name: function name
        - args: value of its arguments

        Returns
        -------
        returns the value returned from the function
        """
        if namespace is None:
            if name in self.functions:
                return self.functions[name].eval(args)
            elif self.parent is not None:
                return self.parent.fn(None, name, args)
        else:
            return self.__eval_namespace__(namespace, name, args)
        raise NameError("Function `"+name+"` is not defined")
    
    def __eval_namespace__(self, ns, fname, args):
        """manages the mess of namespaces and execute the function in its scope."""
        if ns[0] == 'std':
            qftxml.std_procedure(ns[1:], fname, args)
            return None
        if ns[0] == "qfs":
            qftxml.qfs_procedure(ns[1:], fname, args)
            return None
        mod = self.mod(ns[0])
        if mod is None:
            raise NameError(f"Module `{mod}` is not imported")
        set_scope(mod)
        v = mod.fn(fname, args)
        set_scope(self)
        return v

    def def_fn(self, name, args, body):
        """defines function in the current scope."""
        self.functions[name] = Function(args, body)

    def def_proc(self, name, args, body):
        """defines a QFTest procedure in the current scope."""
        self.functions[name] = Procedure(name, args, body)
    
    def has_var(self, name):
        """check if variable its defined in the current scope or its parents."""
        if name in self.variables:
            return True
        elif self.parent is not None:
            return self.parent.has_var(name)
        return False
    
    def set_var(self, name, value):
        """set variable value."""
        if name in self.variables:
            self.variables[name] = value
        elif self.parent is not None:
            self.parent.set_var(name, value)
        return None
        
    def let_var(self, name):
        """defines variable in current scope."""
        self.variables[name] = None

    def import_scope(self, name, scope):
        """imports a scope in current scope."""
        self.imports[name] = scope
        
    def mod(self, name):
        """retrives a module scope from the current scope or its parents."""
        if name in self.imports:
            return self.imports[name]
        elif self.parent is not None:
            return self.parent.mod(name)
        return None

    def obj(self, id):
        """
        retrives object from current scope or its parents.
        Not used for now.
        """
        if id in self.objects:
            return self.objects[id]
        if self.parent is not None:
            return self.parent.obj(id)
        raise NameError(f"Object `{id}` not found!")

    def is_testable(self):
        """retruns if scope is testable.""" 
        return not self.imported

            
class Function(BaseBox):
    """Function object."""
    def __init__(self, args, body):
        """
        Parameters
        ----------
        - args: function arguments
        - body: function body
        """
        self.args = args
        self.block = body
    
    def eval(self, args):
        """evaluates function in a new empty scope."""
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
    """QFTest Procedure object."""
    def __init__(self, name, args, body):
        """
        Parameters
        ----------
        - name: procedure name
        - args: procedure arguments
        - body: procedure body
        """
        self.args = args
        self.name = name
        self.block = body
        self.written = False
    
    def eval(self, args):
        """compiles  the precedure body if needed and call the procedure."""
        if not self.written:
            self.__write_def__()
        self.__write_call__()

    def __write_call__(self):
        el = etree.SubElement(qftxml.current(), "ProcedureCall") 
        qftxml.set_id(el)
        el.set("procedure", self.name)
        pass

    def __write_def__(self):
        proc = etree.SubElement(qftxml.__package__, "Procedure")
        qftxml.set_id(proc)
        proc.set("name", self.name)
        old_current = qftxml.current()
        qftxml.set_current(proc)
        self.block.eval()
        qftxml.set_current(old_current)
        self.written = True


class RetValue(BaseBox):
    """represents the value of a `return` call.""" 
    def __init__(self, value):
        self.value = value
        
    def eval(self):
        return self.value

