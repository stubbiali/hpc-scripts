# hpc-scripts-lumi

The namespace package `hpc-scripts-lumi` is meant to ease the configuration, build and run of
selected software on the LUMI supercomputer. Some template dotfiles are also provided in `dotfiles/`.

### Quick start guide

```bash
# clone the repository into your home
~$ git clone -b namespaces git@github.com:stubbiali/hpc-scripts.git

# install the package in editable mode
~$ module load cray-python
~$ pip install -e hpc-scripts/hpc-scripts-lumi

# set the directory containing the source code of the target software
# all generated bash scripts will be placed in this directory
# we suggest placing this instruction in your bashrc file
~$ export HPC_SCRIPTS_ROOT_DIR=$PROJECT
```

### Supported software

* [HDF5](https://github.com/HDFGroup/hdf5)
* [NetCDF-C](https://github.com/Unidata/netcdf-c)
* [NCO](https://github.com/nco/nco)
* [dwarf-p-cloudsc](https://github.com/ecmwf-ifs/dwarf-p-cloudsc)
* [dwarf-p-cloudsc2-tl-ad](https://github.com/ecmwf-ifs/dwarf-p-cloudsc2-tl-ad)
* [PMAP](https://github.com/PMAP-Project/PMAP)
* [PMAP-LES-shared](https://github.com/PMAP-Project/PMAP-LES-shared)
* [ecRad](https://github.com/ecmwf-ifs/ecrad)
* [ecRad-versions](https://github.com/PMAP-Project/ecRad-versions)

### Console scripts

The following executable commands are installed as part of this package:

* `make_build_hdf5`
* `make_build_nco`
* `make_build_netcdf`
* `make_prepare_cloudsc`
* `make_prepare_cloudsc2`
* `make_prepare_ecrad`
* `make_prepare_ecrad_porting`
* `make_prepare_mpi`
* `make_prepare_pmap`
* `make_select_gpu`
* `pysalloc`
* `sbatch_ecrad_porting` (*)
* `sbatch_pmap` (*)

**Remark**: commands marked with an asterisk  do not accept command-line arguments. In order to alter the default parameters, the user should modify the corresponding Python module in `src/hpc-scripts/lumi`. The customizable section is enclosed within `# >>>: config: start` and `# >>> config: end`.

### Example

Installing PMAP-LES-shared using the software stack LUMI/25.03, and run a benchmark on one GPU.

```bash
# build hdf5 with parallel support
# by default, the latest public release of hdf5 is used
~$ make_build_hdf5
~$ . $HPC_SCRIPTS_ROOT_DIR/build_hdf5.sh

# build netcdf-c with parallel support
# by default, the latest public releases of hdf5 and netcdf-c are used
~$ make_build_netcdf
~$ . $HPC_SCRIPTS_ROOT_DIR/build_netcdf.sh

# build and install pmap in a dedicated virtual environment, jump into the project directory and
#  activate the environment
# the pmap code is searched under $HPC_SCRIPTS_ROOT_DIR/pmap-les-shared/{branch}
# if the code is not found, the repo will be cloned
~$ make_prepare_pmap --project=pmap-les-shared --branch=lumi
~$ . $HPC_SCRIPTS_ROOT_DIR/prepare_pmap_les_shared.sh

# allocate one GPU node on the dev-g partition for an hour
(...) <HPC_SCRIPTS_ROOT_DIR>/pmap-les-shared/lumi$ pysalloc --partition=dev-g --time=01:00:00

# refresh the bash script, so that the already-existing virtual environment is only be activated
<HPC_SCRIPTS_ROOT_DIR>/pmap-les-shared/lumi$ make_prepare_pmap --project=pmap-les-shared --branch=lumi
<HPC_SCRIPTS_ROOT_DIR>/pmap-les-shared/lumi$ . $HPC_SCRIPTS_ROOT_DIR/prepare_pmap_les_shared.sh

# generate the script select_gpu.sh (see https://docs.lumi-supercomputer.eu/runjobs/scheduled-jobs/distribution-binding/#gpu-binding)
(...) <HPC_SCRIPTS_ROOT_DIR>/pmap-les-shared/lumi$ make_select_gpu

# run the moist baroclinic wave benchmark
(...) <HPC_SCRIPTS_ROOT_DIR>/pmap-les-shared/lumi$ GT_BACKEND=dace:gpu srun --ntasks=1 --cpus-per-task=7 ./../../select_gpu.sh pmap config/baroclinic_wave_sphere_moist.yml
```
