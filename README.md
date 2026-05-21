# hpc-scripts: Utility scripts tailored to HPC systems

`hpc-scrips` aims to ease the configuration, build and deployment of selected applications on a
limited set of HPC systems. `hpc-scripts` comes as a Python distribution consisting of multiple *namespace
packages*, each targeting a specific machine, except for `hpc-scripts-common` that gathers common
functionalities consumed by other packages. Packages expose *console scripts* (i.e., executable commands)
that generate the Bash scripts to configure, build and deploy software.

The following packages are available:

* `hpc-scripts-lumi` targets the LUMI supercomputer at CSC.

Since different packages might expose executable commands with the same name, we recommend to only
install on the remote host the package targeting that machine, so to avoid any name collision.
A quick-start guide is provided for each package, with installation instructions, the list of
supported applications, and the available console scripts. Note that the `hpc-scripts` distribution
is *self-contained*: each package only depends on the Python standard library and (optionally)
`hpc-scripts-common`. Therefore, it is safe to pip-install packages outside
a virtual environment, so to have the provided console scripts always available in the path.
