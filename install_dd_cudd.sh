#!/bin/bash
#
# Install `dd`, including the modules
# `dd.cudd` and `dd.cudd_zdd`
# (which are written in Cython).
#
# To run this script, enter in
# a command-line environment:
#
# ./install_dd_cudd.sh
#

set -e
set -v

pip download dd --no-deps
tar -xzf dd-*.tar.gz
cd dd-*/
python setup.py install --fetch --cudd
# confirm that `dd.cudd` did get installed
#python -c 'import dd.cudd'
cd ..
