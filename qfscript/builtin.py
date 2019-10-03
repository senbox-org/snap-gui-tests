from lxml import etree
from rply.token import BaseBox
import ast
import scope
import qftxml
import sys



class ClientConnect(BaseBox):
    def __init__(self, path):
        self.path = path
    
    def eval(self):
        path = self.path[0].eval()

        qftxml.set_var('path', path)
        # qftxml.client_waiter('$(client)', raiseerr=False, varname='isRunning', timeout=1000)
        # qftxml.if_seq('check if is running', 'not $(isRunning)')
        qftxml.client_starter('$(client)', '$(path)')
        qftxml.client_waiter('$(client)', timeout=10000)
        qftxml.set_current(qftxml.current().getparent())

    def __repr__(self):
        return "connect("+self.path+")"

class Main(BaseBox):
    def __init__(self, body):
        self.body = body
        self.imported = False

    def eval(self):
        if not self.imported:
            qftxml.init_root()
        scope.set_scope(scope.scope())
        x = self.body.eval()
        if not self.imported and 'main' in scope.scope().functions :
            x = scope.scope().fn('main',[])   
            if x is not None and type(x) is int:
                qftxml.print_xml()
        if not self.imported:
            qftxml.print_xml()
            sys.exit(x)  
        return x
    
    def __repr__(self):
        inner = str(self.body).split('\n')
        res = '{'
        for l in inner:
            res += '\n\t'+l
        res+='\n}'
        return res
    
class DefProcedure(BaseBox):
    def __init__(self, name, args, body):
        self.args = args
        self.name = name
        self.body = body
        
    def __repr__(self):
        r = 'procedure '+self.name+'('
        for i, a in enumerate(self.args):
            if i > 0 :
                r += ', '
            r += str(a)
        return r+')'
    
    def eval(self):
        scope.scope().def_proc(self.name, self.args, self.body)


   

    
class DefTest(BaseBox):
    def __init__(self, name, desc, body):
        self.name = name.eval()
        self.description = desc.eval()
        self.body = body
        self.__done__ = False

    def eval(self):
        if self.__done__ or not scope.scope().is_testable():
            pass
        test = etree.SubElement(qftxml.testset, "TestCase")
        qftxml.set_id(test)
        test.set("name", self.name)
        test.set("reportname", self.description)
        old_current = qftxml.current()
        qftxml.set_current(test)
        self.body.eval()
        qftxml.set_current(old_current)
        self.__done__ = True

    def __repr__(self):
        return "test "+self.name
 

class Click(BaseBox):
    def __init__(self, comp_id):
        self.comp_id = comp_id

    def __repr__(self):
        return "click("+str(self.comp_id)+')'
    
    def eval(self):
        cid = self.comp_id.eval()
        qftxml.click(qftxml.current(), cid)
        pass

class Menu(BaseBox):
    def __init__(self, window, item):
        self.window = window
        self.item = item

    def __repr__(self):
        return 'menu('+str(self.window)+', '+str(self.item)+')'

    def eval(self):
        win_id = self.window.eval()
        item = self.item.eval()
        items = item.split('/')
        win = qftxml.get_win(win_id)
        menu = qftxml.get_menubar(win)
        for item in items:
            submenu = item[0] == '^'
            name = item[1:] if submenu else item
            menu = qftxml.get_menuitem(menu, name, submenu)
        return menu.get('id')