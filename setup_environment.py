#!/usr/bin/python3
from argparse import ArgumentParser
from subprocess import run
from collections import namedtuple
from os import environ, path, remove
from sys import argv


def struct(name, items):
    struct_class = namedtuple(name, [item[0] for item in items])
    struct_object = struct_class(*[item[1] for item in items])
    return struct_object


with open('/etc/os-release') as os_release_file:
    OS_RELEASE = os_release_file.read()


EDIT = '"emacsclient -c -s emacsserver"'
BASHRC_PATH = path.join(environ['HOME'], '.bashrc')
BASH_PROFILE_PATH = path.join(environ['HOME'], '.bash_profile')
BASE_PACKAGES = ('python3',
                 'python3-pip',
                 'emacs' if environ.get('DESKTOP_SESSION') or '--force-x' in argv else 'emacs-nox')

FEDORA_PACKAGE = BASE_PACKAGES
UBUNTU_PACKAGES = BASE_PACKAGES + ('python3-venv',)
PIP_PACKAGES = 'rope', 'autopep8', 'yapf', 'black', 'flake8', 'ipython'

COMMANDS = struct('Commands', (('create_venv', 'python3 -m venv ~/.default-venv'),
                               ('remove_emacsfile', 'rm ~/.emacs'),
                               ('copy_emacsfile', 'cp /tmp/.emacs ~/.emacs'),
                               ('install_elpy', 'emacs --script /tmp/install_elpy.lisp')))
if 'Ubuntu' in OS_RELEASE:
    SUDO_COMMANDS = struct('SudoCommands', (('apt_install', 'apt -y install ' + ' '.join(UBUNTU_PACKAGES)),))

elif 'Fedora' in OS_RELEASE:
    SUDO_COMMANDS = struct('SudoCommands', (('dnf_install', 'dnf -y install ' + ' '.join(FEDORA_PACKAGES)),))

else:
    SUDO_COMMANDS = tuple()

GIT_CONFIG = {'user.name': 'Jerrad Genson',
              'user.email': 'jerradgenson@gmail.com',
              'core.editor': EDIT}

BASH_PROFILE = struct('BashProfile', (('emacs_server', ('emacs --bg-daemon="emacsserver" > /dev/null 2>&1')),))
BASHRC = struct('BashRC', (('emacs_client', 'alias edit={}'.format(EDIT)),
                           ('visual_editor', 'export VISUAL=edit'),
                           ('editor', 'export EDITOR=edit')))

DEFAULT_BASH_PROFILE =\
    """
    # ~/.bash_profile: executed by bash for login shells.

    if [ -e /etc/bash.bashrc ] ; then
    source /etc/bash.bashrc
    fi

    if [ -e ~/.bashrc ] ; then
    source ~/.bashrc
    fi

    """

INSTALL_ELPY =\
    """
    (package-initialize)
    (require 'package)
    (add-to-list 'package-archives '("melpa-stable" . "https://stable.melpa.org/packages/"))
    (package-refresh-contents)
    (package-install 'elpy)

    """

EMACSFILE =\
    """
    ;; Added by Package.el.  This must come before configurations of
    ;; installed packages.  Don't delete this line.  If you don't want it,
    ;; just comment it out by adding a semicolon to the start of the line.
    ;; You may delete these explanatory comments.
    (package-initialize)

    (setq inhibit-splash-screen t)
    (custom-set-variables
     ;; custom-set-variables was added by Custom.
     ;; If you edit it by hand, you could mess it up, so be careful.
     ;; Your init file should contain only one such instance.
     ;; If there is more than one, they won't work right.
     '(column-number-mode t)
     '(font-use-system-font t)
     '(global-display-line-numbers-mode t)
     '(package-selected-packages (quote (elpy)))
     '(show-paren-mode t))
    (custom-set-faces
     ;; custom-set-faces was added by Custom.
     ;; If you edit it by hand, you could mess it up, so be careful.
     ;; Your init file should contain only one such instance.
     ;; If there is more than one, they won't work right.
     )

    (require 'package)

    ;; Add Elpy repo to source packages
    (add-to-list 'package-archives
                 '("melpa-stable" . "https://stable.melpa.org/packages/"))

    ;; Start and configure Elpy
    (package-initialize)
    (elpy-enable)
    (setq elpy-rpc-python-command "python")
    (setenv "IPY_TEST_SIMPLE_PROMPT" "1")
    (setq python-shell-interpreter "ipython"
          python-shell-interpreter-args "-i")

    (pyvenv-activate "~/.default-venv")
    (add-hook 'elpy-mode-hook (lambda () (highlight-indentation-mode -1)))

    ;; Remove trailing whitespace upon save
    (setq-default indicate-empty-lines t)
    (add-hook 'before-save-hook 'delete-trailing-whitespace)

    ;; Configure Semantic
    (setq semantic-default-submodes
          '(;; Perform semantic actions during idle time
            global-semantic-idle-scheduler-mode
            ;; Use a database of parsed tags
            global-semanticdb-minor-mode
            ;; Highlight the name of the function you're currently in
            global-semantic-highlight-func-mode
            ;; show the name of the function at the top in a sticky
            global-semantic-stickyfunc-mode
            ;; Generate a summary of the current tag when idle
            global-semantic-idle-summary-mode
            ;; Show a breadcrumb of location during idle time
            global-semantic-idle-breadcrumbs-mode
            ;; Switch to recently changed tags with `semantic-mrub-switch-tags',
            ;; or `C-x B'
            global-semantic-mru-bookmark-mode))

    ;; Add Semantic hooks to each language mode we want to use it with
    (add-hook 'emacs-lisp-mode-hook 'semantic-mode)
    (add-hook 'python-mode-hook 'semantic-mode)
    (add-hook 'java-mode-hook 'semantic-mode)
    (add-hook 'c-mode-hook 'semantic-mode)
    (add-hook 'scheme-mode-hook 'semantic-mode)

    """

FILES = [('install_elpy.lisp', INSTALL_ELPY),
         ('.emacs', EMACSFILE)]

FILES = [(path.join('/tmp', file[0]), file[1]) for file in FILES]


def main():
    clargs = parse_command_line()
    for file in FILES:
        with open(file[0], 'w') as file_out:
            file_out.write(file[1])

    if clargs.install_elpy:
        shell(COMMANDS.install_elpy)
        return

    if not clargs.no_sudo:
        for command in SUDO_COMMANDS:
            shell('sudo ' + command)

    for command in COMMANDS:
        if not (clargs.no_venv and command == COMMANDS.create_venv):
            shell(command)

    if not clargs.no_venv:
        for pip_package in PIP_PACKAGES:
            shell('~/.default-venv/bin/pip --no-cache-dir install ' + pip_package)

    for option, value in GIT_CONFIG.items():
        shell('git config --global {} {}'.format(option, value))

    bashrc = BASHRC
    for line in BASH_PROFILE:
        try:
            with open(BASH_PROFILE_PATH) as bash_profile:
                bash_profile_text = bash_profile.read()

        except FileNotFoundError:
            with open(BASH_PROFILE_PATH, 'w') as bash_profile:
                bash_profile.write(DEFAULT_BASH_PROFILE)

            bash_profile_text = DEFAULT_BASH_PROFILE

        with open(BASH_PROFILE_PATH, 'a') as bash_profile:
            if line not in bash_profile_text:
                print('Writing line to {}: {}'.format(BASH_PROFILE_PATH, line))
                bash_profile.write(line + '\n')

    for line in BASHRC:
        try:
            with open(BASHRC_PATH) as bashrc:
                bashrc_text = bashrc.read()

        except FileNotFoundError:
            bashrc_text = ''

        with open(BASHRC_PATH, 'a') as bashrc:
            if line not in bashrc_text:
                print('Writing line to {}: {}'.format(BASHRC_PATH, line))
                bashrc.write(line + '\n')


def cleanup():
    for file in FILES:
        remove(file[0])


def shell(command):
    print(command)
    run(command, shell=True)


def parse_command_line():
    parser = ArgumentParser()
    parser.add_argument('-s', '--no-sudo', action='store_true')
    parser.add_argument('-f', '--force-x', action='store_true')
    parser.add_argument('-e', '--install-elpy', action='store_true')
    parser.add_argument('-v', '--no-venv', action='store_true')
    clargs = parser.parse_args()
    if clargs.no_sudo:
        print('Configuring environment without running sudo commands.')

    if clargs.force_x:
        print('Installing Emacs with X support, even in a headless environment.')

    if clargs.install_elpy:
        print('Installing Elpy only and then exiting.')

    if clargs.no_venv:
        print('Not creating a new Python virtual environment.')

    return clargs


if __name__ == '__main__':
    main()
    cleanup()
