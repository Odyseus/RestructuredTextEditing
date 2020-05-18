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

from . import BaseBlockCmd

__all__ = [
    "RsteSimpletableCommand"
]


class RsteSimpletableCommand(BaseBlockCmd):

    _SEPARATOR = "  "

    def get_result(self, indent, table):
        result = "\n".join(self._draw_table(indent, table))
        result += "\n"
        return result

    def run(self, edit):
        region, lines, indent = self.get_block_bounds()
        table = self._parse_table(lines)
        result = self.get_result(indent, table)
        self.view.replace(edit, region, result)

    def _split_table_cells(self, row_string):
        return re.split(r"\s\s+", row_string.strip())

    def _parse_table(self, raw_lines):
        parsed_lines = []
        for row_string in raw_lines:
            if not self._row_is_separator(row_string):
                parsed_lines.append(self._split_table_cells(row_string))
        return parsed_lines

    def _row_is_separator(self, row):
        return re.match("^[\t =]+$", row)

    def _table_header_line(self, widths):
        linechar = "="
        parts = []
        for width in widths:
            parts.append(linechar * width)
        return RsteSimpletableCommand._SEPARATOR.join(parts)

    def _get_column_max_widths(self, table):
        widths = []
        for row in table:
            num_fields = len(row)
            # dynamically grow
            if num_fields >= len(widths):
                widths.extend([0] * (num_fields - len(widths)))
            for i in range(num_fields):
                field_width = len(row[i])
                widths[i] = max(widths[i], field_width)
        return widths

    def _pad_fields(self, row, width_formats):
        """ Pad all fields using width formats """
        new_row = []
        for i in range(len(row)):
            col = row[i]
            col = width_formats[i] % col
            new_row.append(col)
        return new_row

    def _draw_table(self, indent, table):
        if not table:
            return []
        col_widths = self._get_column_max_widths(table)
        # Reserve room for separater
        len_sep = len(RsteSimpletableCommand._SEPARATOR)
        sep_col_widths = [(col + len_sep) for col in col_widths]
        width_formats = [("%-" + str(w) + "s" + RsteSimpletableCommand._SEPARATOR)
                         for w in col_widths]

        header_line = self._table_header_line(sep_col_widths)
        output = [indent + header_line]
        first = True
        for row in table:
            # draw the lines (num_lines) for this row
            row = self._pad_fields(row, width_formats)
            output.append(indent + RsteSimpletableCommand._SEPARATOR.join(row))
            # draw the under separator for header
            if first:
                output.append(indent + header_line)
                first = False

        output.append(indent + header_line)
        return output


if __name__ == "__main__":
    pass
