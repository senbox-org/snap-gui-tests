"""
Module that manages the QF-Test file generation (xml) as 
well as the project standard library (files defined in snap/lib) 

@author: Martino Ferrari
@email: manda.mgf@gmail.com
"""
import sys
from lxml import etree
import os


"""
Global variables representing the main elements of a QFT file.
"""
__root__ = None # qft root element
__testset__ = None # qft testset element
__package__ = None # qft packageroot element
__extra__ = None # qft extra element
__winlist__ = None # qft windowlist element

"""
Helpers variable storing current state
"""
__current_node__ = None # current xml element
__id__ = 0 # counter used to generated uniques ids

"""
variable to store the 
"""
__stdlib__ = {} # dictionary containing all std functions and packages
__qfslib__ = {} # dictionary containing all qfs functions and packages
__included__ = [] # list of the library to be included in the generated test

"""
STANDARD LIBRARIES PATH
=======================
The `__STDLIB_PATH__` represent the path to the folder containing all the pre-defined functionality
of SNAP-GUI-Test project, normally stored in `snap/lib/`. 
The path is setted by default as `../snap/lib/` but it can be changed by setting an enviromental
variable named `SNAPLIB`.

The `__QFSLIB_PATH__` represent the path to the standard qf test library find inside the qf-test distribution.
It's defined by the enviromental variable `QFSLIB`.
"""
__STDLIB_PATH__ = os.getenv('SNAPLIB') if os.getenv("SNAPLIB") is not None else "../snap/lib/" 
__QFSLIB_PATH__ = os.getenv('QFSLIB') if os.getenv("QFSLIB") is not None else "/opt/qftest/qftest-4.7.0/include/qfs.qft"

def __load_func__(el):
    """
    load an qft function and takes in account its variables.
    """
    findVars = etree.XPath("./variable")
    res = []
    for v in findVars(el):
        res.append(v.get("name"))
    return res


def __load_package__(pkgxml):
    """
    loads all functions inside of a package and explore
    recursively all sub-packages.
    """
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
    """
    loads all procedure of the libraries located in the path
    `__STDLIB_PATH__` and stores it in the `__stdlib__` dictionary.
    
    This function is automatically called at the initialization of the
    root (`init_root()` function). 
    """
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


def __load_qfslib__():
    """
    loads all procedure of the libraries located in the path
    `__QFSLIB_PATH__` and stores it in the `__qfslib__` dictionary.
    
    This function is automatically called at the initialization of the
    root (`init_root()` function). 
    """
    findPRoot = etree.XPath("//PackageRoot")
    tree = etree.parse(__QFSLIB_PATH__)
    pproot = findPRoot(tree)
    if len(proot) > 0:
        __qfslib__ = __load_package__(proot[0])


def __search_args__(ns, fname, packagedict, basename):
    p = packagedict
    path = basename
    for n in ns:
        if n not in p:
            raise NameError(f"Package `{n}` not found in `{path}`")
        p = p[n]
        path += ":"+n
    if fname not in p:
        raise NameError(f"Function `{fname}` not found in package `{path}`")
    return p[fname]

def stdlib_fn_args(ns, fname):
    """
    retrives the list of arguments (and their names) of a specific
    function of the std library.

    Parameters
    ----------
    - ns  (list[str]) : name space, first element is the lib name then the package structure
    - fname (str) : name of the function

    Returns
    -------
    `list[str]` representing the arguments names.

    Raises
    ------
    `NameError` if the namespace or the function name is not resolvable.
    """
    return __search_args__(ns, fname, __stdlib__, "std")

def qfslib_fn_args(ns, fname):
    """
    retrives the list of arguments (and their names) of a specific
    function of the qfs library.

    Parameters
    ----------
    - ns  (list[str]) : name space, first element is the lib name then the package structure
    - fname (str) : name of the function

    Returns
    -------
    `list[str]` representing the arguments names.

    Raises
    ------
    `NameError` if the namespace or the function name is not resolvable.
    """
    return __search_args__(ns, fname, __qfslib__, "qfs")

def print_xml():
    """
    prints the xml tree of the generated QFT test.
    """
    global __root__
    header = '<?xml version="1.0" encoding="ISO-8859-1"?>\n<!DOCTYPE RootStep>\n'
    xml = etree.tostring(__root__, pretty_print=True)
    sys.stdout.buffer.write(bytes(header, encoding='utf-8')+xml)


def set_id(el):
    """
    adds an unique id to an xml element as 
    attribute "`id`". It also auto-increments the
    `__id__` variable.

    Parameters
    ----------
    - el: xml element
    """
    global __id__
    el.set("id", f'_{__id__}')
    __id__ += 1

def set_uid(el):
    """
    adds an unique id to an xml element as 
    attribute "`uid`". It also auto-increments the
    `__id__` variable.

    This is due to the fact that some QFT element have the 
    `id` attribute used for other reasons (e.g. gui elements).

    Parameters
    ----------
    - el: xml element
    """
    global __id__
    el.set("uid", f'_{id}')
    __id__ += 1

def __include__(lib):
    """
    includes an external qft file to the current test file.
    
    Parameters
    ----------
    - lib: path to the qft file
    """
    global __root__
    include = etree.SubElement(__root__, "include")
    include.text = lib

def init_root():
    """
    initializes all elements needed for the generation of 
    the qft test.
    
    In particular create the basics structure of the xml tree:
    - RootStep
        - TestSet
        - PackageRoot
        - ExtraSequence
        - WindowList
    
    It also load the standard library.
    """
    __load_stdlib__()

    global __root__
    global __testset__
    global __package__
    global __extra__ 
    global __winlist__
    __root__ = etree.Element("RootStep")
    set_id(__root__)
    __root__.set("name", "root")
    __root__.set("version", "4.7.0")
    
    __include__("qfs.qft")

    __testset__ = etree.SubElement(__root__, "TestSet")
    set_id(__testset__)
    __testset__.set("name", "TestSet")
    __package__ = etree.SubElement(__root__, "PackageRoot")
    set_id(__package__)
    __extra__ = etree.SubElement(__root__, "ExtraSequence")
    set_id(__extra__)
    __winlist__ = etree.SubElement(__root__, "WindowList")
    set_id(__winlist__)
    # __init_gui__()
    global __current_node__ 
    __current_node__ = __root__


def current():
    """retrives the current xml elements"""
    global __current_node__
    return __current_node__


def set_current(el):
    """sets current xml element."""
    global __current_node__
    __current_node__ = el


def set_var(name, value):
    """
    Define a test
    """
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


"""
Basic Built-in Nodes
====================
- SUTClientStarter
- IfSequence

GUI Elements
------------
- extrafeture

"""

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

def else_seq(name):
    el = etree.SubElement(current(), "ElseSequence")
    set_id(el)
    el.set('name', name)
    set_current(el)
    return el


def wait_for_component(root, component, timeout=1000):
    el = etree.SubElement(root, "ComponentWaiter")
    el.set("client", "$(client)")
    el.set("component",component)
    el.set("timeout", str(timeout))
    set_id(el)
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
    # add_extrafeature(win, 'qfs:label', label)
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
    evnt.set('client', '$(client)')
    evnt.set('component', component)
    evnt.set('event', 'MOUSE_MPRC')
    evnt.set('modifiers', '16')
    return evnt

#def add_menubar(root, classcount):

"""
Obsolete
def __init_gui__():
    global __winlist__
    add_window(__winlist__, 'SNAP', 'SnapWindow')
    dialog = add_dialog(__winlist__, 'Plugin Installer', 'PluginDialog')
    add_button(dialog, "Finish")
"""

def get_win(win_id):
    global __winlist__
    path = __winlist__.xpath(f"//WindowStep[@id='{win_id}']")
    if path is None or len(path) == 0:
        return add_window(__winlist__, win_id, win_id)
        # raise NameError(f'Window named `{win_id}` not found!')
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
        __include__(f"../lib/snap_{mod}.qft")
        __included__.append(mod)

def std_procedure(ns, fname, args):
    mod = f"{'.'.join(ns[1:])}." if len(ns[1:]) > 0 else ""
    fcall = f"{mod}{fname}"
    include(ns[0])
    procedure_call(current(), fcall, args, stdlib_fn_args(ns, fname))


def qfs_procedure(ns, fname, args):
    mod = f"{'.'.join(ns)}." if len(ns) > 0 else ""
    fcall = f"{mod}{fname}"
    procedure_call(current(), fcall, args, qfslib_fn_args(ns, fname))

def std_var(ns, varname):
    include(ns[0])
    mod = f"{'.'.join(ns[1:])}." if len(ns[1:]) > 0 else ""
    return mod+varname


def check_boolean(comp, check='default', var=None):
    el = etree.SubElement(current(), "CheckBooleanStep")
    set_id(el)
    el.set('client', '$(client)')
    el.set('component', comp)
    el.set('checktype', check)
    if var is not None:
        el.set('resvarname', var)
