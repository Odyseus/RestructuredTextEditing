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
import sublime
import sublime_plugin

__all__ = [
    "RsteEmphasisCommand",
    "RsteLiteralCommand",
    "RsteStrongemphasisCommand",
    "RsteSubstitutionCommand"
]


class SurroundCmd(sublime_plugin.TextCommand):
    """
    Base class to surround the selection with text.
    """
    surround = ""

    def run(self, edit):
        for sel in self.view.sel():
            len_surround = len(self.surround)
            sel_str = self.view.substr(sel)
            rsel = sublime.Region(sel.begin() - len_surround, sel.end() + len_surround)
            rsel_str = self.view.substr(rsel)
            if sel_str[:len_surround] == self.surround and sel_str[-len_surround:] == self.surround:
                replacement = sel_str[len_surround:-len_surround]
            else:
                replacement = "%s%s%s" % (self.surround, sel_str, self.surround)
            if rsel_str == replacement:
                self.view.sel().subtract(sel)
                self.view.replace(edit, rsel, sel_str)
                self.view.sel().add(sublime.Region(rsel.begin(), rsel.begin() + len(sel_str)))
            else:
                self.view.replace(edit, sel, replacement)


class RsteStrongemphasisCommand(SurroundCmd):
    surround = "**"


class RsteEmphasisCommand(SurroundCmd):
    surround = "*"


class RsteLiteralCommand(SurroundCmd):
    surround = "``"


class RsteSubstitutionCommand(SurroundCmd):
    surround = "|"


if __name__ == "__main__":
    pass
