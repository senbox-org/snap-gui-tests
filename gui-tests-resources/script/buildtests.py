"""
Simply extracts the list of json files in

@author: Martino Ferrari
@email: manda.mgf@gmail.com
"""
import argparse
import os
import json
import shutil
import sys
from lxml import etree


__BUILD_DIR__ = "testBuild"
__PROPERTIES_FOLDER__ = "shared"
__LIB_FOLDER__ = "lib"


def create_folders(base, tree):
    cd = base 
    for d in tree:
        cd = os.path.join(cd, d)
        if not os.path.isdir(cd):
            os.mkdir(cd)



def make_test(test, rootdir, testdir):
    id = test['id']
    testpath = test['testPath']
    path = os.path.join(rootdir, testpath)
    tree = etree.parse(path)
    findTestCase = etree.XPath("//TestCase")
    for t in findTestCase(tree): 
        if t.get('name') != id:
            t.getparent().remove(t)
    
    id_path = testpath[:-4]+"_"+id.replace(r"[\s\ \t ]","_").replace(" ", "_")+".qft"
    trg_path = os.path.join(testdir, id_path )
    create_folders(testdir , os.path.split(id_path)[:-1])
    with open(trg_path, 'wb') as f:
        f.write(etree.tostring(tree, pretty_print=True))
    return id_path



def __eval_tests__(path, freq, rootdir, testdir):
   
    print(f"Tests: {os.path.split(path)[-1]} ")
    tst_list = []
    with open(path, 'r') as f:
        tests = json.loads(f.read())
        for test in tests:
            if test['frequency'] == freq:
                print(f"\tEnabled: {test['id']}")
                tst_list.append(make_test(test, rootdir, os.path.join(rootdir, testdir, __BUILD_DIR__)))
            else:
                print(f"\tDisabled: {test['id']}")
    return tst_list


def copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)


def prepare_run(rootdir, basedir, testdir):
    build_dir = os.path.join(rootdir, testdir, __BUILD_DIR__)
    snap_dir = os.path.join(build_dir, basedir)
    base_dir = os.path.join(rootdir, basedir)
    if not os.path.isdir(build_dir):   
        os.mkdir(build_dir)
    if not os.path.isdir(snap_dir):
        os.mkdir(snap_dir)
    src_properties_dir = os.path.join(rootdir, __PROPERTIES_FOLDER__)
    trg_properties_dir = os.path.join(build_dir, __PROPERTIES_FOLDER__)
    copy_and_overwrite(src_properties_dir, trg_properties_dir)
    src_lib_dir = os.path.join(base_dir, __LIB_FOLDER__)
    trg_lib_dir = os.path.join(snap_dir, __LIB_FOLDER__)
    copy_and_overwrite(src_lib_dir, trg_lib_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("testlist", help="File containing list of tests")
    parser.add_argument("--basedir", help="SNAP GUI TEST base dir", default="snap")
    parser.add_argument("--rootdir", help="Root dir", default=".")
    parser.add_argument("--testdir", help="Test base dir", default="gui-tests-resources")
    parser.add_argument("-f", "--frequency", help="Frequency tag", default="daily")

    args = parser.parse_args()
    rootdir = args.rootdir
    testdir = args.testdir
    basedir = args.basedir
    frequency = args.frequency

    prepare_run(rootdir, basedir, testdir)
    
    with open(args.testlist, 'r') as f:
        lst = []
        for line in f.readlines():
            line = line.replace(r'\s','').replace('\n','')
            if len(line) == 0:
                continue
            if not line.startswith('#'):
                lst += __eval_tests__(os.path.join(rootdir, testdir, line), frequency, rootdir, testdir)
            else:
                # is a comment
                continue
        list_dir = os.path.join(rootdir, testdir, __BUILD_DIR__, "qftests.lst")
        with open(list_dir, 'w') as lf:
            for test in lst:
                lf.write(test+"\n")
