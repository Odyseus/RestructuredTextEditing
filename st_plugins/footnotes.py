#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2013, Martín Gaitán, Dominic Bou-Samra and contributors
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

  Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

  Neither the name of this project nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import re

import sublime
import sublime_plugin

__all__ = [
    "Footnotes",
    "MarkFootnotes",
    "RsteGoToFootnoteDefinitionCommand",
    "RsteGoToFootnoteReferenceCommand",
    "RsteInsertFootnoteCommand",
    "RsteMagicFootnotesCommand"
]

DEFINITION_KEY = "RestructuredTextEditing-footnote-definitions"
REFERENCE_KEY = "RestructuredTextEditing-footnote-references"
REFERENCE_REGEX = r"\[(\d+)\]\_"
DEFINITION_REGEX = r"^\.\.\s\[(\d+)\]"


def get_id(txt):
    return re.findall(r"\d+", txt)[0]


def get_footnote_references(view):
    ids = {}
    for ref in view.get_regions(REFERENCE_KEY):
        if not re.match(DEFINITION_REGEX, view.substr(view.line(ref))):
            id = get_id(view.substr(ref))
            if id in ids:
                ids[id].append(ref)
            else:
                ids[id] = [ref]
    return ids


def get_footnote_definition_markers(view):
    ids = {}
    for defn in view.get_regions(DEFINITION_KEY):
        id = get_id(view.substr(defn))
        ids[id] = defn
    return ids


def get_footnote_identifiers(view):
    ids = get_footnote_references(view).keys()
    list(ids).sort()
    return ids


def get_last_footnote_marker(view):
    ids = sorted([int(a) for a in get_footnote_identifiers(view) if a.isdigit()])
    if len(ids):
        return int(ids[-1])
    else:
        return 0


def get_next_footnote_marker(view):
    return get_last_footnote_marker(view) + 1


def is_footnote_definition(view):
    line = view.substr(view.line(view.sel()[-1]))
    return re.match(DEFINITION_REGEX, line)


def is_footnote_reference(view):
    refs = view.get_regions(REFERENCE_KEY)
    for ref in refs:
        if ref.contains(view.sel()[0]):
            return True
    return False


def strip_trailing_whitespace(view, edit):
    tws = view.find(r"\s+\Z", 0)
    if tws:
        view.erase(edit, tws)


class Footnotes(sublime_plugin.EventListener):
    def update_footnote_data(self, view):
        view.add_regions(
            REFERENCE_KEY,
            view.find_all(REFERENCE_REGEX),
            "", "cross",
        )
        view.add_regions(
            DEFINITION_KEY,
            view.find_all(DEFINITION_REGEX),
            "",
            "cross",
        )

    def on_modified(self, view):
        self.update_footnote_data(view)

    def on_load(self, view):
        self.update_footnote_data(view)


class RsteMagicFootnotesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if (is_footnote_definition(self.view)):
            self.view.run_command("rste_go_to_footnote_reference")
        elif (is_footnote_reference(self.view)):
            self.view.run_command("rste_go_to_footnote_definition")
        else:
            self.view.run_command("rste_insert_footnote")


class RsteInsertFootnoteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        startloc = self.view.sel()[-1].end()
        markernum = get_next_footnote_marker(self.view)
        if bool(self.view.size()):
            targetloc = self.view.find(r"(\s|$)", startloc).begin()
        else:
            targetloc = 0
        self.view.insert(edit, targetloc, "[%s]_" % markernum)
        self.view.insert(edit, self.view.size(), "\n.. [%s] " % markernum)
        self.view.sel().clear()
        self.view.sel().add(sublime.Region(self.view.size()))
        self.view.show(self.view.size())


class MarkFootnotes(sublime_plugin.EventListener):
    def update_footnote_data(self, view):
        view.add_regions(REFERENCE_KEY, view.find_all(REFERENCE_REGEX), "", "cross", sublime.HIDDEN)
        view.add_regions(
            DEFINITION_KEY,
            view.find_all(DEFINITION_REGEX),
            "",
            "cross",
            sublime.HIDDEN)

    def on_modified(self, view):
        self.update_footnote_data(view)

    def on_load(self, view):
        self.update_footnote_data(view)


class RsteGoToFootnoteReferenceCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        refs = get_footnote_references(self.view)
        match = is_footnote_definition(self.view)
        if match:
            target = match.groups()[0]
            self.view.sel().clear()
            note = refs[target][0]
            point = sublime.Region(note.end(), note.end())
            self.view.sel().add(point)
            self.view.show(note)


class RsteGoToFootnoteDefinitionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        defs = get_footnote_definition_markers(self.view)
        regions = self.view.get_regions(REFERENCE_KEY)

        sel = self.view.sel()
        if len(sel) == 1:
            target = None
            selreg = sel[0]

            for region in regions:
                # cursor beetwen the brackects
                #  ·[X]·_
                if selreg.intersects(region):
                    target = self.view.substr(region)[1:-2]
            if not target:
                # cursor is just after the underscore: [X]_·
                try:
                    a = self.view.find(REFERENCE_REGEX, sel[0].end() - 4)
                    target = self.view.substr(a)[1:-2]
                except BaseException:
                    pass
            if target:
                self.view.sel().clear()
                point = defs[target].end() + 1
                ref = sublime.Region(point, point)
                self.view.sel().add(ref)
                self.view.show(defs[target])


if __name__ == "__main__":
    pass
