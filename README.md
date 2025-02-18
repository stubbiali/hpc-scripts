# hpc-scripts: Utility scripts tailored to HPC systems

This repository collects Bash scripts to build, install and execute (at scale)
selected applications on a limited set of HPC systems. Each folder in the project root
directory contains the scripts for a specific machine, except for the folder
`common` gathering additional configuration files aimed to ameliorate
the user experience and productivity on modern supercomputers.

The following applications are targeted:
* [FVM](https://github.com/ckuehnlein/FVM_GT4Py)
* [CLOUDSC](https://github.com/ecmwf-ifs/dwarf-p-cloudsc)
* [CLOUDSC2](https://github.com/ecmwf-ifs/dwarf-p-cloudsc2-tl-ad)

The following supercomputers are supported (the corresponding top-level
directory is reported before the colon):
* `daint`: [Piz Daint](https://www.cscs.ch/computers/piz-daint/) @ CSCS (Lugano, Switzerland)
* `hpc2020`: [HPC2020](https://www.ecmwf.int/en/elibrary/81163-hpc2020-ecmwfs-new-high-performance-computing-facility)
@ ECMWF (Bologna, Italy)
* `meluxina`: [MeluXina](https://docs.lxp.lu/) @ LuxConnect (Bissen, Luxembourg)

**Disclaimer #1:** For any machine, the support is in principle *partial*, meaning
that we might providing the scripts only for a subset of targeted applications.

**Disclaimer #2:** The scripts are not guaranteed to work out-of-the-box. A few tweaks
and tunings are likely needed. However, most scripts are parametrized through Bash variables
(defined at the beginning of the file), so required changes should mainly be restricted to
these variables.


## Getting started

We suggest cloning the repository in the `$HOME` directory of the HPC system at hand.

We refer the reader to the instructions provided within each folder to get more information
about the (suggested) usage of the scripts.
