# hpc-scripts-common

The namespace package `hpc-scripts-common` contains host-agnostic functionalities and utilities
used by other packages, and some template dotfiles, to be symlinked in your `$HOME` folder.

### Quick start guide

```bash
# clone the repository into home
~$ git clone -b namespaces git@github.com:stubbiali/hpc-scripts.git
```

### Example

```bash
# create a symlink to dotfiles/.vimrc in home
# if .vimrc already exists in home, we suggest creating a backup copy for enhanced safety
~$ mv .vimrc .vimrc.bck
~$ ln -s hpc-scrips/hpc-scripts-common/dotfiles/.vimrc
```
