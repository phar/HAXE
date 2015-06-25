from PySide.QtCore import *
from PySide.QtGui import *
from math import *

class NameDialog(QDialog):
    def __init__(self, node):
        super(NameDialog,self).__init__()
        self.setWindowTitle("Change Node Name...")
        self.node = node
        self.lyt = l = QGridLayout()
        self.setLayout(l)
        self.text = t = QLineEdit(node.title.toPlainText())
        self.ok_b = o = QPushButton("Ok")
        o.clicked.connect(self.ok)
        l.addWidget(t, 0, 0)
        l.addWidget(o, 1, 0)

    def ok(self):
        self.node.title.setPlainText(self.text.text())
        self.close()


class GraphicsButton(QGraphicsTextItem):
    clicked = Signal()
    def mousePressEvent(self, event):
        self.clicked.emit()

class GraphNodeItem(QGraphicsRectItem):
    def __init__(self, child, title="title", x=100,y=100,width=100,height=100):
        super(GraphNodeItem, self).__init__(x, y, width, height+24)
        self.title = QGraphicsTextItem(title, self)
        self.title_font = QFont("Courier")
        self.title_font.setBold(True)
        self.title.setFont(self.title_font)
        self.setOpacity(1)
        self.setBrush(QBrush(Qt.white))
        self.pen = QPen(Qt.black)
        self.pen.setWidth(0)
        self.setPen(self.pen)
        self.p1 = QGraphicsProxyWidget(self)
        # self.p2 = QGraphicsProxyWidget(self)
        self.p2 = GraphicsButton("N", self)
        self.p2.setFont(self.title_font)
        self.child = child
        child.setStyleSheet("QWidget { border: 1px solid black; };")
        self.child.resize(width+1, height+1)
        self.p1.setWidget(child)
        # self.pb = QPushButton("N")
        # self.pb.setMinimumWidth(22)
        # self.pb.setMinimumHeight(22)
        # self.pb.resize(22,22)
        # self.p2.setWidget(self.pb)
        self.p2.clicked.connect(self.edit)
        self.title.setPos(x,y)
        self.p2.setPos(x+width-22, y)
        self.p1.setPos(x, y+24)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.setAcceptHoverEvents(True)
        self.edges = []

    def edit(self):
        self.n = NameDialog(self)
        self.n.show()

    def remove(self):
        for e in self.edges:
            e.remove()
        self.scene().removeItem(self)

    def hoverEnterEvent(self, event):
        for e in self.edges:
            e.highlighted = True
            e.update()
        self.setZValue(2)
        self.update()

    def hoverLeaveEvent(self, event):
        for e in self.edges:
            e.highlighted = False
            e.update()
        self.setZValue(0)
        self.update()

    def get_arrow_source(self):
        p1 = self.boundingRect().bottomRight()
        p2 = self.boundingRect().bottomLeft()
        return self.mapToScene(0.5*(p1.x() + p2.x()), 0.5*(p1.y() + p2.y()))

    def get_arrow_dest(self):
        p1 = self.boundingRect().topRight()
        p2 = self.boundingRect().topLeft()
        return self.mapToScene(0.5*(p1.x() + p2.x()), 0.5*(p1.y() + p2.y()))


    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for edge in self.edges:
                edge.update()
        QGraphicsItem.itemChange(self,change,value)
        return value

    def paint(self, painter, style, widget):
        if self.isSelected():
            self.setBrush(QBrush(Qt.gray))
        else:
            self.setBrush(QBrush(Qt.white))

        # don't draw selection border
        style.state &= ~ QStyle.State_Selected
        super(GraphNodeItem, self).paint(painter, style, widget)

class GraphEdgeItem(QGraphicsItem):
    def __init__(self, src, dst):
        super(GraphEdgeItem, self).__init__()
        #self.setRenderHints(QPainter.Antialiasing)
        self.src = src
        self.dst = dst
        self.src.edges.append(self)
        self.dst.edges.append(self)
        self.setOpacity(1)
        #self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.update()
        self.color = Qt.green
        self.highlighted = False
        self.arrowsize = 8
        self.setZValue(-1)
        self.bound = QRectF(0,0,1000,1000)

    def source(self):
        return self.src.get_arrow_source()

    def dest(self):
        return self.dst.get_arrow_dest()

    def remove(self):
        self.scene().removeItem(self)
        self.src.edges.remove(self)
        self.dst.edges.remove(self)
        del(self)

    def boundingRect(self):
        return self.bound

    def paint(self, painter, style, widget):
        first = self.source()
        last = self.dest()
        lines = []
        width = 4 if self.isSelected() else 2
        painter.setPen(QPen(QColor(0,255,255) if self.highlighted else self.color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        point2 = QPointF(first.x(), first.y() + 10)
        point_2 = QPointF(last.x(), last.y() - 10)
        lines.append(QLineF(first, point2))
        point3 = QPointF(point2.x()+100,point2.y())
        point_3 = QPointF(point2.x()+100,point_2.y())
        lines.append(QLineF(point2, point3))
        lines.append(QLineF(point3, point_3))
        lines.append(QLineF(point_3, point_2))
        lines.append(QLineF(point_2, last))


        for line in lines:
            painter.drawLine(line)

        self.lines = lines

        angle = acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = 2*pi - angle
        arrow_p1 = last + QPointF(sin(angle - pi/3) * self.arrowsize,
                                         cos(angle - pi/3) * self.arrowsize)
        arrow_p2 = last + QPointF(sin(angle - pi + pi/3) * self.arrowsize,
                                         cos(angle - pi + pi/3) * self.arrowsize)
        painter.drawPolygon(QPolygonF([self.dest(), arrow_p1, arrow_p2]))

        minx = min(arrow_p1.x(), arrow_p2.x())
        maxx = max(arrow_p1.x(), arrow_p2.x())
        miny = min(arrow_p1.y(), arrow_p2.y())
        maxy = max(arrow_p1.y(), arrow_p2.y())
        for line in lines:
            minx = min(minx, line.x1(), line.x2())
            maxx = max(maxx, line.x1(), line.x2())
            miny = min(miny, line.y1(), line.y2())
            maxy = max(maxy, line.y1(), line.y2())

        self.bound = QRectF(minx, miny, maxx-minx, maxy-miny)


class MainView(QGraphicsView):
    def __init__(self, scene=None):
        super(MainView, self).__init__(scene)
#        self.setRenderHints(QPainter.Antialiasing)

class PreView(QGraphicsView):
    def __init__(self, scene=None):
        super(PreView, self).__init__(scene)
        self.scale(0.2, 0.2)



class Selector(QGraphicsRectItem):
    def __init__(self, view, x=0,y=0,w=320,h=240):
        super(Selector, self).__init__(x,y,w,h)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.view = view
        self.setBrush(QBrush(Qt.blue))
        self.setOpacity(0.5)
        self.setPos(10,10)


    def itemChange(self, change, value):
         if change == QGraphicsItem.ItemPositionChange:
             print self.boundingRect()
             view.setSceneRect(self.mapToScene(self.boundingRect()))


class HexWidget(QWidget):
    def __init__(self):
        super(HexWidget, self).__init__()
        self.data = "abcd"
        self.setMinimumSize(20,20)

    def paintEvent(self, event):
        p = QPainter(self)
        p.drawText(5, 20, "00")


class Ida(QWidget):
    def __init__(self):
        super(Ida, self).__init__()
        self.layout = l = QGridLayout()
        self.setLayout(l)

        self.scene = scene = QGraphicsScene()
        scene.setSceneRect(QRectF(0, 0, 640, 1200))
        self.hex = h = HexWidget()

        self.mainview = view1 = MainView(scene)

        self.s = s = Selector(view1)
        scene.addItem(s)


        view1.setWindowTitle("Ida View")
        view1.show()
        self.preview = view2 = PreView(scene)
        view2.show()

        self.button = b = QPushButton("Do Stuff")
        self.button.clicked.connect(self.layout_graph)

        l.addWidget(view1, 0, 0, 3, 1)
        l.addWidget(view2, 0, 1, 2, 1)
        l.addWidget(b, 1, 1)
        l.addWidget(h, 2, 1)
        self.populate()

    def layout_graph(self):
        pass

    def populate(self):
        self.nodes = nodes = []
        self.edges = edges = []
        scene = self.scene
        for i in range(5):
            nodes.append(GraphNodeItem(QTextEdit("<b>foo</b>"), "", 300, i*200))
            scene.addItem(nodes[-1])



        edges.append(GraphEdgeItem(nodes[0], nodes[1]))
        edges.append(GraphEdgeItem(nodes[0], nodes[2]))
        edges.append(GraphEdgeItem(nodes[2], nodes[3]))
        edges.append(GraphEdgeItem(nodes[1], nodes[2]))
        edges.append(GraphEdgeItem(nodes[3], nodes[1]))
        edges.append(GraphEdgeItem(nodes[4], nodes[0]))
        for e in edges:
            scene.addItem(e)


app = QApplication([])
i = Ida()
i.show()
app.exec_()


"""
void Sticky::mousePressEvent(QGraphicsSceneMouseEvent *event) {
        if(sizeGripItem->contains(mapToItem(sizeGripItem, event->pos()))) {
                resizing = true;
        }

        QGraphicsItem::mousePressEvent(event);
    }

    void Sticky::mouseMoveEvent(QGraphicsSceneMouseEvent *event) {
        if(resizing) {
                setSize(QSize(event->pos().x(), event->pos().y()));
                emit(moved(this));
                update();
        }
        else {
                emit(moved(this));
                QGraphicsItem::mouseMoveEvent(event);
        }
    }

    void Sticky::mouseReleaseEvent(QGraphicsSceneMouseEvent *event) {
        if(resizing) {
                rect.setBottomRight(graphWidget->getNearestGridPoint(rect.bottomRight()));
                relayout();
                emit(moved(this));
                // hack to tell the canvas we're at a new size
                moveBy(1,1);
                moveBy(-1,-1);

                scene()->update();
        }
        resizing = false;
        QGraphicsItem::mouseReleaseEvent(event);
    }
"""
