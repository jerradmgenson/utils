#!/usr/bin/python3
from argparse import ArgumentParser
from subprocess import run
from collections import namedtuple
from os import environ

_PACKAGES = (('python', 'python3'),
             ('pip', 'python3-pip'),
             ('emacs', 'emacs' if environ.get('DESKTOP_SESSION') else 'emacs-nox'))

_Packages = namedtuple('Packages', [package[0] for package in _PACKAGES])
PACKAGES = _Packages(*[package[1] for package in _PACKAGES])

PIP_PACKAGES = 'rope', 'autopep8', 'yapf', 'black', 'flake8', 'ipython'

_COMMANDS = (('create_venv', 'python3 -m venv ~/.default-venv'),
             ('get_elpy_script', 'wget -O "install_elpy.lisp" "https://raw.githubusercontent.com/jerradmgenson/utils/emacs/install_elpy.lisp"'),
             ('remove_emacsfile', 'rm ~/.emacs'),
             ('install_elpy', 'emacs --script install_elpy.lisp'),
             ('remove_elpy_script', 'rm install_elpy.lisp'),
             ('get_emacsfile', 'wget -O "{}/.emacs" "https://raw.githubusercontent.com/jerradmgenson/utils/emacs/.emacs"'.format(environ['HOME'])))

_Commands = namedtuple('Commands', [command[0] for command in _COMMANDS])
COMMANDS = _Commands(*[command[1] for command in _COMMANDS])

GIT_CONFIG = {'user.name': 'Jerrad Genson',
              'user.email': 'jerradgenson@gmail.com',
              'core.editor': 'emacs'}


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
        command = 'sudo dnf -y install ' + ' '.join(packages)
        shell(command)

    for command in COMMANDS:
        shell(command)

    for pip_package in PIP_PACKAGES:
        shell('~/.default-venv/bin/pip --no-cache-dir install ' + pip_package)

    for option, value in GIT_CONFIG.items():
        shell('git config --global {} {}'.format(option, value))


def shell(command):
    print(command)
    run(command, shell=True)


def parse_command_line():
    parser = ArgumentParser()
    parser.add_argument('-n', '--no-sudo', action='store_true')
    parser.add_argument('-f', '--force-x', action='store_true')
    parser.add_argument('-e', '--install-elpy', action='store_true')
    clargs = parser.parse_args()
    if clargs.no_sudo:
        print('Configuring environment without running sudo commands.')

    if clargs.force_x:
        print('Installing Emacs with X support, even in a headless environment.')

    if clargs.install_elpy:
        print('Intalling Elpy only and then exiting.')

    return clargs


if __name__ == '__main__':
    main()
