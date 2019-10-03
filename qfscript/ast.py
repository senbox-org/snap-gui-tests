"""
contains all the main and generic classes of the QFScript AST tree.
There is almost one class for any kind of AST node type, each class contains
an `eval` method that will be called during the execution of the script.
Most of the classes implements as well the `__rerp__` method to print nicely the
AST if needed.

@author: Martino Ferrari
@email: manda.mgf@gmail.com
"""
from rply.token import BaseBox
from utils import color
from scope import Scope, RetValue
import scope
import sys

    
class Value(BaseBox):
    """generic value"""
    def __init__(self, value):
        """
        Parameters:
        ----------
        - value: value represented
        """
        self.value = value
        self.inner = isinstance(value, BaseBox)

    def __repr__(self):
        return str(self.value)
    

class NumInt(Value):
    """integer value"""
    def eval(self):
        if isinstance(self.value, BaseBox):
            return int(self.value.eval())
        return int(self.value)
    

class NumFloat(Value): 
    """float value"""   
    def eval(self):
        if self.inner:
            return float(self.value.eval())
        return float(self.value)
    

class TypBool(Value): 
    """bool value"""
    def eval(self):
        if self.inner:
            return bool(self.value.eval())
        return bool(self.value)
    

class TypString(Value):
    """string value"""
    def __init__(self, value):
        self.inner = isinstance(value, BaseBox)
        if isinstance(value, str):
            self.value = value[1:-1]
        else:
            self.value = value
    
    def eval(self):
        if self.inner:
            return str(self.value.eval())
        return str(self.value)
    

class BinaryOp(BaseBox):
    """generic binary operator node"""
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
    def __repr__(self):
        return str(self.left) + ' '+type(self).__name__+' '+str(self.right)


class Add(BinaryOp):
    """addition operator"""
    def eval(self):
        return self.left.eval() + self.right.eval()


class Sub(BinaryOp):
    """substraction operator"""
    def eval(self):
        return self.left.eval() - self.right.eval()


class Mul(BinaryOp):
    """multiplication operator"""
    def eval(self):
        x = self.left.eval()
        y = self.right.eval()
        return x * y


class Div(BinaryOp):
    """division operator"""
    def eval(self):
        return self.left.eval() / self.right.eval()
    

class Gt(BinaryOp):
    """greater then operator"""
    def eval(self):
        return self.left.eval() > self.right.eval()


class GEt(BinaryOp):
    """greater-equal then operator"""
    def eval(self):
        return self.left.eval() >= self.right.eval()
          

class Lt(BinaryOp):
    """less then operator"""
    def eval(self):
        return self.left.eval() < self.right.eval()
          

class LEt(BinaryOp):
    """less-equal then operator"""
    def eval(self):
        return self.left.eval() <= self.right.eval()
          

class Eq(BinaryOp):
    """equal operator"""
    def eval(self):
        return self.left.eval() == self.right.eval()


class NEq(BinaryOp):
    """not-equal operator"""
    def eval(self):
        return self.left.eval() != self.right.eval()
    

class And(BinaryOp):
    """boolean and operator"""
    def eval(self):
        return self.left.eval() and self.right.eval()


class Or(BinaryOp):
    """boolean or operator"""
    def eval(self):
        return self.left.eval() or self.right.eval()
    
    
class Not(BaseBox):
    """boolean not operator (not binary of course)"""
    def __init__(self, val):
        self.right = val
        
    def eval(self):
        return not self.right.eval()


class Block(BaseBox):
    """code block node."""
    def __init__(self, body):
        """
        Parameters
        ----------
        - body: list of lines nodes representing the block
        """
        self.body = body

    def eval(self):        
        """
        evaluates code block line by line.

        Returns
        -------
        - Something if any Return node is inside the code block
        - None otherwise 
        """
        if self.body is None:
            pass
        scope.set_scope(Scope(scope.scope()))
        x = self.body.eval()
        scope.set_scope(scope.scope().parent)
        if isinstance(x, RetValue):
            return x.value
        return None
    
    def __repr__(self):
        inner = str(self.body).split('\n')
        res = '{'
        for l in inner:
            res += '\n\t'+l
        res+='\n}'
        return res
        
        
class Print(BaseBox):
    """print node, mostly useful for debug."""
    def __init__(self, arg):
        self.arg = arg
    
    def eval(self):
        """use print python function to print the arguments."""
        res = ''
        for a in self.arg:
            res += str(a.eval())+' '
        print(f'{res}')
        
    def __repr__(self):
        r = 'print('
        for i, a in enumerate(self.arg):
            if i > 0 :
                r += ', '
            r += str(a)
        return r+')'
        

class Read(BaseBox):
    """reads console input node. mostly useful for debug."""
    def __repr__(self):
        return 'read()'
    
    def eval(self):
        return input()
    

class Variable(BaseBox):
    """variable node, represent both call and definition of a variable."""
    def __init__(self, name, let = False):
        """
        Parameters
        ----------
        - name: name of the variable (identifier)
        - let: flag for definition or call (default false)
        """
        self.name = name
        self.let = let
        
    def eval(self):
        """defines the variable or returns the value of the variable depending on
        the  value of the field `let`."""
        if self.let:
            scope.scope().let_var(self.name)
        else:
            return scope.scope().var(self.name)
        
    def __repr__(self):
        return ("let " if self.let else "") + self.name
    
    
class FDefine(BaseBox):
    """function definition node."""" 
    def __init__(self, name, args, body):
        """
        Parameters
        ----------
        - name: function name
        - args: function arguments
        - body: function body
        """
        self.args = args
        self.name = name
        self.body = body
        
    def __repr__(self):
        r = 'func '+self.name+'('
        for i, a in enumerate(self.args):
            if i > 0 :
                r += ', '
            r += str(a)
        return r+')'
    
    def eval(self):
        """
        defines the function in the current scope.
        """
        scope.scope().def_fn(self.name, self.args, self.body)
        pass
        

class FCall(BaseBox):
    """function call node."""
    def __init__(self, name, args, namespace=None):
        """
        Parameters
        ----------
        - name: function name
        - args: function arguments
        - namespace: possible name space
        """
        self.name = name
        self.args = args
        self.namespace = namespace
    
    def eval(self):
        """
        evalues the arguments and uses the scope to call the correct function.
        """
        vals = [x.eval() for x in self.args]
        return scope.scope().fn(self.namespace, self.name, vals)
  
    
    def __repr__(self):
        av = ""
        for m in self.namespace:
            av += m+":"
        r = av+self.name+'('
        for i, a in enumerate(self.args):
            if i > 0 :
                r += ', '
            r += str(a)
        return r+')'
    
    def set_namespace(self, namespace):
        """sets a different namespace for this function node."""
        self.namespace = namespace

class Assignment(BaseBox):
    """variable assignament node."""
    def __init__(self, left, right):
        """
        Parameters
        ----------
        - left: variable
        - right: expression
        """"
        self.left = left
        self.right = right
    
    def eval(self):
        """evalues expression and sets its value to the left variable."""
        self.left.eval()
        scope.scope().set_var(self.left.name, self.right.eval())
        
    def __repr__(self):
        return str(self.left) + " = " + str(self.right)
        

class Line(BaseBox):
    """code line node. It actually represent all the line inside the same code block.""" 
    def __init__(self, value):
        self.value = [value]
    
    def extend(self, l):
        """append an extra line or operation to current line."""
        self.value.append(l)
        return self
    
    def eval(self):
        """evaluats line by line and returns a value 
        (and stops the execution) if a Return node is found."""
        for v in self.value:
            x = v.eval()
            if isinstance(x, RetValue):
                return x
            
    def __repr__(self):
        r = ''
        for i, v in enumerate(self.value):
            if i > 0:
                r += '\n'
            r += str(v)
        return r
        

class Comment(BaseBox):
    """comment node. Simply skips the line."""
    def __init__(self, comment):
        self.text = comment.replace('\n','')
        
    def eval(self):
        pass
    
    def __repr__(self):
        return color.ITALIC+self.text+color.END
    


class Return(BaseBox):
    """
    return node. 
    It blocks the execution of code block and return the values of its expression."""
    def __init__(self, val):
        """
        Paramters
        ---------
        - val: return expression
        """
        self.val = val
    
    def __repr__(self):
        return 'return '+str(self.val)
    
    def eval(self):
        """returns the value of its expression."""
        x = RetValue(self.val.eval())
        return x
    

class IfElse(BaseBox): 
    """if/else node. Note that the else is optional."""
    def __init__(self, cond, body, else_body=None):
        """
        Parameters
        ----------
        - cond: branch condition
        - body: if body
        - else_body: optional else body
        """
        self.cond = cond
        self.body = body
        self.else_body = else_body
    
    def eval(self):
        """
        evaluates the condition and if its true executes the 
        if body otherwise, if any else body is defined, executes
        the else body.
        """ 
        cond = self.cond.eval()
        if cond:
            x = self.body.eval()
            if x != None:
                return RetValue(x)
            return None
        elif self.else_body is not None:
            return self.else_body.eval()
        return None
    
    def __repr__(self):
        r = 'if ('+str(self.cond)+')\n'+str(self.body)
        if self.else_body is not None:
            r += 'else\n'+str(self.else_body)
        return r
    

class While(BaseBox):
    """while loop node."""
    def __init__(self, cond, body):
        """
        Paramters
        ---------
        - cond: while condition
        - body: loop body
        """
        self.cond = cond
        self.body = body
    
    def __repr__(self):
        return 'while '+str(self.cond)+'\n'+str(self.body)
    
    def eval(self):
        """continue to execute the while 
        body until the condition is true"""
        cond = self.cond.eval()
        while cond:
            x = self.body.eval()
            if x is not None:
                return x
            cond = self.cond.eval()
        return None
    
 
class For(BaseBox):
    """for loop node. Basically a while with extra steps."""
    def __init__(self,init, cond, cmd, body):
        """
        Parameters
        ----------
        - init: init expression (e.g. let i = 0)
        - cond: for condition (e.g. i < 10)
        - cmd: loop expression (e.g. i++)
        - body: loop body
        """
        self.init = init
        self.cond = cond
        self.cmd = cmd
        self.body = body
        
    def __repr__(self):
        return 'for ('+str(self.init)+', '+str(self.cond)+', '+str(self.cmd)+')\n'+str(self.body)
    
    def eval(self):
        """first evaluates the init expression, then execute the loop body until the condition is true.
        At every loops execute the loop expression as weel."""
        scope.set_scope(Scope(scope.scope()))
        self.init.eval()
        cond = self.cond.eval()
        while cond:
            x = self.body.eval()
            if x is not None:
                return x
            self.cmd.eval()
            cond = self.cond.eval()
        scope.set_scope(scope.scope().parent)
        return None

class Import(BaseBox):
    """import node. It include external script resources in a new namespace."""
    def __init__(self, resource, name=None):
        """
        Parameters
        ----------
        - resource: name of the resource to import without extension
        - name: name to use for this resource, if not defined is simply the resource name
        """
        self.resource = resource
        self.name = name if name is not None else resource
    
    def eval(self):
        """uses the scope to import a new resource."""
        scope.scope().import_scope(self.name, scope.load_scope(self.resource))


class ExternalVariable(BaseBox):
    """external variable. To be used with jenkins and the test generation suits."""
    def __init__(self, name):
        self.name = name 

    def __repr__(self):
        return self.name

    def eval(self):
        return self.name