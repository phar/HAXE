import sys
#sys.path.append(r'C:\Python27\Lib\site-packages')
from PySide.QtCore import *
from PySide.QtGui import *
from construct import *
from utils import *
import logging
#logging.basicConfig(level=logging.DEBUG)

import gc;gc.disable()
class ConstructItem(object):
    __metaclass__ = logged
    def __init__(self, data, parent=None):
        self.data = data
        self.parent = parent

    def childCount(self):
        if isinstance(self.data, (dict, list)):
            return len(self.data)
        return 0

    def child(self, i):
        try:
            if isinstance(self.data, dict):
                return ConstructItem(self.data.items()[i], self)
            elif isinstance(self.data, list):
                return ConstructItem(self.data[i], self)
        except:
            print "getting {} from {} failed".format(i, self.data)


    def parent(self):
        return self.parent

    def columnCount(self):
        if isinstance(self.data, (dict, list)):
            return 1
        return 2

    def data(self, col):
        if col == 1:
            return str(self.data)

class TreeNode(object):
    def __init__(self, value, row, parent, name=""):
        self.value = value
        self.row = row
        self.parent = parent
        self.name = name

class ConstructModel(QAbstractItemModel):
    #__metaclass__ = logged
    def __init__(self, cons, buf):
        super(ConstructModel, self).__init__()
        self.cons = cons
        self.buf = buf
        self.root = TreeNode(None,0,None)
        self.parsed = TreeNode(cons.parse(buf), 0, self.root)
        self.parents = {}

    def columnCount(self, parent):
        return 2

    def rowCount(self, parent):
        if parent.isValid():
            item = parent.internalPointer()
            if item == self.root:
                return 1
            elif isinstance(item.value, (dict, list)):
                return len(item.value)
            return 0
        else:
            return 1

    def index(self, row, column, item):
        if item.isValid():
            item = item.internalPointer()
        else:
            return self.createIndex(0,column,self.parsed)
        if (id(item), row, column) in self.parents:
            return self.createIndex(row, column,
                                    self.parents[(id(item), row, column)])
        else:
            if isinstance(item.value, dict):
                k, v  = item.value.items()[row]
                child = TreeNode(v, row, item, k)
            elif isinstance(item.value, list):
                child = TreeNode(item.value[row], row, item)
            elif item == self.root:
                child = self.parsed
            else:
                return QModelIndex()
            self.parents[(id(item), row, column)] = child
            return self.createIndex(row,column,child)
        return QModelIndex()

    def data(self, index, role):
        if role != Qt.DisplayRole:
            return
        if not index.isValid():
            return
        item = index.internalPointer()
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return str(item.name)
            else:
                if not isinstance(item.value, (dict, list)):
                    return str(item.value)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        item = index.internalPointer()
        if item == self.root:
            return QModelIndex()
        if item == self.parsed:
            return self.createIndex(0,0,self.root)
        else:
            return self.createIndex(item.row,0,item.parent)
        return QModelIndex()

class StructExplorer(QTreeView):
    def __init__(self, cons, data, parent=None):
        super(StructExplorer, self).__init__(parent)
        self.setItemsExpandable(True)
        self.model = ConstructModel(cons, data)
        self.setModel(self.model)

if __name__ == '__main__':
    app = QApplication([])
    import mmap
    data = mmap.mmap(-1, 16)
    cons = Struct("foo",
                  ULInt32("a"),
                  ULInt32("b"),
                  GreedyRange(Byte("c")))
    w = StructExplorer(cons, data)
    w.show()
    app.exec_()
