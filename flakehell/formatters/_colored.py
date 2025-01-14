from __future__ import absolute_import, unicode_literals

import re

from flake8.formatting.default import Default
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer

from termcolor import colored

from .._logic import color_code, color_description

REX_TEXT = re.compile('[A-Z]+')


class ColoredFormatter(Default):
    error_format = '{path}:{row}:{col}: {code} {text}'

    def after_init(self):
        if self.options.format.lower() not in ('default', 'colored'):
            self.error_format = self.options.format
        self._lexer = PythonLexer()
        self._formatter = TerminalFormatter()

    def format(self, error):
        filename = error.filename
        if filename.startswith('./'):
            filename = filename[2:]

        line = self.error_format.format(
            code=color_code(error.code),
            text=color_description(error.text),
            path=filename,
            row=colored(error.line_number, 'green'),
            col=colored(error.column_number, 'green'),
        )
        plugin = getattr(error, 'plugin', None)
        if plugin:
            line += colored(' [{}]'.format(plugin), 'grey')
        return line

    def show_source(self, error):
        # type: (...) -> str
        """Called when ``--show-source`` option is provided."""
        if not self._should_show_source(error):
            return ''

        formated_line = error.physical_line.lstrip()
        adjust = len(error.physical_line) - len(formated_line)

        code = highlight(
            formated_line,
            self._lexer,
            self._formatter,
        )

        return '  {code}  {pointer}^'.format(
            code=code,
            pointer=' ' * (error.column_number - 1 - adjust),
        )

    def _should_show_source(self, error):
        # type: (...) -> bool
        return self.options.show_source and error.physical_line is not None
