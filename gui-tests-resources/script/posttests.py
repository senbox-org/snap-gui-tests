"""
Clean the test directory after the tests are ended.

@author: Martino Ferrari
@email: manda.mgf@gmail.com
"""
import argparse
import os
import json
import shutil


__BUILD_DIR__ = "testBuild"
__PROPERTIES_FOLDER__ = "shared"


if __name__ == "__main__":
    # arg parser configuration
    parser = argparse.ArgumentParser()
    parser.add_argument("--basedir", help="SNAP GUI TEST base dir", default="snap")
    parser.add_argument("--rootdir", help="Root dir", default=".")
    parser.add_argument("--testdir", help="Test base dir", default="gui-tests-resources")

    # parse arguments
    args = parser.parse_args()
    rootdir = args.rootdir # project root path
    testdir = args.testdir # test root path
    basedir = args.basedir # snap qft test relative path 

    build_dir = os.path.join(rootdir, testdir, __BUILD_DIR__) # build path
    snap_dir = os.path.join(build_dir, basedir) # copy of the snap tests in the build path 
    properties_dir = os.path.join(build_dir, __PROPERTIES_FOLDER__) # copy of the properties in the build path 
    shutil.rmtree(snap_dir) # remove snap test copy
    shutil.rmtree(properties_dir) # remove properties copy
