import sys
from lxml import etree
import os


root = None
testset = None
package = None
extra = None
winlist = None
current_node = None
id = 0

__stdlib__ = {}
__included__ = []
__STDLIB_PATH__ = "../snap/lib/"

def __load_func__(el):
    findVars = etree.XPath("./variable")
    res = []
    for v in findVars(el):
        res.append(v.get("name"))
    return res

def __load_package__(pkgxml):
    findPackage = etree.XPath("./Package")
    findProc = etree.XPath("./Procedure")
    pkg = {}
    for f in findProc(pkgxml):
        name = f.get("name")
        pkg[name] = __load_func__(f)
    for p in findPackage(pkgxml):
        name = p.get("name")
        pkg[name] = __load_package__(p)
    return pkg

def __load_stdlib__():
    findPRoot = etree.XPath("//PackageRoot")
    for f in os.listdir(__STDLIB_PATH__):
        fpath = os.path.join(__STDLIB_PATH__, f)
        if os.path.isfile(fpath):
            if fpath.endswith('.qft'):
                name = f[5:-4]
                mod = {}
                tree = etree.parse(fpath)
                proot = findPRoot(tree)
                if len(proot) > 0:
                    mod = __load_package__(proot[0])
                __stdlib__[name] = mod

def stdlib_fn_args(ns, fname):
    p = __stdlib__
    path = "std"
    for n in ns:
        if n not in p:
            raise NameError(f"Package `{n}` not found in `{path}`")
        p = p[n]
        path += ":"+n
    if fname not in p:
        raise NameError(f"Function `{fname}` not found in package `{path}`")
    return p[fname]

def print_xml():
    global root
    header = '<?xml version="1.0" encoding="ISO-8859-1"?>\n<!DOCTYPE RootStep>\n'
    xml = etree.tostring(root, pretty_print=True)
    sys.stdout.buffer.write(bytes(header, encoding='utf-8')+xml)


def set_id(el):
    global id
    el.set("id", f'_{id}')
    id += 1

def set_uid(el):
    global id
    el.set("uid", f'_{id}')
    id += 1

def __include__(root, lib):
    include = etree.SubElement(root, "include")
    include.text = lib

def init_root():
    __load_stdlib__()

    global root
    global testset
    global package
    global extra 
    global winlist
    root = etree.Element("RootStep")
    set_id(root)
    root.set("name", "root")
    root.set("version", "4.7.0")
    
    __include__(root, "qfs.qft")

    testset = etree.SubElement(root, "TestSet")
    set_id(testset)
    testset.set("name", "TestSet")
    package = etree.SubElement(root, "PackageRoot")
    set_id(package)
    extra = etree.SubElement(root, "ExtraSequence")
    set_id(extra)
    winlist = etree.SubElement(root, "WindowList")
    set_id(winlist)
    # __init_gui__()
    global current_node 
    current_node = root


def current():
    global current_node
    return current_node


def set_current(el):
    global current_node
    current_node = el


def set_var(name, value):
    el = etree.SubElement(current(), "SetGlobalStep")
    set_id(el)
    el.set("description", "a variable")
    el.set("varname", name)
    val = etree.SubElement(el, "default")
    val.text = value


def client_waiter(client, raiseerr=True, varname=None, timeout=None):
    el = etree.SubElement(current(), "ClientWaiter")
    set_id(el)
    el.set("client", client)
    el.set("raise", "true" if raiseerr else "false")
    if varname is not None:
        el.set("resvarname", varname)
    if timeout is not None:
        el.set("timeout", str(timeout))
    return el


def client_starter(client, executable):
    el = etree.SubElement(current(), "SUTClientStarter")
    set_id(el)
    el.set('client', client)
    el.set('executable', executable)
    return el


def if_seq(name, test):
    el = etree.SubElement(current(), "IfSequence")
    set_id(el)
    el.set('name', name)
    el.set('test', test)
    set_current(el)
    return el


def add_extrafeature(el, name, value, neagate=False, regexp=False, state=0):
    feature = etree.SubElement(el, "extrafeature")
    feature.set('name', name)
    feature.set('negate', 'true' if neagate else 'false')
    feature.set('regexp', 'true' if regexp else 'false')
    feature.set('state', str(state))
    feature.text=value
    return feature

def add_window(root, label, name):
    win = etree.SubElement(root, 'WindowStep')
    set_uid(win)
    win.set('feature', label)
    win.set('id', name)
    win.set('name', name)
    win.set('class', 'Window')
    add_extrafeature(win, 'qfs:class', 'javax.swing.JFrame')
    add_extrafeature(win, 'qfs:genericclass', 'Window')
    add_extrafeature(win, 'qfs:label', label)
    add_extrafeature(win, 'qfs:systemclass', 'javax.swing.JFrame')
    return win

def add_dialog(root, label, name):
    win = etree.SubElement(root, 'WindowStep')
    set_uid(win)
    win.set('feature', label)
    win.set('id', name)
    win.set('name', name)
    win.set('class', 'Dialog')
    add_extrafeature(win, 'qfs:class', 'javax.swing.JDialog')
    add_extrafeature(win, 'qfs:genericclass', 'Dialog')
    add_extrafeature(win, 'qfs:label', label)
    add_extrafeature(win, 'qfs:systemclass', 'javax.swing.JDialog')
    return win

def add_menubar(root, name):
    mbar = etree.SubElement(root, 'ComponentStep')
    mbar.set('class', 'MenuBar')
    id = root.get('id')+'.menubar_'+name
    mbar.set('id', id)
    set_uid(mbar)
    add_extrafeature(mbar, 'qfs:class', 'org.openide.awt.MenuBar')
    add_extrafeature(mbar, 'qfs:genericclass', 'MenuBar')
    add_extrafeature(mbar, 'qfs:systemclass', 'javax.swing.JMenuBar')
    add_extrafeature(mbar, 'qfs:type', 'Menu:MenuBar')
    return mbar

def add_menuitem(root, label, submenu=False):
    mitem = etree.SubElement(root, 'ComponentStep')
    mitem.set('feature', label)
    id = root.get('id')+'.menuitem_'+label.replace(' ', '_')
    mitem.set('id', id)
    mitem.set('name', id)
    mitem.set('class', 'MenuItem')
    set_uid(mitem)
    sysclass = "javax.swing.JMenu" if submenu else "javax.swing.JMenuItem"
    add_extrafeature(mitem, 'qfs:class', sysclass)
    add_extrafeature(mitem, 'qfs:genericclass', 'MenuItem')
    add_extrafeature(mitem, 'qfs:systemclass', sysclass)
    add_extrafeature(mitem, 'qfs:label', label, state=1)
    return mitem
    
def add_button(root, label):
    btn = etree.SubElement(root, 'ComponentStep')
    btn.set('class', 'Button')
    btn.set('feature', label)
    id = root.get('id')+'.button_'+label.replace(' ','_')
    btn.set('name', id)
    btn.set('id', id)
    set_uid(btn)
    sysclass = "javax.swing.JButton"
    add_extrafeature(btn, 'qfs:class', sysclass)
    add_extrafeature(btn, 'qfs:genericclass', 'Button')
    add_extrafeature(btn, 'qfs:systemclass', sysclass)
    add_extrafeature(btn, 'qfs:label', label, state=1)
    return btn

def click(root, component):
    evnt = etree.SubElement(root, 'MouseEventStep')
    set_id(evnt)
    evnt.set('clicks', '1')
    evnt.set('client', 'client')
    evnt.set('component', component)
    evnt.set('event', 'MOUSE_MPRC')
    evnt.set('modifiers', '16')
    return evnt

#def add_menubar(root, classcount):

def __init_gui__():
    global winlist
    add_window(winlist, 'SNAP', 'SnapWindow')
    dialog = add_dialog(winlist, 'Plugin Installer', 'PluginDialog')
    add_button(dialog, "Finish")

def snap_window_el():
    pass

def get_win(win_id):
    global winlist
    path = winlist.xpath(f"//WindowStep[@id='{win_id}']")
    if path is None or len(path) == 0:
        raise NameError(f'Window named `{win_id}` not found!')
    if len(path) > 1:
        raise NameError(f'Multiple path ({len(path)}) found for window `{win_id}`!')
    return path[0]


def get_menubar(win):
    path = win.xpath(f"//ComponentStep[@class='MenuBar']")
    if len(path) == 1:
        return path[0]
    elif len(path) > 1:
        raise NameError("Multiple menus for same window!!")
    return add_menubar(win, 'main')

def get_menuitem(root, label, submenu=False):
    path = root.xpath(f"//ComponentStep[@feature='{label}']")
    if len(path) == 0:
        return add_menuitem(root, label, submenu=submenu)
    elif len(path) == 1:
        return path[0]
    raise NameError(f"Multiple items with label `{label}` found!")


def procedure_call(root, procedure, arguments, argname):
    el = etree.SubElement(root, "ProcedureCall")
    set_id(el)
    el.set("procedure", procedure)
    for val, name in zip(arguments, argname):
        #<variable name="prod_reader_type">envisat</variable>
        var = etree.SubElement(el, "variable")
        var.set("name", name)
        var.text = str(val)
    return root

def include(mod):
    if mod not in __included__:
        __include__(root, f"../lib/snap_{mod}.qft")
        __included__.append(mod)

def std_procedure(ns, fname, args):
    mod = f"{'.'.join(ns[1:])}." if len(ns[1:]) > 0 else ""
    fcall = f"{mod}{fname}"
    include(ns[0])
    procedure_call(current(), fcall, args, stdlib_fn_args(ns, fname))