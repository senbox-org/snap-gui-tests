"""
Builds all the existing test that match the 
selected frequency tag.

@author: Martino Ferrari
@email: manda.mgf@gmail.com
"""
import argparse
import os
import json
import shutil
import sys
from lxml import etree


# Test Build target directory
__BUILD_DIR__ = "testBuild"
# Extra properties folder
__PROPERTIES_FOLDER__ = "shared"


def create_folders(tree, base="."):
    """
    Creates a path tree from a list of names.   
    e.g. ["test", "snap", "lib"] will generate 
    the following tree: test/snap/lib/

    Paramters
    ---------
    - tree: list of names defining the path tree
    - base: base folder path (default=".")
    """
    cd = base 
    for d in tree:
        cd = os.path.join(cd, d)
        if not os.path.isdir(cd):
            os.mkdir(cd)


def make_test(test, rootdir, testdir):
    """
    Builds a QFT test file from a JSON test definition.

    Parameters
    ----------
    - test: json object representing the test
    - rootdir: snap-gui-test project directory
    - testdir: build target directory

    Returns
    -------
    - str: the file path of the new generated test
    """
    id = test['id']
    testpath = test['testPath']
    # create the absolute path of the original test
    path = os.path.join(rootdir, testpath)
    # parse the original test
    tree = etree.parse(path)
    findTestCase = etree.XPath("//TestCase")
    # remove all testcase that are not the selected one
    for t in findTestCase(tree): 
        if t.get('name') != id:
            t.getparent().remove(t)
    # create the new filename for the test using its id and old file name
    id_path = testpath[:-4]+"_"+id.replace(r"[\s\ \t ]","_").replace(" ", "_")+".qft"
    # create the absolute path of the test relative to the target destination
    trg_path = os.path.join(testdir, id_path )
    # eventually create any needed subpath
    create_folders(os.path.split(id_path)[:-1], testdir)
    # save the test as new file
    with open(trg_path, 'wb') as f:
        f.write(etree.tostring(tree, pretty_print=True))
    return id_path



def eval_json(path, freq, rootdir, testdir):
    """
    Evaluates a test definition json file to build the tests that match the frequency tag selected.

    Parameters
    ----------
    - path: path of the target json file
    - freq: frequency tag
    - rootdir: project root path
    - testdir: test build target path

    Returns
    -------
    - list(str) : the list of the paths of the builded tests 
    """
    print(f"Tests: {os.path.split(path)[-1]} ")
    tst_list = []
    # load json file 
    with open(path, 'r') as f:
        tests = json.loads(f.read())
        # iterate all json objects inside the file
        for test in tests:
            # check if the frequency of the test match the selected tag
            if test['frequency'] == freq:
                # if is the case build the test
                print(f"\tEnabled: {test['id']}")
                tst_list.append(make_test(test, rootdir, os.path.join(rootdir, testdir, __BUILD_DIR__)))
            else:
                print(f"\tDisabled: {test['id']}")
    # return the list of builded tests
    return tst_list


def copy_and_overwrite(from_path, to_path):
    """
    Copies an entire path tree to a new destination (that will be overwritten).

    Parameters
    ----------
    - from_path: source path
    - to_path: target path 
    """
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)


def prepare_run(rootdir, basedir, testdir):
    """
    Prepares the enviroment for building the tests.
    In particular creates all the needed folders and 
    copy the needed files in the target directory.

    Parameters
    ----------
    - rootdir: is the snap-gui-test root relative path
    - basedir: is the qft tests project relative path (normally "snap/")
    - testdir: is the target path for the test building
    """
    # Initialize the different paths
    build_dir = os.path.join(rootdir, testdir, __BUILD_DIR__)
    snap_dir = os.path.join(build_dir, basedir)
    base_dir = os.path.join(rootdir, basedir)
    # Create the directory if is needed
    if not os.path.isdir(build_dir):   
        os.mkdir(build_dir)
    if not os.path.isdir(snap_dir):
        os.mkdir(snap_dir)
    # Copy the properties from the project to the target path
    src_properties_dir = os.path.join(rootdir, __PROPERTIES_FOLDER__)
    trg_properties_dir = os.path.join(build_dir, __PROPERTIES_FOLDER__)
    copy_and_overwrite(src_properties_dir, trg_properties_dir)
    # Copy the QFT tests from the project to the target path
    copy_and_overwrite(base_dir, snap_dir)


if __name__ == "__main__":
    # prepare arg parsers
    parser = argparse.ArgumentParser()
    parser.add_argument("testlist", help="File containing list of tests")
    parser.add_argument("--basedir", help="SNAP GUI TEST base dir", default="snap")
    parser.add_argument("--rootdir", help="Root dir", default=".")
    parser.add_argument("--testdir", help="Test base dir", default="gui-tests-resources")
    parser.add_argument("-f", "--frequency", help="Frequency tag", default="daily")
    # parse arguments and extract useful informations
    args = parser.parse_args()
    rootdir = args.rootdir
    testdir = args.testdir
    basedir = args.basedir
    frequency = args.frequency

    # prepare the project for the build
    prepare_run(rootdir, basedir, testdir)
    
    # open the test list file
    with open(args.testlist, 'r') as f:
        lst = []
        # iterate all lines of the list file
        for line in f.readlines():
            # prepare string 
            line = line.replace(r'\s','').replace('\n','')
            if len(line) == 0 or line.startswith('#'):
                # if is an empty line or a comment skip it
                continue
            else:
                # otherwise evaluate and build the tests from the json file
                lst += eval_json(os.path.join(rootdir, testdir, line), frequency, rootdir, testdir)
        # create the list of tests generate during this build
        list_dir = os.path.join(rootdir, testdir, __BUILD_DIR__, "qftests.lst")
        with open(list_dir, 'w') as lf:
            for test in lst:
                lf.write(test+"\n")
