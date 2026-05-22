# hpc-scripts: Script generator for HPC systems

`hpc-scrips` aims to ease the configuration, build and deployment of selected applications on a
limited set of HPC systems. `hpc-scripts` comes as a Python distribution consisting of multiple *namespace
packages*, each targeting a specific machine, except for `hpc-scripts-common` that gathers common
functionalities consumed by other packages. Packages expose *console scripts* (i.e., executable commands)
that synthesize Bash scripts to configure, build and deploy software. Some console scripts might
issue commands themselves, like `salloc` and `sbatch`.

The following packages are available:

* `hpc-scripts_common` collects utilities and functionalities used by other packages;
* `hpc-scripts-lumi` targets the LUMI supercomputer at CSC;
* `hpc-scripts-santis` targets the Santis vCluster of the Alps compute infrastructure at CSCS.

Since different packages might expose executable commands with the same name, we recommend to only
install on the remote host the package targeting that machine, so to avoid any name collision.

A quick-start guide is provided for each package, with installation instructions, the list of
supported applications, and the available console scripts.

Note that the `hpc-scripts` distribution is *self-contained*: each package only depends on the Python
standard library and (optionally) `hpc-scripts-common`. Therefore, it is safe to pip-install packages
outside a virtual environment, so to have the provided console scripts always available in the path.
Nevertheless, we may recommend using [uv tool](https://docs.astral.sh/uv/concepts/tools/) for enhanced
security.

The distribution is parametrized via the following environment variables:

* `HPCS_APPS_ROOT_DIR` sets the root directory to search for application codes, or where
application codes will be cloned if not found. For any application `{app}`, the source code of the branch `{branch}` will be cloned under `$HPCS_APPS_ROOT_DIR/{app}/{branch}`.
* `HPCS_SCRIPTS_ROOT_DIR` sets the root directory where the scripts produced by the distribution are to be stored.

If unset, the environment variables above default to any of the following directory (the first in the
list to exist):

1. `$HPCS_ROOT_DIR`
2. `$PROJECT`
3. `$SCRATCH`
4. `$HOME`
5. `/tmp`
