#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import re

root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir)))))

import sublime
import sublime_plugin

from python_utils import log_system
from python_utils.sublime_text_utils import events
from python_utils.sublime_text_utils import logger as logger_utils
from python_utils.sublime_text_utils import settings as settings_utils


package_name = os.path.basename(root_folder)
plugin_name = "RestructuredTextEditing"

_log_file = log_system.generate_log_path(storage_dir=os.path.join(root_folder, "tmp", "logs"),
                                         prefix="LOG")
logger = logger_utils.SublimeLogger(logger_name=plugin_name, log_file=_log_file)
settings = settings_utils.Settings(name_space=plugin_name, logger=logger)


@events.on("plugin_loaded")
def on_plugin_loaded():
    settings.load()


@events.on("plugin_unloaded")
def on_plugin_unloaded():
    settings.unobserve()


def is_desired_scope(view):
    if view and len(view.sel()) > 0:
        return len(view.sel()) > 0 and bool(
            view.score_selector(view.sel()[0].a, settings.get("commands_scope", ""))
        )
    else:
        return False


class LineIndexError(Exception):
    pass


class BaseBlockCmd(sublime_plugin.TextCommand):
    def _get_row_text(self, row):

        if row < 0 or row > self.view.rowcol(self.view.size())[0]:
            raise LineIndexError("Cannot find table bounds.")

        point = self.view.text_point(row, 0)
        region = self.view.line(point)
        text = self.view.substr(region)
        return text

    def get_cursor_position(self):
        return self.view.rowcol(self.view.sel()[0].begin())

    def get_block_bounds(self):
        """given the cursor position as started point,
           returns the limits and indentation"""
        row, col = self.get_cursor_position()
        upper = lower = row

        try:
            while self._get_row_text(upper - 1).strip():
                upper -= 1
        except LineIndexError:
            pass
        else:
            upper += 1

        try:
            while self._get_row_text(lower + 1).strip():
                lower += 1
        except LineIndexError:
            pass
        else:
            lower -= 1

        block_region = sublime.Region(self.view.text_point(upper - 1, 0),
                                      self.view.text_point(lower + 2, 0))
        lines = [self.view.substr(region) for region in self.view.lines(block_region)]
        try:
            row_text = self._get_row_text(upper - 1)
        except LineIndexError:
            row_text = ""
        indent = re.match(r"^(\s*).*$", row_text).group(1)
        return block_region, lines, indent

    def is_enabled(self):
        return is_desired_scope(self.view)

    def is_visible(self):
        return is_desired_scope(self.view)


if __name__ == "__main__":
    pass
