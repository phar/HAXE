"""
Python reimplementation of ColumnsView class of KDE's hexeditor Okteta.
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *

DEFAULT_SINGLE_STEP = 20

class Range:
    def __init__(self, start, end):
        self._start = start
        self._end = end

    def __eq__(self, other):
        return isinstance(other, Range) and self._start == other.start and self._end == other.end

    def set(self, start, end=None):
        if isinstance(start, Range):
            self._start = start.start
            self._end = start.end
        else:
            self._start = start
            if end is not None:
                self._end = end

    def start(self):
        return self._start
    def end(self):
        return self._end

    def setStart(self, start):
        self._start = start

    def restrictTo(self, limit):
        if self._start < Limit.start:
            self._start = Limit.start
        if self._end > Limit.end:
            self._end = Limit.end

    def extendTo(self, limit):
        if self._start > Limit.start:
            self._start = Limit.start
        if self._end < Limit.end:
            self._end = Limit.end

    def moveStartBy(self, d):
        self._start +=d


    def moveEndBy(self, d):
        self._end +=d

    def moveBy(self, d):
        self._start +=d
        self._end +=d

    def includes(self, value):
        return self._start <= value and self._end >= value



class NumberRange(Range):
    def __init__(self, start, end, width=None):
        self._start = start
        if end:
            self._end = end
        else:
            self._end = start + width

    def startsBefore(self, value):
        return self._start < value

    def isValid(self):
        return self._start <= self._end

    @staticmethod
    def fromWidth(start, width):
        return NumberRange(start, None, width)

    def width(self):
        return self._end - self._start

class PixelXRange(NumberRange):
    pass

class PixelYRange(NumberRange):
    pass

class ColumnsViewPrivate:
    def __init__(self):
        self.NoOfLines = 0
        self.LineHeight = 0
        self.ColumnsWidth = 0
        self.Columns = []

    def updateWidths(self):
        self.columnsWidth = 0
        for col in self.columns:
            col.setX(self.columnsWidth)
            self.columnsWidth += col.visibleWidth()


class ColumnsView(QAbstractScrollArea):
    def __init__(self, parent=None):
        super(ColumnsView, self).__init__(parent)
        self.viewport().setAttribute(Qt.WA_StaticContents)
        self.viewport().setBackgroundRole(QPalette.Base)
        self.horizontalScrollBar().setSingleStep(DEFAULT_SINGLE_STEP)
        self.verticalScrollBar().setSingleStep(DEFAULT_SINGLE_STEP)
        self.viewport().setFocusProxy(self)
        self.viewport().setFocusPolicy(Qt.WheelFocus)
        self.d = ColumnsViewPrivate()

    def noOfLines(self):
        return self.d.NoOfLines
    def lineHeight(self):
        return self.d.lineHeight
    def lineAt(self, y):
        return (y / self.d.lineHeight) if self.d.lineHeight != 0 else 0

    def visibleLines(self):
        yspan = PixelYRange.fromWidth(self.yOffset(), self.visibleHeight())
        return (self.lineAt(yspan.start()), self.lineAt(yspan.end()))

    def visibleWidth(self):
        return self.viewport().width()
    def visibleHeight(self):
        return self.viewport().height()

    def columnsHeight(self):
        return self.d.NoOfLines*self.d.LineHeight

    def columnsWidth(self):
        return self.d.ColumnsWidth

    def xOffset(self):
        return self.horizontalScrollBar().value()

    def yOffset(self):
        return self.verticalScrollBar().value()

    def yOffsetOfLine(self, lineIndex):
        return lineIndex * self.d.lineHeight - self.yOffset()

    def setColumnsPos(self, x, y):
        self.horizontalScrollBar().setValue(x)
        self.verticalScrollBar().setValue(y)

    def setNoOfLines(self, new):
        if self.d.noOfLines == new:
            return
        self.d.noOfLines = new
        self.updateScrollBars()

    def setLineHeight(self, newHeight):
        if self.d.lineHeight == newHeight:
            return
        self.d.lineHeight = newHeight
        for col in self.d.Columns:
            col.setLineHeight(self.d.lineHeight)
        self.verticalScrollBar().setSingleStep(self.d.lineHeight)
        self.updateScrollBars()
    def updateWidths(self):
        self.d.updateWidths()
        self.updateScrollBars()

    def updateScrollBars(self):
        viewSize = self.maximumViewportSize()

        needsVerticalBar = ( self.columnsHeight() > viewSize.height() )
        needsHorizontalBar = ( self.columnsWidth() > viewSize.width() )
        scrollBarWidth = self.style().pixelMetric( QStyle.PM_ScrollBarExtent )

        if needsVerticalBar:
            viewSize.setWidth(viewSize.width() - scrollBarWidth)
        if needsHorizontalBar:
            viewSize.setHeight(viewSize.height() - scrollBarWidth)

        self.verticalScrollBar().setRange( 0, self.columnsHeight()-viewSize.height() )
        self.verticalScrollBar().setPageStep( viewSize.height() )
        self.horizontalScrollBar().setRange( 0, self.columnsWidth()-viewSize.width() )
        self.horizontalScrollBar().setPageStep( viewSize.width() )

    def updateColumn(self, columnRenderer, lines=None):
        if columnRenderer.isVisible():
            if lines is None:
                self.viewport().update(columnRenderer.x()-self.xOffset(), 0,
                                       columnRenderer.width(), self.visibleHeight())
            else:
                linesToUpdate = self.visibleLines()
                linesToUpdate.restrictTo( lines )
                if linesToUpdate.isValid():
                    x = columnRenderer.x() - self.xOffset()
                    y = self.yOffsetOfLine( linesToUpdate.start() )
                    width = columnRenderer.width()
                    height = self.d.LineHeight * linesToUpdate.width()
                    self.viewport().update( x, y, width, height )


    def noOfLinesPerPage(self):

        if d.LineHeight < 1:
            return 1

        result = (self.visibleHeight()-1) / self.d.LineHeight # -1 ensures to get always the last visible line

        if result < 1:
            # ensure to move down at least one line
            result = 1

        return result



    def addColumn(self, columnRenderer ):
    #   if  Reversed :
    #     Columns.prepend( C )
    #   else
        self.d.Columns.append( columnRenderer )

        self.updateWidths()



    def removeColumn( self, columnRenderer ):
        columnRendererIndex = self.d.Columns.indexOf( columnRenderer )
        if  columnRendererIndex != -1 :
            self.d.Columns.removeAt( columnRendererIndex )
        slefupdateWidths()



    def scrollContentsBy( self, dx, dy ):
        self.viewport().scroll( dx, dy )


    def event( self, event ):
        if  event.type() == QEvent.StyleChange or event.type() == QEvent.LayoutRequest :
            self.updateScrollBars()

        return QAbstractScrollArea.event(self, event )



    def resizeEvent( self,  event ):
        self.updateScrollBars()

        QAbstractScrollArea.resizeEvent(self, event )


    def paintEvent( self, paintEvent ):
        QAbstractScrollArea.paintEvent(self, paintEvent )

        x = self.xOffset()
        y = self.yOffset()

        dirtyRect = paintEvent.rect()
        dirtyRect.translate( x, y )

        painter = QPainter( self.viewport() )
        painter.translate( -x, -y )

        self.renderColumns( painter, dirtyRect.x(),dirtyRect.y(), dirtyRect.width(), dirtyRect.height() )



    def renderColumns(self, painter,  cx,  cy,  cw,  ch ):
        dirtyXs = PixelXRange.fromWidth( cx, cw )

        # content to be shown?
        if  dirtyXs.startsBefore(self.d.ColumnsWidth) :

            dirtyYs = PixelYRange.fromWidth( cy, ch )

            # collect affected columns
            dirtyColumns = []
            for column in self.d.Columns:
                if  column.isVisible() and column.overlaps(dirtyXs) :
                    dirtyColumns.append( column )


            # any lines of any columns to be drawn?
            if  self.d.NoOfLines > 0 :

                # calculate affected lines
                dirtyLines = visibleLines( dirtyYs )
                dirtyLines.restrictEndTo( self.d.NoOfLines - 1 )

                if  dirtyLines.isValid() :

                    # paint full columns
                    for col in self.d.Columns:
                        col.renderColumn( painter, dirtyXs, dirtyYs )

                    cy = dirtyLines.start() * self.d.LineHeight

                    # starting painting with the first line
                    line = dirtyLines.start()

                    painter.translate( dirtyColumns[0].x(), cy )

                    for column in dirtyColumns:
                        column.renderFirstLine( painter, dirtyXs, line )
                        painter.translate( column.width(), 0 )

                    painter.translate( -column.x(), 0 )

                    # Go through the other lines
                    while True:

                        ++line

                        if  line > dirtyLines.end() :
                            break

                        painter.translate( dirtyColumns[0].x(), self.d.LineHeight )

                        for column in dirtyColumns:

                            column.renderNextLine( painter )
                            painter.translate( column.width(), 0 )

                        painter.translate( -column.x(), 0 )

                    cy = dirtyLines.end() * self.d.LineHeight

                    painter.translate( 0, -cy )



            # draw empty columns?
            dirtyYs.setStart( self.columnsHeight() )
            if  dirtyYs.isValid() :

                for column in dirtyColumns:
                    column.renderEmptyColumn( painter, dirtyXs, dirtyYs )



        # painter empty rects
        dirtyXs.setStart( self.d.ColumnsWidth )
        if  dirtyXs.isValid() :
            self.renderEmptyArea( painter, dirtyXs.start(), cy, dirtyXs.width(), ch )



    def renderEmptyArea( self, painter,  cx , cy, cw,  ch):
        painter.fillRect( cx,cy, cw,ch, self.viewport().palette().brush(QPalette.Base) ) # TODO: use stylist here, too







if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    h = ColumnsView()
    h.show()

    app.exec_()
