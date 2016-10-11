# -*- coding: utf-8 -*-

import sys
import subprocess

#
# Exceptions.
#
class ShellError(Exception):
    pass


width = lambda: int(subprocess.check_output(['tput', 'cols']))
height = lambda: int(subprocess.check_output(['tput', 'lines']))

#
# Shell tables.
#
class Table:
    def __init__(self, output_format='text',
                 page=False, auto_flush=False,
                 sizes=None, borders_color=None,
                 csv_sep=';'):
        self.output_format = output_format
        self.page = page
        self.auto_flush = auto_flush
        self.sizes = sizes
        self.borders_color = borders_color
        self.csv_separtor = csv_sep
        self._buffer = []

    def _colorize(self, color, value):
        return '\033[%sm%s\033[00m' % (color, value)

    def _autoflush(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            if self.auto_flush:
                self.flush()
        return wrapper

    @_autoflush
    def add_border(self, sizes=None, color=None):
        if self.output_format != 'text':
            return

        line = '+'
        for idx, size in enumerate(sizes or self.sizes):
            line += '-' * size
            line += '+'
        if color or self.borders_color:
            line = self._colorize(color or self.borders_color, line)
        self._buffer.append(line)

    def _add_text_line(self, values, sizes=None, colors=None,
                       borders_color=None, indent=1, sep='|'):
        sizes = sizes or self.sizes
        if sizes is None:
            raise ShellError('no sizes')
        if len(sizes) != len(values):
            raise ShellError('length of sizes is different from length of values')

        lines = []
        for idx, value in enumerate(values):
            size = sizes[idx] - 2
            if not isinstance(value, str):
                value = str(value)

            line_number = 0
            column_lines = []

            # Split column value on new line.
            value_lines = value.split('\n')
            for line in value_lines:
                # Split line on word.
                line = line.split(' ')
                cur_line = ' '
                while line:
                    word = line.pop(0)
                    new_line = cur_line + word + ' '
                    if len(new_line) > size + 2:
                        if cur_line == ' ':
                            cur_line = new_line
                            column_lines.append(cur_line)
                            cur_line = ' ' * indent + ' '
                        else:
                            cur_line += ' ' * (size + 2 - len(cur_line))
                            column_lines.append(cur_line)
                            cur_line = ' ' * indent + ' ' + word + ' '
                    else:
                        cur_line = new_line
                cur_line += ' ' * (size + 2 - len(cur_line))
                column_lines.append(cur_line)

            # Add column lines.
            for line in column_lines:
                if line_number > len(lines) - 1:
                    # Initialize a new line.
                    new_line = []
                    for __ in range(len(sizes)):
                       new_column = ' ' * sizes[__]
                       if colors and colors[__]:
                           new_column = colorize(colors[idx], new_column)
                       new_line.append(new_column)
                    lines.append(new_line)
                if colors and colors[idx]:
                    line = colorize(colors[idx], line)
                lines[line_number][idx] = line
                line_number += 1

        border = sep if not borders_color else colorize(borders_color, sep)
        self._buffer.extend(border + border.join(line) + border for line in lines)

    def _add_csv_line(self, values, sep):
        pass

    def _add_dokuwiki_line(self, values, sep):
        self._buffer.append('%s %s %s' % (
            sep,
            (' %s ' % sep).join([val.replace('\n', ' \\\\') for val in values]),
            sep))

    @_autoflush
    def add_line(self, values, sizes=None, colors=None, borders_color=None, indent=1):
        {'text': lambda: self._add_text_line(values, sizes, colors, borders_color, indent, sep='|'),
         'dokuwiki': lambda: self._add_dokuwiki_line(map(str, values), sep='|'),
         'csv': lambda: self._add_csv_line(values, self.csv_separator)
        }.get(self.output_format)()

    @_autoflush
    def add_header(self, values, sizes=None, colors=None, borders_color=None, indent=1):
        {'text': lambda: self._add_text_line(values, sizes, colors, borders_color, indent, sep='|'),
         'dokuwiki': lambda: self._add_dokuwiki_line(values, sep='^'),
         'csv': lambda: self._add_csv_line(values, self.csv_separator)
        }.get(self.output_format)()

    def flush(self):
        if self.page:
            import os, pydoc
            os.environ['PAGER'] = 'less -c -r'
            pydoc.pager('\n'.join(self._buffer))
        else:
            print('\n'.join(self._buffer))
        self._buffer = []
