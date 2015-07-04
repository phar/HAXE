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
import sip
sip.setapi('QDate', 2)
sip.setapi('QDateTime', 2)
sip.setapi('QString', 2)
sip.setapi('QTextStream', 2)
sip.setapi('QTime', 2)
sip.setapi('QUrl', 2)
sip.setapi('QVariant', 2)

from PySide.QtGui import *
from PySide.QtCore import *
#from PyQt4.Qsci import *
from binascii import *
import time
import mmap
from math import *
import re
import os
import collections

try:
    Signal = pyqtSignal
except:
    pass

class Cursor(QObject):
    changed = Signal()

    def __init__(self, address=0, nibble=0):
        super(Cursor, self).__init__()
        self._address = address
        self._nibble = nibble

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value
        self.changed.emit()


    @property
    def nibble(self):
        return self._nibble

    @nibble.setter
    def nibble(self, value):
        self._nibble = value
        self.changed.emit()

    def update(self, other_cursor):
        changed = False
        if not self.address == other_cursor.address:
            self._address = other_cursor.address
            changed = True
        if not self.nibble == other_cursor.nibble:
            self._nibble = other_cursor.nibble
            changed = True
        if changed:
            self.changed.emit()

    def right(self):
        if self.nibble == 0:
            self.nibble = 1
        else:
            self.address +=1
            self.nibble = 0

    def left(self):
        if self.nibble == 1:
            self.nibble = 0
        else:
            self.address -=1
            self.nibble = 1

    def rewind(self, amount):
        self.address -= amount
        if self.address < 0:
            self.address = 0


    def forward(self, amount):
        self.address += amount


class Selection(QObject):
    def __init__(self, start=0, end=0, active=True, color=Qt.green):
        self._start = min(start, end)
        self._end = max(start, end)
        self.active = active
        self.color = color

    def __len__(self):
        return self._end - self._start

    def contains(self, address):
        return address >= self._start and address <= self._end

    # enforce that start <= end
    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        if not self.active:
            self._start = self._end = value
            return
        self._start = min(value, self.end)
        self._end = max(value, self.end)

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        if not self.active:
            self._start = self._end = value
            return
        self._end = max(value, self.start)
        self._start = min(value, self.start)

class HexView(QAbstractScrollArea):
    selectionChanged = Signal()
    def __init__(self, parent=None, data=open("hexview.py").read()):
        super(HexView, self).__init__(parent)
        self.data = mmap.mmap(-1, len(data))
        self.data[:] = data
        # font stuff
        self.setFont(QFont("Courier", 10))
        self.charWidth = self.fontMetrics().width("2")
        self.charHeight = self.fontMetrics().height()
        self.magic_font_offset = 4

        self.viewport().setCursor(Qt.IBeamCursor)
        # constants
        self.addr_width = 8
        self.bpl = 16
        self.addr_start = 1
        self.gap2 = 2
        self.gap3 = 2
        self.data_width = self.maxWidth()
        self.data_start = self.addr_start + self.addr_width + self.gap2
        self.code_start = self.data_start + self.data_width + self.gap3

        self.pos = 0
        self.blink = False

        self.selection = Selection(active=False, color=self.palette().color(QPalette.Highlight))

        self.highlights = []
        self._cursor = Cursor(32,1)

        self.cursor.changed.connect(self.cursorMove)
        # cursor blinking timer
        self.cursorTimer = QTimer()
        self.cursorTimer.timeout.connect(self.updateCursor)
        self.cursorTimer.setInterval(500)
        self.cursorTimer.start()

        self.adjust()

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor.update(value)

    def getLine(self, pos=0):
        return (pos, self.bpl, self.data[pos:pos+self.bpl])

    def toAscii(self, string):
        return "".join([x if ord(x) >= 33 and ord(x) <= 126 else "." for x in string])

    def getLines(self, pos=0):
        while pos < len(self.data)-self.bpl:
            yield (pos, self.bpl, self.toAscii(self.data[pos:pos+self.bpl]))
            pos += self.bpl
        yield (pos, len(self.data)-pos, self.toAscii(self.data[pos:]))

    def getBytes(self, count=1):
        return self.data[self.cursor.address:self.cursor.address+count]

    def maxWidth(self):
        return self.bpl * 3 - 1

    def numLines(self):
        return int(ceil(float(len(self.data))/ self.bpl))


    def cursorRect(self):
        return self.cursorToHexRect(self.cursor)

    def cursorRect2(self):
        return self.cursorToAsciiRect(self.cursor)

    def updateCursor(self):
        self.blink = not self.blink
        self.viewport().update(self.cursorRect())


    def visibleColumns(self):
        ret = int(ceil(float(self.viewport().width())/self.charWidth))
        return ret

    def visibleLines(self):
        return int(ceil(float(self.viewport().height())/self.charHeight))

    def totalCharsPerLine(self):
        ret = self.bpl * 4 + self.addr_width + self.addr_start + self.gap2 + self.gap3
        return ret

    def adjust(self):
        self.horizontalScrollBar().setRange(0, self.totalCharsPerLine() - self.visibleColumns() + 1)
        self.horizontalScrollBar().setPageStep(self.visibleColumns())
        self.verticalScrollBar().setRange(0, self.numLines() - self.visibleLines() + 1)
        self.verticalScrollBar().setPageStep(self.visibleLines())

    # =====================  Coordinate Juggling  ============================

    def pxToCharCoords(self, px, py):
        cx = int(px / self.charWidth)
        cy = int((py-self.magic_font_offset) / self.charHeight)
        return (cx, cy)

    def charToPxCoords(self, cx, cy):
        "return upper left corder of the rectangle containing the char at position cx, cy"
        px = cx * self.charWidth
        py = cy * self.charHeight + self.magic_font_offset
        return QPoint(px, py)

    def pxCoordToCursor(self, coord):
        column, row = self.pxToCharCoords(coord.x()+self.charWidth/2, coord.y())
        if column >= self.data_start and column < self.code_start:
            rel_column = column-self.data_start
            line_index = rel_column - (rel_column / 3)
            addr = self.pos + line_index/2 + row * self.bpl
            return Cursor(addr, 1 if rel_column % 3 == 1 else 0)

    def indexToHexCharCoords(self, index):
        rel_index = index - self.pos
        cy = rel_index / self.bpl
        line_index = rel_index % self.bpl
        rel_column = line_index * 3
        cx = rel_column + self.data_start
        return (cx, cy)

    def indexToAsciiCharCoords(self, index):
        rel_index = index - self.pos
        cy = rel_index / self.bpl
        line_index = rel_index % self.bpl
        cx = line_index + self.code_start
        return (cx, cy)

    def cursorToHexRect(self, cur):
        hex_cx, hex_cy = self.indexToHexCharCoords(cur.address)
        hex_cx += cur.nibble
        hex_point = self.charToPxCoords(hex_cx, hex_cy)
        hex_rect = QRect(hex_point, QSize(
                           2, self.charHeight))
        return hex_rect


    def cursorToAsciiRect(self, cur):
        ascii_cx, ascii_cy = self.indexToAsciiCharCoords(cur.address)
        ascii_point = self.charToPxCoords(ascii_cx-1, ascii_cy)
        ascii_rect = QRect(ascii_point, QSize(
                           2, self.charHeight))
        return ascii_rect

    def charAtCursor(self, cursor):
        code_char = self.data[cursor.address]
        hexcode = "{:02x}".format(ord(code_char))
        hex_char = hexcode[cursor.nibble]
        return (hex_char, code_char)

    # ====================  Event Handling  ==============================
    def cursorMove(self):
        x, y = self.indexToAsciiCharCoords(self.cursor.address)
        if y > self.visibleLines() - 4:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + y - self.visibleLines() + 4)
        if y < 4:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + y - 4)


    def mousePressEvent(self, event):
        cur = self.pxCoordToCursor(event.pos())
        if cur is not None:
            if self.selection.active:
                self.selection.active = False
                self.selection.start = self.selection.end = cur.address
                self.viewport().update()
            self.blink = False
            self.viewport().update(self.cursorRect())
            self.cursor = cur


    def mouseMoveEvent(self, event):
        self.selection.start = self.cursor.address
        new_cursor = self.pxCoordToCursor(event.pos())
        if new_cursor is None:
            return
        self.selection.end = new_cursor.address
        self.selection.active = True
        self.viewport().update()
        self.selectionChanged.emit()

    def mouseReleaseEvent(self, event):
        cur = self.pxCoordToCursor(event.pos())
        if cur is not None:
            self.cursor = cur
            self.viewport().update(self.cursorRect())



    def resizeEvent(self, event):
        self.adjust()


    def paintHighlight(self, painter, line, selection):
        if self.selection.active:
            cx_start_hex, cy_start_hex = self.indexToHexCharCoords(self.selection.start)
            cx_end_hex, cy_end_hex = self.indexToHexCharCoords(self.selection.end)
            cx_start_ascii, cy_start_ascii = self.indexToAsciiCharCoords(self.selection.start)
            cx_end_ascii, cy_end_ascii = self.indexToAsciiCharCoords(self.selection.end)
            if line == cy_start_hex:
                topleft_hex = QPoint(self.charToPxCoords(cx_start_hex, line))
                topleft_ascii = QPoint(self.charToPxCoords(cx_start_ascii, line))
                if line == cy_end_hex: # single line selection
                    bottomright_hex = QPoint(self.charToPxCoords(cx_end_hex, line))
                    bottomright_ascii = QPoint(self.charToPxCoords(cx_end_ascii, line))
                else:
                    bottomright_hex = QPoint(self.charToPxCoords(self.code_start - self.gap2, line))
                    bottomright_ascii = QPoint(self.charToPxCoords(self.code_start + self.bpl, line))
                bottomright_hex += QPoint(0, self.charHeight)
                bottomright_ascii += QPoint(0, self.charHeight)
                painter.fillRect(QRect(topleft_hex, bottomright_hex), selection.color)
                painter.fillRect(QRect(topleft_ascii, bottomright_ascii), selection.color)
            elif line > cy_start_hex and line <= cy_end_hex:
                topleft_hex = QPoint(self.charToPxCoords(self.data_start, line))
                topleft_ascii = QPoint(self.charToPxCoords(self.code_start, line))
                if line == cy_end_hex:
                    bottomright_hex = QPoint(self.charToPxCoords(cx_end_hex, line))
                    bottomright_ascii = QPoint(self.charToPxCoords(cx_end_ascii, line))
                else:
                    bottomright_hex = QPoint(self.charToPxCoords(self.code_start - self.gap2, line))
                    bottomright_ascii = QPoint(self.charToPxCoords(self.code_start + self.bpl, line))
                bottomright_hex += QPoint(0, self.charHeight)
                bottomright_ascii += QPoint(0, self.charHeight)
                painter.fillRect(QRect(topleft_hex, bottomright_hex), selection.color)
                painter.fillRect(QRect(topleft_ascii, bottomright_ascii), selection.color)


    def paintHex(self, painter, row, column):
        addr = self.pos + row * self.bpl + column
        topleft = self.charToPxCoords(column*3 + self.data_start, row)
        bottomleft = topleft + QPoint(0, self.charHeight-self.magic_font_offset)
        byte = "{:02x}".format(ord(self.data[addr]))
        size = QSize(self.charWidth*3, self.charHeight)
        rect = QRect(topleft, size)

        for sel in [self.selection] + self.highlights:
            if sel.active and sel.contains(addr):
                painter.fillRect(rect, sel.color)
                painter.setPen(self.palette().color(QPalette.HighlightedText))
                painter.drawText(bottomleft, byte)
                painter.setPen(self.palette().color(QPalette.WindowText))
                break
        else:
            if row % 2 == 0:
                painter.fillRect(rect, self.palette().color(QPalette.AlternateBase))
            painter.setPen(self.palette().color(QPalette.WindowText))
            painter.drawText(bottomleft, byte)


    def paintAscii(self, painter, row, column):
        addr = self.pos + row * self.bpl + column
        topleft = self.charToPxCoords(column + self.code_start, row)
        bottomleft = topleft + QPoint(0, self.charHeight-self.magic_font_offset)
        byte = self.toAscii(self.data[addr])
        size = QSize(self.charWidth, self.charHeight)
        rect = QRect(topleft, size)

        for sel in [self.selection] + self.highlights:
            if sel.active and sel.contains(addr):
                painter.fillRect(rect, sel.color)
                painter.setPen(self.palette().color(QPalette.HighlightedText))
                painter.drawText(bottomleft, byte)
                painter.setPen(self.palette().color(QPalette.WindowText))
                break
        else:
            if row % 2 == 0:
                painter.fillRect(rect, self.palette().color(QPalette.AlternateBase))
            painter.setPen(self.palette().color(QPalette.WindowText))
            painter.drawText(bottomleft, byte)



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
            self.viewport().update(self.cursorRect2())

            return

        if event.rect() == self.cursorRect2():
            if self.blink:
                painter.fillRect(self.cursorRect2(), Qt.black)
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

        self.pos = self.verticalScrollBar().value() * self.bpl

        for i, line in enumerate(self.getLines(self.pos)):
            if i > self.visibleLines():
                break

            if i % 2 == 0:
                painter.fillRect(0, (i)*charh+self.magic_font_offset,
                                 self.viewport().width(), charh,
                                 self.palette().color(QPalette.AlternateBase))
            (address, length, ascii) = line

            data = self.data[address:address+length]


            # selection highlight
            self.paintHighlight(painter, i, self.selection)
            for h in self.highlights:
                self.paintHighlight(painter, i, h)

            # address
            painter.drawText(addr_start, (i+1)*charh, "{:08x}".format(address))

            # hex data
            for j, byte in enumerate(data):
                self.paintHex(painter, i, j)
                self.paintAscii(painter, i, j)
                #painter.drawText(data_start + j*charw3, (i+1)*charh, "{:02x}".format(ord(byte)))

            # ascii data
            #for j, char in enumerate(data):
            #painter.drawText(code_start, (i+1)*charh, ascii)
        painter.setPen(Qt.gray)
        painter.drawLine(data_start-charw, 0, data_start-charw, self.height())
        painter.drawLine(code_start-charw, 0, code_start-charw, self.height())

        if self.blink and self.cursorRect().top() < self.height() and self.cursorRect().bottom() > 0:
            painter.fillRect(self.cursorRect(), Qt.black)
            painter.fillRect(self.cursorRect2(), Qt.black)
        duration = time.time()-start
        if duration > 0.02:
            print "painting took: ", duration, 's'

    def keyPressEvent(self, event):
        key = event.key()
        mod = event.modifiers()
        text = event.text()
        hexalpha = "0123456789abcdef"
        if key == Qt.Key_Right:
            if mod & Qt.ShiftModifier:
                if not self.selection.active:
                    self.selection.start = self.cursor.address
                    self.selection.active = True
                self.selection.end = self.cursor.address
            self.cursor.right()
        elif key == Qt.Key_Left:
            self.cursor.left()
        elif key == Qt.Key_Up:
            self.cursor.rewind(self.bpl)
        elif key == Qt.Key_Down:
            self.cursor.forward(self.bpl)
        elif key in [Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt]:
            pass
        elif text in hexalpha:
            oldbyte = ord(self.data[self.cursor.address])
            if self.cursor.nibble == 1:
                byte = (oldbyte & 0xf0) | hexalpha.index(text)
            else:
                byte = (oldbyte & 0x0f) | (hexalpha.index(text) << 4)
            self.data[self.cursor.address] = chr(byte)
            self.cursor.right()

        self.viewport().update()


class Analyzer(QLabel):
    def __init__(self, parent = None, hexview = None):
        super(Analyzer, self).__init__(parent)
        self.hexview = hexview
        self.hexview.cursor.changed.connect(self.read_numbers)
        self.hexview.selectionChanged.connect(self.read_numbers)
        self.string = ""

    def read_numbers(self):
        self.string = "{}\n{}".format(ord(self.hexview.getBytes()),
                                      len(self.hexview.selection))
        self.setText(self.string)

class StructEditor(QWidget):
    def __init__(self, hv=None, parent=None):
        super(StructEditor, self).__init__(parent)

class Delegate(QItemDelegate):
    def __init__(self):
        super(Delegate, self).__init__()
        self.validator = QIntValidator()

    def setModelData(self, editor, model, index):
        print editor, model, index
        editor = QLineEdit(editor)
        editor.setValidator(self.validator)
        super(Delegate, self).setModelData(editor, model, index)


class HexEditor(QMainWindow):
    def __init__(self):
        super(HexEditor, self).__init__()

        self.hexview = HexView()
        self.setCentralWidget(self.hexview)

        a = Analyzer(hexview=self.hexview)
        self.font = QFont("Courier", 10)



        # make struct editor widget
        self.structeditor = QTextEdit()
        # qscintilla compatibility
        self.structeditor.text = self.structeditor.toPlainText
        self.structeditor.setText = self.structeditor.setPlainText

        self.structeditor.setFont(self.font)

        self.dock1 = QDockWidget()
        self.dock1.setWindowTitle("Struct Editor")
        self.dock1.setWidget(self.structeditor)
        self.dock1.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock1)



        # make struct explorer widget
        self.structexplorer = s = QTreeWidget()
        s.setColumnCount(3)
        s.setHeaderLabels(["Name","Value","Color"])
        s.setItemsExpandable(True)
        self.d = Delegate()
        s.setItemDelegateForColumn(1, self.d)

        self.dock2 = QDockWidget()
        self.dock2.setWindowTitle("Struct Explorer")
        self.dock2.setWidget(self.structexplorer)
        self.dock2.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock2)

        self.hexview.cursor.changed.connect(self.eval)
        self.set_example_data()
        self.createActions()
        self.createMenus()

    def open_file(self):
        self.filename = QFileDialog.getOpenFileName(self, "Open File...")[0]
        #print self.filename
        if self.filename:
            size = os.stat(self.filename).st_size
            self.hexview.data = mmap.mmap(-1, size)
            self.hexview.data[:] = open(self.filename, 'rb').read()

    def createActions(self):
        self.act_open = QAction("&Open", self)
        self.act_open.setShortcuts(QKeySequence.Open)
        self.act_open.setStatusTip("Open file")
        self.act_open.triggered.connect(self.open_file)

        self.act_quit = QAction("&Quit", self)
        self.act_quit.setShortcuts(QKeySequence.Quit)
        self.act_quit.setStatusTip("Quit file")
        self.act_quit.triggered.connect(self.close)



    def createMenus(self):
        self.filemenu = self.menuBar().addMenu("&File")
        self.filemenu.addAction(self.act_open)
        self.filemenu.addAction(self.act_quit)

    def reset(self):
        self.hexview.highlights = []
        self.hexview.viewport().update()

    def foo(self, x):
        try:
            y = ("\n" + self.structeditor.text()).index("\n" + x)
        except:
            print x
            raise
        return y

    def eval(self):
        try:
            self.structexplorer.clear()
            self.items = []
            ns = {}
            exec(compile("from construct import *\n" + self.structeditor.text(), '<none>', 'exec'), ns)
            results = []
            import construct
            keys = sorted([x for x, v in ns.iteritems() if isinstance(v, construct.Construct) and x not in dir(construct) and (not x.startswith('_'))],
                          key=self.foo)
            for name in keys:
                cons = ns[name]
                try:
                    parsed = cons.parse(self.hexview.data[self.hexview.cursor.address:])
                except:
                    parsed = "<parse error>"
                if isinstance(parsed, construct.lib.container.Container):
                    self.items.append(QTreeWidgetItem(self.structexplorer,
                                                      [cons.name,
                                                       'Container',
                                                       "none"]))
                    parent = self.items[-1]
                    parent.setExpanded(True)
                    for k, v in parsed.iteritems():
                        it = QTreeWidgetItem(parent, [k, str(v), 'none'])
                        it.setFlags(it.flags() | Qt.ItemIsEditable)
                        self.items.append(it)
                else:
                    it = QTreeWidgetItem(self.structexplorer,
                                                      [cons.name,
                                                       str(parsed),
                                                       "none"])
                    self.items.append(it)
            for i in range(3):
                self.structexplorer.resizeColumnToContents(i)


#            self.hexview.viewport().update()
        except Exception as e:
            print e

    def set_example_data(self):
        self.hexview.highlights.append(Selection(10,20))
        self.structeditor.setText("""foo = Union("default data types",
    ULInt8("uint8"),
    ULInt16("uint16"),
    ULInt32("uint32"),
    ULInt64("uint64"),
    SLInt8("sint8"),
    SLInt16("sint16"),
    SLInt32("sint32"),
    SLInt64("sint64"),
    LFloat32("float"),
    LFloat64("double"),
)
bar = Union("data types (big endian)",
    UBInt8("uint8"),
    UBInt16("uint16"),
    UBInt32("uint32"),
    UBInt64("uint64"),
    SBInt8("sint8"),
    SBInt16("sint16"),
    SBInt32("sint32"),
    SBInt64("sint64"),
    BFloat32("float"),
    BFloat64("double"),
)
    """)
        self.eval()




if __name__ == '__main__':
    app = QApplication([])
    h = HexEditor()
    h.show()
    app.exec_()
