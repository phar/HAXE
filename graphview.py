from PySide.QtCore import *
from PySide.QtGui import *
from math import *
from Queue import PriorityQueue


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
        self.pen = QPen(Qt.black, 0)
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
        self.path = QPainterPath()

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
        return self.scene().sceneRect()

    def route_astar(self):

        src = self.source()
        dst = self.dest()
        s = self.scene()
        nodes = [x for x in s.items() if isinstance(x, GraphNodeItem)]
        cl = 20 # clearance
        borders = [x.boundingRect() #.adjusted(-cl,-cl,cl,cl)
                   for x in nodes]

        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __hash__(self):
                return self.x * 1000000 + self.y

            def q(self):
                return QPointF(self.x, self.y)

            def __eq__(self, other):
                return self.x == other.x and self.y == other.y

            def __repr__(self):
                return "Point({}, {}) @ {}".format(self.x, self.y, hex(id(self)))

            def __sub__(self, other):
                return Point(self.x - other.x, self.y - other.y)

            def __len__(self):
                return abs(self.x) + abs(self.y)

        start = Point(int(src.x()/cl)*cl, int(src.y()/cl)*cl+2*cl)
        goal = Point(int(dst.x()/cl)*cl, int(dst.y()/cl)*cl-2*cl)

        def neighbors(node):
            x = node.x
            y = node.y
            candidates = [(x - cl, y),
                          (x + cl, y),
                          (x, y-cl),
                          (x, y+cl),
                          # (x - cl, y - cl),
                          # (x - cl, y + cl),
                          # (x + cl, y - cl),
                          # (x + cl, y + cl),
            ]
            candidates = [Point(*x) for x in candidates if
                          self.scene().sceneRect().contains(x[0], x[1])]
            return candidates

        def cost(cur, nxt, prev):
            return (len(cur-nxt)
                    + (cl*5 if any([b.contains(nxt.q()) for b in borders]) else 0)
                    + abs(nxt.y - cur.y) * 0.5)


        def heuristic(goal, next):
            return len(goal - next)

        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        previous = start

        i = 0
        while not frontier.empty():
            current = frontier.get()[1]

            if current == goal:
                break

            i += 1
            for next in neighbors(current):
                new_cost = cost_so_far[current] + cost(current, next, previous)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    #print priority
                    frontier.put((priority, next))
                    came_from[next] = current
                    previous = current

        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()



        self.path = QPainterPath()

        self.path.moveTo(path[0].q())
        for pos in path[1:]:
            self.path.lineTo(pos.q())


    def route(self):
        self.path = QPainterPath()
        self.path.moveTo(self.source())
        self.path.lineTo(self.dest())



    def paint(self, painter, style, widget):
        self.route()

        width = 4 if self.isSelected() else 0
        painter.setPen(QPen(QColor(0,255,255) if self.highlighted else self.color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.drawPath(self.path)
#         lines.append(QLineF(first, point2))
# #        lines.append(QLineF(point2, point3))
# #        lines.append(QLineF(point3, point_3))
# #        lines.append(QLineF(point_3, point_2))
# #        lines.append(QLineF(point_2, last))
#         lines.append(QLineF(point2, last))

#         for line in lines:
#             painter.drawLine(line)

#         self.lines = lines

#         angle = acos(line.dx() / line.length())
#         if line.dy() >= 0:
#             angle = 2*pi - angle
#         arrow_p1 = last + QPointF(sin(angle - pi/3) * self.arrowsize,
#                                          cos(angle - pi/3) * self.arrowsize)
#         arrow_p2 = last + QPointF(sin(angle - pi + pi/3) * self.arrowsize,
#                                          cos(angle - pi + pi/3) * self.arrowsize)
#         painter.drawPolygon(QPolygonF([self.dest(), arrow_p1, arrow_p2]))

#         minx = min(arrow_p1.x(), arrow_p2.x())
#         maxx = max(arrow_p1.x(), arrow_p2.x())
#         miny = min(arrow_p1.y(), arrow_p2.y())
#         maxy = max(arrow_p1.y(), arrow_p2.y())
#         for line in lines:
#             minx = min(minx, line.x1(), line.x2())
#             maxx = max(maxx, line.x1(), line.x2())
#             miny = min(miny, line.y1(), line.y2())
#             maxy = max(maxy, line.y1(), line.y2())

#         self.bound = QRectF(minx, miny, maxx-minx, maxy-miny)
        painter.setRenderHint(QPainter.Antialiasing, False)

class MainView(QGraphicsView):
    resized = Signal()
    def __init__(self, scene=None):
        super(MainView, self).__init__(scene)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        #        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.horizontalScrollBar().setValue(0)
        self.verticalScrollBar().setValue(0)

    def resizeEvent(self, event):
        self.resized.emit()

class PreView(QGraphicsView):
    def __init__(self, scene=None, parent=None, selector=None):
        super(PreView, self).__init__(scene, parent)
        self.selector = selector
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sr = self.scene().sceneRect()
        self.setFixedSize(int(sr.width() *0.1), int(sr.height() * 0.1) )
        self.setDragMode(QGraphicsView.RubberBandDrag)
#        self.setAcceptHoverEvents(True)
        viewsize = self.size()
        srect = self.scene().sceneRect()
        self.resetTransform()
        self.scale(viewsize.width() / (srect.width() + 10),
                   viewsize.height() / (srect.height() + 10))
        self.update()

        parent.resized.connect(self.update)


    def enterEvent(self, event):
        if self.selector:
            self.selector.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.selector.setFlag(QGraphicsItem.ItemIsMovable, True)

    def leaveEvent(self, event):
        if self.selector:
            self.selector.setFlag(QGraphicsItem.ItemIsSelectable, False)
            self.selector.setFlag(QGraphicsItem.ItemIsMovable, False)

    def update(self):
        self.setGeometry(self.parent().size().width() - self.size().width(),
                         self.parent().size().height() - self.size().height(),
                         self.size().width(),
                         self.size().height())


class Selector(QGraphicsRectItem):
    def __init__(self, view, x=0,y=0,w=320,h=240):
        super(Selector, self).__init__(x,y,w,h)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        self.view = view
        self.view.resized.connect(self.update)
        self.view.horizontalScrollBar().valueChanged.connect(self.update)
        self.view.verticalScrollBar().valueChanged.connect(self.update)
        # self.setBrush(QBrush(Qt.blue))
        self.setOpacity(1)
        self.updating = False
        self.update()

    def update(self, *ignored):
        if not self.updating:
            self.setRect(QRectF(QPointF(self.view.horizontalScrollBar().sliderPosition(),
                                        self.view.verticalScrollBar().sliderPosition()),
                                self.view.size()))
        #self.view.fitInView(self)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            #print self.boundingRect()
            self.updating = True
            self.view.horizontalScrollBar().setValue(self.mapRectToScene(self.boundingRect()).left())
            self.view.verticalScrollBar().setValue(self.mapRectToScene(self.boundingRect()).top())
            self.updating = False
            return value
        return super(Selector,self).itemChange(change, value)

    def mouseMoveEvent(self, event):#
        vec = event.scenePos() - event.lastScenePos()
        print self.pos(), vec
        self.moveBy(vec.x(), vec.y())
        if self.x() < 0:
            self.setPos(0, self.y())
        elif self.x() > 640 - self.rect().width():
            self.setPos(640 - self.rect().width(), self.y())

        if self.y() < 0:
            self.setPos(self.x(), 0)
        elif self.y() > 1200 - self.rect().height():
            self.setPos(self.x(), 1200 - self.rect().height())


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
        h.setMinimumWidth(24)

        self.mainview = view1 = MainView(scene)
        view1.setSceneRect(0,0,640,1200)
        self.s = s = Selector(view1)
        scene.addItem(s)
        view1.horizontalScrollBar().setValue(0)
        view1.verticalScrollBar().setValue(0)

        self.setWindowTitle("Ida View")
        self.preview = view2 = PreView(scene, view1, s)

        self.button = b = QPushButton("Do Stuff")
        self.button.clicked.connect(self.layout_graph)
        b.setMinimumWidth(24)

        l.addWidget(view1, 0, 0, 3, 3)
#        l.addWidget(view2, 2, 2, 2, 3)
        l.addWidget(b, 2, 3)
        l.addWidget(h, 3, 3)
        l.setColumnStretch(0, 1)
        l.setColumnStretch(3, 0)
        self.populate()


    def layout_graph(self):
        pass

    def populate(self):
        self.nodes = nodes = []
        self.edges = edges = []
        scene = self.scene
        for i in range(3):
            nodes.append(GraphNodeItem(QTextEdit("<b>xor eax, eax<br>ret</b>"), "", 300, 100 + i*300))
            scene.addItem(nodes[-1])



        edges.append(GraphEdgeItem(nodes[2], nodes[0]))
        # edges.append(GraphEdgeItem(nodes[0], nodes[2]))
        # edges.append(GraphEdgeItem(nodes[2], nodes[3]))
        # edges.append(GraphEdgeItem(nodes[1], nodes[2]))
        # edges.append(GraphEdgeItem(nodes[3], nodes[1]))
        # edges.append(GraphEdgeItem(nodes[4], nodes[0]))
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
