# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2022-2024 by Helmut Konrad Schewe. All rights reserved.
# This file is property of Helmut Konrad Schewe. Any unauthorized copy,
# use or distribution is an offensive act against international law and may
# be prosecuted under federal law. Its content is company confidential.
# =============================================================================

import utilo


class TablePrinter:  # pylint:disable=too-many-instance-attributes

    def __init__(self, cols, rows, width=5, height=3, border='|*|*='):
        self.content = [[] for _ in range(cols * rows)]
        self.cols = cols
        self.rows = rows
        self.width = width
        self.height = height
        self.border_lr, self.border_inner, self.border_line = border.split('*')

    def insert(self, col, row, value: str):
        assert col < self.cols, f'{col}<{self.cols}'
        assert row < self.rows, f'{row}<{self.rows}'
        index = row * self.cols + col
        lines = [item[0:self.getwidth(col)] for item in value.splitlines()]
        self.content[index].extend(lines)

    def getwidth(self, index) -> int:
        try:
            return self.width[index] + 1
        except TypeError:
            return self.width

    @property
    def tablewidth(self) -> int:
        if utilo.iterable(self.width):  # pylint:disable=W0160
            width = sum(self.width) + len(self.width)
        else:
            width = (self.width + 1) * self.cols + (len(self.border_lr) * 2) + 1
        return width

    def __str__(self):
        width = self.tablewidth
        result = ''
        for row in range(self.rows):
            newline = False
            for _ in range(self.height):
                done = False
                line = [self.border_lr]
                for col in range(self.cols):
                    current = self.content[row * self.cols + col]
                    if not current:
                        line.append(' ' * self.getwidth(col))
                        continue
                    done = True
                    raw = current[0]
                    current.remove(raw)
                    line.append(raw.ljust(self.getwidth(col), ' '))
                line.append(self.border_lr)
                raw = self.border_inner.join(line)
                newline |= done
                if done:
                    result += raw.rstrip()
                    result += utilo.NEWLINE
            if newline and self.border_line:
                result += (self.border_line * width) + utilo.NEWLINE
        if result:
            result = self.border_line * width + utilo.NEWLINE + result
        return result


def table_smallest(table) -> str:
    noborder = '**'
    widths = table_width(table)
    printer = TablePrinter(
        cols=len(widths),
        rows=len(table),
        width=widths,
        height=30,
        border=noborder,
    )
    for row_index, row in enumerate(table):
        for col_index, col in enumerate(row):
            if isinstance(col, str):
                printer.insert(col_index, row_index, col)
                continue
            for item in col:
                printer.insert(col_index, row_index, str(item))
    result = str(printer)
    return result


def table_width(table) -> tuple:
    result = []
    for row in table:
        for index, column in enumerate(row):
            if isinstance(column, str):
                try:
                    result[index] = max((result[index]), len(column))
                except IndexError:
                    result[index] = len(column)
            else:
                for item in column:
                    try:
                        result[index] = max((result[index]), len(str(item)))
                    except IndexError:
                        result.append(len(str(item)))
    return tuple(result)
