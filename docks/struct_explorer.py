from PySide.QtCore import *
from PySide.QtGui import *
from construct import *
from construct.adapters import *
from math import *
from binascii import *
#from ..mmapslice import *


def red(cons):
    cons.color = Qt.red
    return cons


class TreeNode(object):
    def __init__(self, value, row, parent, cons, name="", root=None):
        self.value = value
        self.row = row
        self.parent = parent
        self.name = name
        self.cons = cons
        self.root = root or self
        try:
            self.offset = self.parent.offset + self.parent.size_so_far
        except:
            self.offset = 0

        self.children = []

        if isinstance(parent, TreeNode):
#            try:
            parent.size_so_far += len(self.cons.build(self.value))
#            except:
#                parent.size_so_far += self.cons.size()
        self.size_so_far = 0

        if isinstance(self.value, dict): # struct
            for i, con in enumerate(self.cons.subcons):
                if isinstance(con, ConstAdapter):
                    self.children.append(TreeNode(con.value, i, self, con, con.name or "Magic", self.root))
                else:
                    self.children.append(TreeNode(self.value[con.name], i, self, con, con.name, self.root))

        elif isinstance(self.value, list):
            for i, v in enumerate(self.value):
                self.children.append(TreeNode(v, i, self, self.cons.subcon,
                                              "{}[{}]".format(self.name, i), self.root))


    def read_value(self, val):
        # if isinstance(self.value, Password):
        #     assert len(val) < 16
        #     return Password(val, self.value.length)
        if isinstance(self.value, (int, float)):
            return eval(val, globals(), {self.parent.name: self.parent.value})
        elif isinstance(self.value, str):
            return val
        else:
            raise Exception('dont know how to read for a value of %s', self.value)


    def editable(self):
        if isinstance(self.cons, ConstAdapter):
            return False
        if isinstance(self.value, (dict, list)):
            return False
        return True

    def size(self):
        return len(self.cons.build(self.value))


class ConstructModel(QAbstractItemModel):
    def __init__(self, *children):
        super(ConstructModel, self).__init__()
        self.root = TreeNode(None,0,None, None)
        for child in children:
            self.root.children.append(child)
        #self.setRootIndex

    def columnCount(self, parent):
        return 4

    def rowCount(self, parent):
        if parent.row() == -1 and parent.column() == -1:
            return len(self.root.children)
        if parent.isValid():
            item = parent.internalPointer()
            return len(item.children)


    def index(self, row, column, item):
        if item.isValid():
            item = item.internalPointer()
        elif len(self.root.children) == 0:
            return QModelIndex()
        else:
            return self.createIndex(row,column,self.root.children[row])

        return self.createIndex(row, column, item.children[row])

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 1 and index.internalPointer().editable():
            return super(ConstructModel,self).flags(index) | Qt.ItemIsEditable
        return super(ConstructModel,self).flags(index)


    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            try:
                item = index.internalPointer()
                parent = item.parent
                row = index.row()
                if isinstance(parent.value, dict):
                    key = item.name
                    print key
                elif isinstance(parent.value, list):
                    key = row
                else:
                    return False
                val = item.read_value(value)
                try:
                    # build and reparse, else item.value might be float when the cons is int
                    parent.value[key] = item.value = item.cons.parse(item.cons.build(val))
                except:
                    return False
                data = item.root.cons.build(item.root.value)
                self.item.buf[:len(data)] = data
                print self.buf[:len(data)].__repr__()
                self.dataChanged.emit(index, index)
            except Exception as e:
                raise
        return False

    def data(self, index, role):
        if role not in (Qt.DisplayRole, Qt.EditRole):
            return
        if not index.isValid():
            return
        item = index.internalPointer()
        if role in (Qt.DisplayRole, Qt.EditRole):
            if index.column() == 0:
                return str(item.name)
            elif index.column() == 1:
                if isinstance(item.value, dict):
                    return "<Struct>"
                elif isinstance(item.value, list):
                    return "<Array>"
                else:
                    return str(item.value)
            elif index.column() == 2:
                return hex(item.offset)
            else:
                return hex(item.size())

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return
        if orientation == Qt.Horizontal:
            return ['Name', 'Value','Offset','Size'][section]

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        item = index.internalPointer()
        if item == self.root:
            return QModelIndex()
        return self.createIndex(item.row,0,item.parent)


    def add_tree(self, tree):
        self.beginInsertRows(self.index(0,0, QModelIndex()),
                             len(self.root.children),
                             len(self.root.children))
        self.root.children.append(tree)
        tree.parent = self.root
        self.endInsertRows()



    def rm_tree(self, int_index):
        self.beginRemoveRows(self.index(0,0, QModelIndex()),
                             int_index,
                             int_index)
        del self.root.children[int_index]
        self.endRemoveRows()

    def clear(self):
        self.root.children = []
        self.reset()


class StructExplorer(QWidget):
    def __init__(self, *roots):
        super(StructExplorer, self).__init__(None)
        self.tv = tv = QTreeView()
        self.roots = roots
        self.model = ConstructModel()
        tv.setItemsExpandable(True)
        tv.setModel(self.model)
        tv.expandAll()
        self.layout = l = QGridLayout()
        self.setLayout(l)
        self.setMinimumWidth(500)
        l.addWidget(tv, 0, 0, 1, 4)
        self.button = b = QPushButton("ok")
        self.button.clicked.connect(self.klick)
        l.addWidget(b, 1, 0)
        self.label = QLabel("")
        l.addWidget(self.label, 1, 1)
        self.b2 = QPushButton("clear")
        self.b2.clicked.connect(self.klock)
        l.addWidget(self.b2, 1, 2)
        self.sm = self.tv.selectionModel()
        self.sm.currentRowChanged.connect(self.updatelabel)
        self.model.dataChanged.connect(self.updatelabel)
        self.i = 0

    def updatelabel(self, current, previous):
        item = current.internalPointer()
        if isinstance(item, TreeNode):
            self.label.setText(hexlify(item.cons.build(item.value)))
        #self.data[item.offset,item.offset+item.size()])


    def klick(self):
        self.model.add_tree(self.roots[self.i % len(self.roots)])
        self.i += 1

    def klock(self):
        self.model.clear()


if __name__ == '__main__':
    app = QApplication([])
    import mmap
    content = "\x05hello\x08world!!!"
    data = mmap.mmap(-1, len(content))
    data[:] = content
    cons = Struct("foo",
                  PascalString("first"),
                  PascalString("second"))
    root1 = TreeNode(cons.parse(data), 0, None, cons, cons.name)
    root2 = TreeNode(cons.parse(data), 0, None, cons, cons.name)
    root3 = TreeNode(cons.parse(data), 0, None, cons, cons.name)
    root4 = TreeNode(cons.parse(data), 0, None, cons, cons.name)
    w = StructExplorer(root1, root2, root3, root4)
    w.show()
    app.exec_()
