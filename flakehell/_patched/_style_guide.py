from __future__ import absolute_import, unicode_literals

from builtins import dict, super

from flake8.style_guide import Decision, StyleGuide, StyleGuideManager

from ._violation import FlakeHellViolation

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache


class FlakeHellStyleGuideManager(StyleGuideManager):
    def __init__(self, options, formatter, decider=None):
        """Initialize our StyleGuide.

        .. todo:: Add parameter documentation.
        """
        super().__init__(options, formatter, decider)
        self.default_style_guide = FlakeHellStyleGuide(
            options, formatter, self.stats, decider=decider,
        )
        self.style_guides = [self.default_style_guide]
        self.style_guides.extend(self.populate_style_guides_with(options))

    @lru_cache(maxsize=None)
    def style_guide_for(self, filename):
        """Patched styleguide finder to give priority to flakehell's stileguides
        """
        guides = sorted(
            (g for g in self.style_guides if g.applies_to(filename)),
            key=lambda g: len(g.filename or ''),
            reverse=True,
        )
        for guide in guides:
            if isinstance(guide, FlakeHellStyleGuide):
                return guide
        return guides[0]

    def handle_error(
        self,
        code,  # type: str
        filename,  # type: str
        line_number,  # type: int
        column_number,  # type: int
        text,  # type: str
        plugin,  # type: str
        physical_line=None,  # type: str
    ):
        guide = self.style_guide_for(filename)
        params = dict(
            code=code,
            filename=filename,
            line_number=line_number,
            column_number=column_number,
            text=text,
            physical_line=physical_line,
        )
        if isinstance(guide, FlakeHellStyleGuide):
            params['plugin'] = plugin
        return guide.handle_error(**params)


class FlakeHellStyleGuide(StyleGuide):
    def handle_error(
        self,
        code,  # type: str
        filename,  # type: str
        line_number,  # type: int
        column_number,  # type: int
        text,  # type: str
        plugin,  # type: str
        physical_line=None,  # type: str
    ):
        """This function copied as is, but Violation replaced by FlakeHellViolation
        """
        disable_noqa = self.options.disable_noqa
        if not column_number:
            column_number = 0
        error = FlakeHellViolation(
            code=code,
            filename=filename,
            line_number=line_number,
            column_number=column_number + 1,
            text=text,
            physical_line=physical_line,
            plugin=plugin,
        )
        error_is_selected = (
            self.should_report_error(error.code) is Decision.Selected
        )
        is_not_inline_ignored = error.is_inline_ignored(disable_noqa) is False
        is_included_in_diff = error.is_in(self._parsed_diff)
        if (
            error_is_selected
            and is_not_inline_ignored
            and is_included_in_diff
        ):
            self.formatter.handle(error)
            self.stats.record(error)
            return 1
        return 0
