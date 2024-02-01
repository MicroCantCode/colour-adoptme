#!/bin/bash

echo "Running python coverage"
script_name=${BASH_SOURCE[0]}
script_dir=$(dirname $(readlink -f ${script_name}))

pushd ${script_dir}/../

PYTHONPATH=$PYTHONPATH:${PYTHONPATH}/tests coverage run -m unittest discover -v
coverage html

