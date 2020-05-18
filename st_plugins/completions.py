#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sublime_plugin

from . import logger
from . import settings
from python_utils.sublime_text_utils import events
from python_utils.sublime_text_utils import utils

__all__ = [
    "RsteCompletions"
]

_default_completions_scope = """\
text.restructuredtext - source - meta.tag | \
punctuation.definition.tag.begin | \
comment.block.documentation.python"""


class RsteCompletions(utils.CompletionsSuperClass, sublime_plugin.ViewEventListener):
    _completions_scope = _default_completions_scope
    _completions = []
    _settings = settings
    _logger = logger

    def on_query_completions(self, *args, **kwargs):
        return super().on_query_completions(*args, **kwargs)


@events.on("plugin_loaded")
def on_plugin_loaded():
    RsteCompletions.update_completions()


@events.on("plugin_unloaded")
def on_plugin_unloaded():
    events.off(on_settings_changed)


@events.on("settings_changed")
def on_settings_changed(settings, **kwargs):
    """On settings changed.

    Parameters
    ----------
    settings : object
        A ``settings_utils.Settings`` instance.
    **kwargs
        Keyword arguments.
    """
    if settings.has_changed("completions"):
        RsteCompletions.update_completions()


if __name__ == "__main__":
    pass
