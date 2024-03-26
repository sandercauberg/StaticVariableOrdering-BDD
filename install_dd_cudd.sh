#!/usr/bin/env bash
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


set -v
set -e
pip install dd==0.6.0
    # to first install
    # dependencies of `dd`
pip uninstall -y dd
pip download \
    --no-deps dd \
    --no-binary dd
tar -xzf dd-*.tar.gz
pushd dd-*/
export DD_FETCH=1 DD_CUDD=1
pip install . \
    -vvv \
    --use-pep517 \
    --no-build-isolation
# confirm that `dd.cudd` did get installed
pushd tests/
python -c 'import dd.cudd'
popd
popd