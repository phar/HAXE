from PyQt4.QtCore import *
from PyQt4.QtGui import *

from binascii import *
import sys
sys.path.append('/home/csar')
from libpy.misc import by


class Hex(QDialog):
    def __init__(self, data="\x00\x01\x02\x03", parent=None):
        super(Hex, self).__init__(parent)
        self.data = open('qthexedit.py','rb').read()
        l = QGridLayout()

        self.address = QListWidget(self)
        self.dataview = QTextEdit(self)
        self.interpview = QTextEdit(self)

        self.address.setFixedWidth(128)
        self.address.setVerticalScrollBarPolicy(1)
        self.address.setHorizontalScrollBarPolicy(1)
        self.dataview.setVerticalScrollBarPolicy(1)

        for view in [self.dataview, self.interpview]:
            #            view.setWordWrapMode(0)
            view.setLineWrapMode(3) # fixedcolumnwidth
            view.setFontFamily("Courier")
            view.setHorizontalScrollBarPolicy(1)
            #view.setCursorWidth()
            view.ensureCursorVisible()

        self.dataview.setLineWrapColumnOrWidth(47)
        self.interpview.setLineWrapColumnOrWidth(16)

#        self.interpview.setWordWrapMode(0)


        l.addWidget(self.address, 0, 0)
        l.addWidget(self.dataview, 0, 1)
        l.addWidget(self.interpview, 0, 2)

        l.setColumnMinimumWidth(0, 64)
        l.setColumnMinimumWidth(1, 256)
        l.setColumnMinimumWidth(2, 128)
        l.setColumnStretch(0, 0)
        l.setColumnStretch(1, 2)
        l.setColumnStretch(2, 1)
        self.setLayout(l)
        self.scroll1 = self.address.verticalScrollBar()
        self.scroll2 = self.dataview.verticalScrollBar()
        self.scroll = self.interpview.verticalScrollBar()
        self.populate()

        self.connect(self.scroll, SIGNAL("actionTriggered(int)"),
                      self.sync_scroll)
        self.connect(self.scroll2, SIGNAL("actionTriggered(int)"),
                      self.sync_scroll2)

        self.connect(self.dataview, SIGNAL("cursorPositionChanged()"),
                     self.sync_cursor)
        self.connect(self.interpview, SIGNAL("cursorPositionChanged()"),
                     self.sync_cursor2)


    def populate(self):
        import re
        hex_text = " ".join(by(hexlify(self.data), 2))
        int_text = re.sub(r'[^a-zA-Z0-9]','.', self.data) #"\n".join(by(re.sub(r'[^a-zA-Z0-9]','.', self.data), 16))
        self.interpview.setText(int_text)
        self.dataview.setText(hex_text)

    def sync_cursor(self):
        pos = self.dataview.textCursor().position()
        self.interpview.moveCursor(pos)

    def sync_cursor2(self):
        pos = self.interpview.textCursor().position()
        self.dataview.moveCursor(pos)

    def sync_scroll(self):
        val = self.scroll.value()
        self.scroll2.setValue(val)


    def sync_scroll2(self):
        val = self.scroll2.value()
        self.scroll.setValue(val)

    # def sync_content_interp(self):
    #     new_text = self.interpview.toPlainText()
    #     hex_text = []
    #     for line in new_text.split('\n'):
    #         hex_text.append(hexlify(bytes(line)))
    #     self.dataview.setText("\n".join(hex_text))
    #     lines = new_text.count('\n') + 1
#        self.address.addItems(["0x%08x" % i for i in range(lines)])

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet("QTextEdit { border: 0px solid black };")
    h = Hex()
    h.show()

    app.exec_()
