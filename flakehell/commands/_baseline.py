from __future__ import absolute_import, unicode_literals

from .._constants import NAME, VERSION
from .._patched import FlakeHellApplication
from .._types import CommandResult, SimpleNamespace
from ..formatters import BaseLineFormatter


def baseline_command(argv):
    # type: () -> CommandResult
    """Run patched flake8 against the code.
    """
    app = FlakeHellApplication(program=NAME, version=VERSION)
    app.formatter = BaseLineFormatter(SimpleNamespace(
        output_file=None,
        show_source=False,
    ))
    try:
        app.run(argv)
        app.exit()
    except SystemExit as exc:
        return exc.code, ''
