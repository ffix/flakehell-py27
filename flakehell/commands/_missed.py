from __future__ import absolute_import, print_function, unicode_literals

from .._constants import NAME, VERSION, ExitCodes
from .._logic import get_installed, get_plugin_rules
from .._patched import FlakeHellApplication
from .._types import CommandResult


def missed_command(argv):
    # type: (...) -> CommandResult
    """Show patterns from the config that has no matched plugin installed.
    """
    if argv and argv[0] == '--help':
        print(missed_command.__doc__)
        return 0, ''
    if argv:
        return ExitCodes.TOO_MANY_ARGS, 'the command does not accept arguments'

    app = FlakeHellApplication(program=NAME, version=VERSION)
    installed_plugins = sorted(get_installed(app=app), key=lambda p: p['name'])
    if not installed_plugins:
        return ExitCodes.NO_PLUGINS_INSTALLED, 'no plugins installed'

    count = 0
    for pattern in app.options.plugins:
        for plugin in installed_plugins:
            rules = get_plugin_rules(
                plugin_name=plugin['name'],
                plugins={pattern: ['+*']},
            )
            if rules:
                break
        else:
            print(pattern)
            count += 1
    return count, ''
