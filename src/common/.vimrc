" disable compatibility with vi which can cause unexpected issues
set nocompatible

" enable type file detection. Vim will be able to try to detect the type of file in use
filetype on

" enable plugins and load plugin for the detected file type
filetype plugin on

" load an indent file for the detected file type
filetype indent on

" turn syntax highlighting on
syntax on

" add numbers to each line on the left-hand side
set number

" highlight cursor line underneath the cursor horizontally
" set cursorline

" highlight cursor line underneath the cursor vertically
" set cursorcolumn

" set shift width to 4 spaces
set shiftwidth=4

" set tab width to 4 columns
set tabstop=4

" use space characters instead of tabs
set expandtab

" do not save backup files
set nobackup

" do not let cursor scroll below or above N number of lines when scrolling
set scrolloff=10

" do not wrap lines - allow long lines to extend as far as the line goes
set nowrap

" while searching though a file incrementally highlight matching characters as you type
set incsearch

" ignore capital letters during search
set ignorecase

" override the ignorecase option if searching for capital letters
" this will allow you to search specifically for capital letters
set smartcase

" show partial command you type in the last line of the screen
set showcmd

" show the mode you are on the last line
set showmode

" show matching words during a search
set showmatch

" use highlighting when doing a search
set hlsearch

" set the commands to save in history default number is 20
set history=1000

" enable auto completion menu after pressing TAB
set wildmenu

" make wildmenu behave like similar to Bash completion
set wildmode=list:longest

" there are certain files that we would never want to edit with Vim
" wildmenu will ignore files with these extensions
set wildignore=*.docx,*.jpg,*.png,*.gif,*.pdf,*.pyc,*.exe,*.flv,*.img,*.xlsx
