#     PyQt hex editor widget
#     Copyright (C) 2015 Christoph Sarnowski

#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; either version 2 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License along
#     with this program; if not, write to the Free Software Foundation, Inc.,
#     51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from PySide.QtGui import *
from PySide.QtCore import *
from binascii import *
import time
from math import *
import re
import collections


class HexCoder:
    def __init__(self, data, bytes_per_line=16):
        self.data = data
        self.bpl = bytes_per_line

    def getLine(self, pos=0):
        return (pos, self.bpl, self.data[pos:pos+self.bpl])


    def getLines(self, pos=0):
        while pos < len(self.data)-self.bpl:
            yield (pos, self.bpl, re.sub("[^a-zA-Z0-9]",".", self.data[pos:pos+self.bpl]))
            pos += self.bpl
        yield (pos, len(self.data)-pos, re.sub("[^a-zA-Z0-9]",".", self.data[pos:]))

    def maxWidth(self):
        return self.bpl * 3 - 1

    def numLines(self):
        return int(ceil(float(len(self.data))/ self.bpl))

Cursor = collections.namedtuple("Cursor", ["address", "nibble"])

class HexView(QAbstractScrollArea):
    def __init__(self, parent=None, coder=HexCoder, data=open("hexview.py").read()):
        super(HexView, self).__init__(parent)
        self.data = data
        self.coder = coder(data)
        self.setFont(QFont("Courier", 12))
        self.charWidth = self.fontMetrics().width("2")
        self.charHeight = self.fontMetrics().height()
        self.addr_width = 8
        self.pos = 0
        self.blink = False
        self.data_width = self.coder.maxWidth()

        self.addr_start = 1
        self.gap2 = 2
        self.gap3 = 2
        self.data_start = self.addr_start + self.addr_width + self.gap2
        self.code_start = self.data_start + self.data_width + self.gap3

        self.magic_font_offset = 4
        self.adjust()
        self.cursor = Cursor(32,1)
        self.cursorTimer = QTimer()
        self.cursorTimer.timeout.connect(self.updateCursor)
        self.cursorTimer.setInterval(500)
        self.cursorTimer.start()

    def cursorRect(self):
        return self.cursorToCoord(self.cursor)[0]

    def cursorRect2(self):
        return self.cursorToCoord(self.cursor)[1]

    def updateCursor(self):
        self.blink = not self.blink
        self.viewport().update(self.cursorRect())


    def visibleColumns(self):
        ret = int(ceil(float(self.viewport().width())/self.charWidth))
        return ret

    def visibleLines(self):
        return int(ceil(float(self.viewport().height())/self.charHeight))

    def totalCharsPerLine(self):
        ret = self.coder.bpl * 4 + self.addr_width + self.addr_start + self.gap2 + self.gap3
        return ret

    def adjust(self):
        self.horizontalScrollBar().setRange(0, self.totalCharsPerLine() - self.visibleColumns())
        self.horizontalScrollBar().setPageStep(self.visibleColumns())
        self.verticalScrollBar().setRange(0, self.coder.numLines() - self.visibleLines() + 1)
        self.verticalScrollBar().setPageStep(self.visibleLines())

    def coordToAddress(self, coord):
        column = int(coord.x() / self.charWidth)
        row = int((coord.y()-self.magic_font_offset) / self.charHeight)
        if column >= self.data_start and column < self.code_start:
            rel_column = column-self.data_start
            line_index = rel_column - (rel_column / 3)
            addr = self.pos + line_index/2 + row * self.coder.bpl
            return Cursor(addr, 1 if rel_column % 3 == 1 else 0)

    def cursorToCoord(self, cur):
        address = cur.address
        rel_address = address - self.pos
        row = rel_address / self.coder.bpl
        line_index = rel_address % self.coder.bpl
        rel_column = line_index * 3
        column = rel_column + self.data_start
        x = column * self.charWidth
        y = row * self.charHeight + self.magic_font_offset


        coord_code = QRect((self.code_start + line_index)* self.charWidth,y,
                           self.charWidth, self.charHeight)
        return (QRect(x + cur.nibble * self.charWidth,y,self.charWidth, self.charHeight),
                coord_code)

    def charAtCursor(self, cursor):
        code_char = self.data[cursor.address]
        hexcode = "{:02x}".format(ord(code_char))
        hex_char = hexcode[cursor.nibble]
        return (hex_char, code_char)


    def mousePressEvent(self, event):
        cur = self.coordToAddress(event.pos())
        self.blink = False
        self.viewport().update(self.cursorRect())
        self.viewport().update(self.cursorRect2())
        self.cursor = cur


    def resizeEvent(self, event):
        self.adjust()

    def paintEvent(self, event):
        start = time.time()
        painter = QPainter(self.viewport())
        palette = self.viewport().palette()

        rect = self.cursorRect()
        rect.setRight(self.cursorRect2().right())

        #painter.fillRect(event.rect(), Qt.green)
        if event.rect() == self.cursorRect():
            if self.blink:
                painter.fillRect(self.cursorRect(), Qt.black)
                painter.setPen(Qt.white)
            painter.drawText(self.cursorRect().bottomLeft().x(),
                             self.cursorRect().bottomLeft().y() - self.magic_font_offset+1,
                             self.charAtCursor(self.cursor)[0])
            self.viewport().update(self.cursorRect2())

            return

        if event.rect() == self.cursorRect2():
            if self.blink:
                painter.fillRect(self.cursorRect2(), Qt.black)
                painter.setPen(Qt.white)
            painter.drawText(self.cursorRect2().bottomLeft().x(),
                             self.cursorRect2().bottomLeft().y() - self.magic_font_offset+1,
                             self.charAtCursor(self.cursor)[1])
            return



        charh = self.charHeight
        charw = self.charWidth
        charw3 = 3*charw
        data_width = self.data_width
        addr_width = self.addr_width
        addr_start = self.addr_start
        gap2 = self.gap2
        gap3 = self.gap3

        data_start = addr_start + addr_width + gap2
        code_start = data_start + data_width + gap3

        hs = self.horizontalScrollBar().value()
        addr_start -= hs
        code_start -= hs
        data_start -= hs

        # self.addr_start = addr_start
        # self.code_start = code_start
        # self.data_start = data_start

        addr_start *= charw
        data_start *= charw
        code_start *= charw

        self.pos = self.verticalScrollBar().value() * self.coder.bpl

        for i, line in enumerate(self.coder.getLines(self.pos)):
            if i > self.visibleLines():
                break

            if i % 2 == 0:
                painter.fillRect(0, (i)*charh+self.magic_font_offset,
                                 self.viewport().width(), charh,
                                 QColor(240,240,240))
            (address, length, coded) = line

            data = self.data[address:address+length]

            # address
            painter.drawText(addr_start, (i+1)*charh, "{:08x}".format(address))

            # hex data
            col = 0
            for byte in data:
                painter.drawText(data_start + col, (i+1)*charh, "{:02x}".format(ord(byte)))
                col += charw3


            # coded data
            painter.drawText(code_start, (i+1)*charh, coded)
        painter.setPen(Qt.gray)
        painter.drawLine(data_start-charw, 0, data_start-charw, self.height())
        painter.drawLine(code_start-charw, 0, code_start-charw, self.height())

        if self.blink and self.cursorRect().top() < self.height() and self.cursorRect().bottom() > 0:
            painter.fillRect(self.cursorRect(), Qt.black)
            painter.fillRect(self.cursorRect2(), Qt.black)
            painter.setPen(Qt.white)
            painter.drawText(self.cursorRect().bottomLeft().x(),
                             self.cursorRect().bottomLeft().y() - self.magic_font_offset+1,
                             self.charAtCursor(self.cursor)[0])
            painter.drawText(self.cursorRect2().bottomLeft().x(),
                             self.cursorRect2().bottomLeft().y() - self.magic_font_offset+1,
                             self.charAtCursor(self.cursor)[1])
        print "painting took: ", time.time()-start, "s"


if __name__ == '__main__':
    app = QApplication([])
    h = HexView()
    h.setGeometry(-1870,32,800,600)
    h.show()
    app.exec_()
