from PySide.QtCore import *
from PySide.QtGui import *
from construct import *
from math import *

class TreeNode(object):
    def __init__(self, value, row, parent, cons, name=""):
        self.value = value
        self.row = row
        self.parent = parent
        self.name = name
        self.cons = cons

class ConstructModel(QAbstractItemModel):
    def __init__(self, cons, buf):
        super(ConstructModel, self).__init__()
        self.cons = cons
        self.buf = buf
        self.root = TreeNode(None,0,None, None)
        self.parsed = TreeNode(cons.parse(buf), 0, self.root, self.cons,self.cons.name)
        self.parents = {}

    def columnCount(self, parent):
        return 3

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
                child = TreeNode(v, row, item, item.cons.subcons[row], k)
            elif isinstance(item.value, list):
                child = TreeNode(item.value[row], row, item, item.cons.subcon,  "{}[{}]".format(item.name,row))
            elif item == self.root:
                child = self.parsed
            else:
                return QModelIndex()
            self.parents[(id(item), row, column)] = child
            return self.createIndex(row,column,child)
        return QModelIndex()


    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 1 and not isinstance(index.internalPointer().value, (dict, list)) :
            return super(ConstructModel,self).flags(index) | Qt.ItemIsEditable
        return super(ConstructModel,self).flags(index)


    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            try:
                item = index.internalPointer()
                parent = item.parent
                row = index.row()
                if isinstance(parent.value, dict):
                    key = parent.value.items()[row][0]
                    print key
                elif isinstance(parent.value, list):
                    key = row
                else:
                    return False
                safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh',
                             'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot',
                             'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians', 'sin',
                             'sinh', 'sqrt', 'tan', 'tanh', 'abs','int','float','sum','max','min'] #use the list to filter the local namespace
                safe_dict = dict([ (k, globals().get(k, None)) for k in safe_list ]) #add any needed builtins back in.
                safe_dict[parent.name] = parent.value
                #import pdb;pdb.set_trace()
                val = eval(value, {"__builtins__": None}, safe_dict)
                try:
                    item.cons.build(val)
                except:
                    return False
                parent.value[key] = item.value = val
                self.buf[:] = self.cons.build(self.parsed.value)
                print self.buf[:].__repr__()
                self.dataChanged.emit(index, index)
            except Exception as e:
                print e
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
            else:
                if isinstance(item.value, dict):
                    return "<Struct>"
                elif isinstance(item.value, list):
                    return "<Array>"
                else:
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
        self.expandAll()

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
