"""
Simply extracts the list of json files in

@author: Martino Ferrari
@email: manda.mgf@gmail.com
"""
import argparse
import os
import json
import shutil


__BUILD_DIR__ = "testBuild"
__PROPERTIES_FOLDER__ = "shared"
__LIB_FOLDER__ = "lib"


def clean_run(rootdir, basedir, testdir):
    build_dir = os.path.join(rootdir, testdir, __BUILD_DIR__)
    snap_dir = os.path.join(build_dir, basedir)
    properties_dir = os.path.join(build_dir, __PROPERTIES_FOLDER__)
    shutil.rmtree(snap_dir)
    shutil.rmtree(properties_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--basedir", help="SNAP GUI TEST base dir", default="snap")
    parser.add_argument("--rootdir", help="Root dir", default=".")
    parser.add_argument("--testdir", help="Test base dir", default="gui-tests-resources")

    args = parser.parse_args()
    rootdir = args.rootdir
    testdir = args.testdir
    basedir = args.basedir

    clean_run(rootdir, basedir, testdir)