#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

import sublime
import sublime_plugin

from . import is_desired_scope
from . import logger
from . import plugin_name
from . import settings
from python_utils import cmd_utils
from python_utils.misc_utils import get_system_tempdir
from python_utils.sublime_text_utils.utils import get_file_path
from python_utils.sublime_text_utils.utils import get_view_context
from python_utils.sublime_text_utils.utils import substitute_variables

__all__ = [
    "RstePreviewCommand",
    "RstePreviewListener"
]

rst_to_html = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.path.join(os.path.dirname(__file__),
                                  os.pardir,
                                  "st_scripts",
                                  "rst_to_html.py")
                     ))))


class StorageClass():
    def __init__(self):
        self.open_previews = {}


Storage = StorageClass()


class RstePreviewCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        file_path = get_file_path(self.view)
        text = self.view.substr(sublime.Region(0, self.view.size())).encode("utf-8")

        if not text or not file_path:
            sublime.status_message("No content to preview")
            return

        html_file_id = "%d-%d" % (self.view.window().id(), self.view.id())
        html_file_path = os.path.join(get_system_tempdir(), plugin_name, html_file_id + ".html")

        cmd = [rst_to_html, html_file_path]
        stylesheets = substitute_variables(get_view_context(
            self.view), settings.get("preview_stylesheets"))

        if stylesheets:
            for css in stylesheets:
                cmd.append("--extra-css")
                cmd.append(css)

        if html_file_id not in Storage.open_previews:
            Storage.open_previews = html_file_id
            cmd.append("--open-in-browser")
        else:
            sublime.status_message("Reload web page")

        with cmd_utils.popen(cmd,
                             logger=logger,
                             bufsize=160 * len(text),
                             cwd=os.path.dirname(rst_to_html)) as proc:
            stdout, stderr = proc.communicate(text)

        if stderr:
            logger.error("%s Error:\n%s" %
                         (self.__class__.__name__, str(stderr.decode("utf-8")).strip()))

    def is_enabled(self):
        return is_desired_scope(self.view)

    def is_visible(self):
        return is_desired_scope(self.view)


class RstePreviewListener(sublime_plugin.EventListener):
    def on_close(self, view):
        if view and view.id() and view.window() and view.window().id():
            html_file_id = "%d-%d" % (view.window().id(), view.id())

            if html_file_id in Storage.open_previews:
                del Storage.open_previews[html_file_id]


if __name__ == "__main__":
    pass
