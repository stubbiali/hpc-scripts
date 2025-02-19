#!/bin/bash

for host in daint hpc2020 levante lumi meluxina
do
  rm -rf "$PWD"/src/"$host"/common
  mkdir -p "$PWD"/src/"$host"/common
  touch "$PWD"/src/"$host"/common/__init__.py
  ln -s "$PWD"/src/common/utils.py "$PWD"/src/"$host"/common/
  ln -s "$PWD"/src/common/utils_module.py "$PWD"/src/"$host"/common/
  ln -s "$PWD"/src/common/utils_spack.py "$PWD"/src/"$host"/common/
done
