:mod:`porcupine.dirs` --- Paths to Porcupine's files
====================================================

.. module:: porcupine.dirs

This small module contains information about where Porcupine is
installed and where its setting files are.

.. data:: cachedir
    :type: pathlib.Path

    User-wide temporary files go here. Currently Porcupine doesn't use
    this for anything, but plugins may use this.

.. data:: configdir
    :type: pathlib.Path

    Porcupine's user-wide settings, color themes and other things are
    here.
