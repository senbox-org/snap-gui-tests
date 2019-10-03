from rply.token import BaseBox
from utils import color
from scope import Scope, RetValue
import scope
import sys




        
class Function(BaseBox):
    def __init__(self, args, body):
        self.args = args
        self.block = body
    
    def eval(self, args):
        scope.set_scope(Scope(scope.scope()))
        for (var, value) in zip(self.args, args):
            name = var.name
            scope.scope().let_var(name)
            scope.scope().set_var(name, value)
        res = self.block.body.eval()
        scope.set_scope(scope.scope().parent)
        if isinstance(res, RetValue):
            return res.value
        return None
    
    
class Value(BaseBox):
    def __init__(self, value):
        self.value = value
        self.inner = isinstance(value, BaseBox)

    def __repr__(self):
        return str(self.value)
    

class NumInt(Value):
    def eval(self):
        if isinstance(self.value, BaseBox):
            return int(self.value.eval())
        return int(self.value)
    

class NumFloat(Value):    
    def eval(self):
        if self.inner:
            return float(self.value.eval())
        return float(self.value)
    

class TypBool(Value): 
    def eval(self):
        if self.inner:
            return bool(self.value.eval())
        return bool(self.value)
    

class TypString(Value):
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
    def __init__(self, left, right):
        self.left = left
        self.right = right
        
    def __repr__(self):
        return str(self.left) + ' '+type(self).__name__+' '+str(self.right)


class Add(BinaryOp):
    def eval(self):
        return self.left.eval() + self.right.eval()


class Sub(BinaryOp):
    def eval(self):
        return self.left.eval() - self.right.eval()


class Mul(BinaryOp):
    def eval(self):
        x = self.left.eval()
        y = self.right.eval()
        return x * y


class Div(BinaryOp):
    def eval(self):
        return self.left.eval() / self.right.eval()
    

class Gt(BinaryOp):
    def eval(self):
        return self.left.eval() > self.right.eval()


class GEt(BinaryOp):
    def eval(self):
        return self.left.eval() >= self.right.eval()
          

class Lt(BinaryOp):
    def eval(self):
        return self.left.eval() < self.right.eval()
          

class LEt(BinaryOp):
    def eval(self):
        return self.left.eval() <= self.right.eval()
          

class Eq(BinaryOp):
    def eval(self):
        return self.left.eval() == self.right.eval()


class NEq(BinaryOp):
    def eval(self):
        return self.left.eval() != self.right.eval()
    

class And(BinaryOp):
    def eval(self):
        return self.left.eval() and self.right.eval()


class Or(BinaryOp):
    def eval(self):
        return self.left.eval() or self.right.eval()
    
    
class Not(BaseBox):
    def __init__(self, val):
        self.right = val
        
    def eval(self):
        return not self.right.eval()


class Block(BaseBox):
    def __init__(self, body):
        self.body = body

    def eval(self):        
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
    def __init__(self, arg):
        self.arg = arg
    
    def eval(self):
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
    def __repr__(self):
        return 'read()'
    
    def eval(self):
        return input()
    

class Variable(BaseBox):
    def __init__(self, name, let = False):
        self.name = name
        self.let = let
        
    def eval(self):
        if self.let:
            scope.scope().let_var(self.name)
        else:
            return scope.scope().var(self.name)
        
    def __repr__(self):
        return ("let " if self.let else "") + self.name
    
    
class FDefine(BaseBox):
    def __init__(self, name, args, body):
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
        scope.scope().def_fn(self.name, self.args, self.body)
        pass
        

class FCall(BaseBox):
    def __init__(self, name, args, namespace=None):
        self.name = name
        self.args = args
        self.namespace = namespace
    
    def eval(self):
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
        self.namespace = namespace

class Assignment(BaseBox):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def eval(self):
        self.left.eval()
        scope.scope().set_var(self.left.name, self.right.eval())
        
    def __repr__(self):
        return str(self.left) + " = " + str(self.right)
        

class Line(BaseBox):
    def __init__(self, value):
        self.value = [value]
    def extend(self, l):
        self.value.append(l)
        return self
    
    def eval(self):
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
    def __init__(self, comment):
        self.text = comment.replace('\n','')
        
    def eval(self):
        pass
    
    def __repr__(self):
        return color.ITALIC+self.text+color.END
    


class Return(BaseBox):
    def __init__(self, val):
        self.val = val
    
    def __repr__(self):
        return 'return '+str(self.val)
    
    def eval(self):
        x = RetValue(self.val.eval())
        return x
    

class IfElse(BaseBox): 
    def __init__(self, cond, body, else_body=None):
        self.cond = cond
        self.body = body
        self.else_body = else_body
    
    def eval(self):
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
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body
    
    def __repr__(self):
        return 'while '+str(self.cond)+'\n'+str(self.body)
    
    def eval(self):
        cond = self.cond.eval()
        while cond:
            x = self.body.eval()
            if x is not None:
                return x
            cond = self.cond.eval()
        return None
    
 
class For(BaseBox):
    def __init__(self,init, cond, cmd, body):
        self.init = init
        self.cond = cond
        self.cmd = cmd
        self.body = body
        
    def __repr__(self):
        return 'for ('+str(self.init)+', '+str(self.cond)+', '+str(self.cmd)+')\n'+str(self.body)
    
    def eval(self):
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
    def __init__(self, resource, name=None):
        self.resource = resource
        self.name = name if name is not None else resource
    
    def eval(self):
        scope.scope().import_scope(self.name, scope.load_scope(self.resource))


class ExternalVariable(BaseBox):
    def __init__(self, name):
        self.name = name 

    def __repr__(self):
        return self.name

    def eval(self):
        return self.name