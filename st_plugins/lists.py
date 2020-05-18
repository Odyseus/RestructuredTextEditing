#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Smart list is used to automatially continue the current list.
Author: Muchenxuan Tong <demon386@gmail.com>

Original from https://github.com/demon386/SmartMarkdown with this patch:
https://github.com/vovkkk/SmartMarkdown/commit/bb1bb76179771212c1f21883d9b64d0a299fc98c
roman number conversion from Mark Pilgrim's "Dive into Python"

Modified by Martín Gaitán <gaitan@gmail.com>

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


from . import BaseBlockCmd


__all__ = [
    "RsteIndentListItemCommand",
    "RsteSmartListCommand"
]

ORDER_LIST_PATTERN = re.compile(r"(\s*[(]?)(\d+|[a-y]|[A-Y])([.)]\s+)(.*)")
UNORDER_LIST_PATTERN = re.compile(r"(\s*(?:[-+|*]+|[(]?#[).]))(\s+)\S+")
EMPTY_LIST_PATTERN = re.compile(
    r"(\s*)([-+*]|[(]?(?:\d+|[a-y]|[A-Y]|#|[MDCLXVImdclxvi]+)[.)])(\s+)$")
NONLIST_PATTERN = re.compile(r"(\s*[>|%]+)(\s+)\S?")
ROMAN_PATTERN = re.compile(r"(\s*[(]?)(M{0,4}CM|CD|D?C{0,3}XC|XL|L?X{0,3}IX|IV|V?I{0,3})([.)]\s+)(.*)",
                           re.IGNORECASE)
# Define digit mapping
ROMAN_MAP = (("M", 1000),
             ("CM", 900),
             ("D", 500),
             ("CD", 400),
             ("C", 100),
             ("XC", 90),
             ("L", 50),
             ("XL", 40),
             ("X", 10),
             ("IX", 9),
             ("V", 5),
             ("IV", 4),
             ("I", 1))


class RomanError(Exception):
    pass


class NotIntegerError(RomanError):
    pass


class InvalidRomanNumeralError(RomanError):
    pass


def to_roman(n):
    """convert integer to Roman numeral"""
    if not (0 < n < 5000):
        raise Exception("number out of range (must be 1..4999)")
    result = ""
    for numeral, integer in ROMAN_MAP:
        while n >= integer:
            result += numeral
            n -= integer
    return result


def from_roman(s):
    """convert Roman numeral to integer"""
    result = 0
    index = 0
    for numeral, integer in ROMAN_MAP:
        while s[index:index + len(numeral)] == numeral:
            result += integer
            index += len(numeral)
    return result


class RsteSmartListCommand(BaseBlockCmd):

    def run(self, edit):

        def update_ordered_list(lines):
            new_lines = []
            next_num = None

            def kind(a):
                return a

            for line in lines:
                match = ORDER_LIST_PATTERN.match(line)
                if not match:
                    new_lines.append(line)
                    continue
                new_line = match.group(1) + \
                    (kind(next_num) or match.group(2)) + \
                    match.group(3) + match.group(4)
                new_lines.append(new_line)

                if not next_num:
                    try:
                        next_num = int(match.group(2))
                        kind = str
                    except ValueError:
                        next_num = ord(match.group(2))
                        kind = chr
                next_num += 1
            return new_lines

        def update_roman_list(lines):
            new_lines = []
            next_num = None

            def kind(a):
                return a

            for line in lines:
                match = ROMAN_PATTERN.match(line)
                if not match:
                    new_lines.append(line)
                    continue
                new_line = match.group(1) + \
                    (kind(next_num) or match.group(2)) + \
                    match.group(3) + match.group(4)
                new_lines.append(new_line)

                if not next_num:
                    actual = match.group(2)
                    next_num = from_roman(actual.upper())

                    if actual == actual.lower():

                        def kind(a):
                            return to_roman(a).lower()

                    else:
                        kind = to_roman
                next_num += 1
            return new_lines

        for region in self.view.sel():
            line_region = self.view.line(region)
            # the content before point at the current line.
            before_point_region = sublime.Region(line_region.a,
                                                 region.a)
            before_point_content = self.view.substr(before_point_region)
            # Disable smart list when folded.
            folded = False
            for i in self.view.folded_regions():
                if i.contains(before_point_region):
                    self.view.insert(edit, region.a, "\n")
                    folded = True
            if folded:
                break

            match = EMPTY_LIST_PATTERN.match(before_point_content)
            if match:
                insert_text = match.group(1) + \
                    re.sub(r"\S", " ", str(match.group(2))) + \
                    match.group(3)
                self.view.erase(edit, before_point_region)
                self.view.insert(edit, line_region.a, insert_text)
                break

            match = ROMAN_PATTERN.match(before_point_content)
            if match:
                actual = match.group(2)
                next_num = to_roman(from_roman(actual.upper()) + 1)
                if actual == actual.lower():
                    next_num = next_num.lower()

                insert_text = match.group(1) + \
                    next_num + \
                    match.group(3)
                self.view.insert(edit, region.a, "\n" + insert_text)

                # backup the cursor position
                pos = self.view.sel()[0].a

                # update the whole list
                region, lines, indent = self.get_block_bounds()
                new_list = update_roman_list(lines)
                self.view.replace(edit, region, "\n".join(new_list) + "\n")
                # restore the cursor position
                self.view.sel().clear()
                self.view.sel().add(sublime.Region(pos, pos))
                self.view.show(pos)

                break

            match = ORDER_LIST_PATTERN.match(before_point_content)
            if match:
                try:
                    next_num = str(int(match.group(2)) + 1)
                except ValueError:
                    next_num = chr(ord(match.group(2)) + 1)

                insert_text = match.group(1) + \
                    next_num + \
                    match.group(3)
                self.view.insert(edit, region.a, "\n" + insert_text)

                # backup the cursor position
                pos = self.view.sel()[0].a

                # update the whole list
                region, lines, indent = self.get_block_bounds()
                new_list = update_ordered_list(lines)
                self.view.replace(edit, region, "\n".join(new_list) + "\n")
                # restore the cursor position
                self.view.sel().clear()
                self.view.sel().add(sublime.Region(pos, pos))
                self.view.show(pos)
                break

            match = UNORDER_LIST_PATTERN.match(before_point_content)
            if match:
                insert_text = match.group(1) + match.group(2)
                self.view.insert(edit, region.a, "\n" + insert_text)
                break

            match = NONLIST_PATTERN.match(before_point_content)
            if match:
                insert_text = match.group(1) + match.group(2)
                self.view.insert(edit, region.a, "\n" + insert_text)
                break

            self.view.insert(edit, region.a, "\n" +
                             re.sub(r"\S+\s*", "", before_point_content))
        self.adjust_view()

    def adjust_view(self):
        for region in self.view.sel():
            self.view.show(region)


class RsteIndentListItemCommand(sublime_plugin.TextCommand):
    bullet_pattern = r"([-+*]|([(]?(\d+|#|[a-y]|[A-Y]|[MDCLXVImdclxvi]+))([).]))"
    bullet_pattern_re = re.compile(bullet_pattern)
    line_pattern_re = re.compile(r"^\s*" + bullet_pattern)
    spaces_re = re.compile(r"^\s*")

    def run(self, edit, reverse=False):
        for region in self.view.sel():
            if region.a != region.b:
                continue

            line = self.view.line(region)
            line_content = self.view.substr(line)

            new_line = line_content

            m = self.line_pattern_re.match(new_line)
            if not m:
                return

            # Determine how to indent (tab or spaces)
            tab_str = self.view.settings().get("tab_size", 4) * " "
            sep_str = " " if m.group(4) else ""

            prev_line = self.view.line(sublime.Region(line.begin() - 1, line.begin() - 1))
            prev_line_content = self.view.substr(prev_line)

            prev_prev_line = self.view.line(
                sublime.Region(
                    prev_line.begin() - 1,
                    prev_line.begin() - 1))
            prev_prev_line_content = self.view.substr(prev_prev_line)

            if not reverse:
                # Do the indentation
                new_line = self.bullet_pattern_re.sub(tab_str + sep_str + r"\1", new_line)

                # Insert the new item
                if prev_line_content:
                    new_line = "\n" + new_line

            else:
                if not new_line.startswith(tab_str):
                    continue
                # Do the unindentation
                new_line = re.sub(tab_str + sep_str + self.bullet_pattern, r"\1", new_line)

                # Insert the new item
                if prev_line_content:
                    new_line = "\n" + new_line
                else:
                    prev_spaces = self.spaces_re.match(prev_prev_line_content).group(0)
                    spaces = self.spaces_re.match(new_line).group(0)
                    if prev_spaces == spaces:
                        line = sublime.Region(line.begin() - 1, line.end())

            endings = [".", ")"]

            # Transform the bullet to the next/previous bullet type
            if self.view.settings().get("list_indent_auto_switch_bullet", True):
                bullets = self.view.settings().get("list_indent_bullets", ["*", "-", "+"])

                def change_bullet(m):
                    bullet = m.group(1)
                    try:
                        return bullets[(bullets.index(bullet) +
                                        (1 if not reverse else -1)) % len(bullets)]
                    except ValueError:
                        pass
                    n = m.group(2)
                    ending = endings[(endings.index(m.group(4)) +
                                      (1 if not reverse else -1)) % len(endings)]
                    if n.isdigit():
                        return "${1:a}" + ending
                    elif n != "#":
                        return "${1:0}" + ending
                    return m.group(2) + ending
                new_line = self.bullet_pattern_re.sub(change_bullet, new_line)

            self.view.replace(edit, line, "")
            self.view.run_command("insert_snippet", {"contents": new_line})


if __name__ == "__main__":
    pass
