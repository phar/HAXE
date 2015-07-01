from PySide.QtGui import *
from PySide.QtCore import *
from binascii import *
import time
from math import *



class HexCoder:
    def __init__(self, data, bytes_per_line=16):
        self.data = data
        self.bpl = bytes_per_line

    def getLine(self, pos=0):
        return (pos, self.bpl, self.data[pos:pos+self.bpl])


    def getLines(self, pos=0):
        while pos < len(self.data)-self.bpl:
            yield (pos, self.bpl, self.data[pos:pos+self.bpl])
            pos += self.bpl
        yield (pos, len(self.data)-pos, self.data[pos:])

    def maxWidth(self):
        return self.bpl * 3 - 1

    def numLines(self):
        return int(ceil(float(len(self.data))/ self.bpl))

class HexView(QAbstractScrollArea):
    def __init__(self, parent=None, coder=HexCoder, data="foobar"*2000):
        super(HexView, self).__init__(parent)
        self.data = data
        self.coder = coder(data)
        self.setFont(QFont("Courier", 10))
        self.charWidth = self.fontMetrics().maxWidth()
        self.charHeight = self.fontMetrics().height()
        self.addr_width = 8
        self.adjust()


    def visibleColumns(self):
        ret = int(ceil(float(self.viewport().width())/self.charWidth))
        return ret

    def visibleLines(self):
        return int(ceil(float(self.viewport().height())/self.charHeight))

    def totalCharsPerLine(self):
        ret = self.coder.bpl * 4 + self.addr_width + 4
        return ret

    def adjust(self):
        self.horizontalScrollBar().setRange(0, self.totalCharsPerLine() - self.visibleColumns())
        self.horizontalScrollBar().setPageStep(self.visibleColumns())
        self.verticalScrollBar().setRange(0, self.coder.numLines() - self.visibleLines())
        self.verticalScrollBar().setPageStep(self.visibleLines())

    def resizeEvent(self, event):
        self.adjust()

    def paintEvent(self, event):
        start = time.time()
        painter = QPainter(self.viewport())
        palette = self.viewport().palette()
        charh = self.charHeight
        charw = self.charWidth
        charw3 = 3*charw
        data_width = self.coder.maxWidth()
        addr_width = self.addr_width
        addr_start = 1
        gap2 = 1
        gap3 = 2

        data_start = addr_start + addr_width + gap2
        code_start = data_start + data_width + gap3

        hs = self.horizontalScrollBar().value()
        addr_start -= hs
        code_start -= hs
        data_start -= hs

        addr_start *= charw
        data_start *= charw
        code_start *= charw


        for i, line in enumerate(self.coder.getLines(self.verticalScrollBar().value() * self.coder.bpl)):
            if i > self.visibleLines():
                break

            if i % 2 == 0:
                painter.fillRect(0, (i+1)*charh+4, self.viewport().width(), charh, QColor(240,240,240))
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

        painter.drawLine(data_start-charw, 0, data_start-charw, self.height())
        painter.drawLine(code_start-charw, 0, code_start-charw, self.height())
        print "painting took: ", time.time()-start, "s"


if __name__ == '__main__':
    app = QApplication([])
    h = HexView()
    h.setGeometry(-1870,32,800,600)
    h.show()
    app.exec_()
