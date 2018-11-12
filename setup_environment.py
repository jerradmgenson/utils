#!/usr/bin/python3
from argparse import ArgumentParser
from subprocess import run
from collections import namedtuple
from os import environ, path
from sys import argv

from structures.struct import struct

BASHRC_PATH = path.join(environ['HOME'], '.bashrc')
BASH_PROFILE_PATH = path.join(environ['HOME'], '.bash_profile')
PACKAGES = struct('Packages', (('python', 'python3'),
                               ('pip', 'python3-pip'),
                               ('emacs', 'emacs' if environ.get('DESKTOP_SESSION') or '--force-x' in argv else 'emacs-nox')))

PIP_PACKAGES = 'rope', 'autopep8', 'yapf', 'black', 'flake8', 'ipython'

COMMANDS = struct('Commands', (('create_venv', 'python3 -m venv ~/.default-venv'),
                               ('get_elpy_script', 'wget -O "install_elpy.lisp" "https://raw.githubusercontent.com/jerradmgenson/utils/environment/install_elpy.lisp"'),
                               ('remove_emacsfile', 'rm ~/.emacs'),
                               ('install_elpy', 'emacs --script install_elpy.lisp'),
                               ('remove_elpy_script', 'rm install_elpy.lisp'),
                               ('get_emacsfile', 'wget -O "{}/.emacs" "https://raw.githubusercontent.com/jerradmgenson/utils/environment/.emacs"'.format(environ['HOME']))))

SUDO_COMMANDS = struct('SudoCommands', (('dnf_install', 'dnf -y install ' + ' '.join(PACKAGES)),))
GIT_CONFIG = {'user.name': 'Jerrad Genson',
              'user.email': 'jerradgenson@gmail.com',
              'core.editor': 'emacs'}

BASH_PROFILE = struct('BashProfile', (('emacs_server', ('emacs --bg-daemon="emacsserver" > /dev/null 2>&1')),))
BASHRC = struct('BashRC', (('emacs_client', 'alias edit="emacsclient -c -s emacsserver"'),))
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


def main():
    clargs = parse_command_line()
    if clargs.install_elpy:
        shell(COMMANDS.get_elpy_script)
        shell(COMMANDS.install_elpy)
        shell(COMMANDS.remove_elpy_script)
        return

    packages = PACKAGES
    if clargs.force_x:
        packages = packages._replace(emacs='emacs')

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
