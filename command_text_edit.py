from PySide2.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint, QRectF, QRect, QSize
from PySide2.QtGui import QPainter, QPen, QColor, QFont, QBrush, QPalette, QFontMetricsF, QFontMetrics, QTextOption
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QLayout, QTextEdit, QSizePolicy, QFrame, QLineEdit

from PySide2 import QtGui
import sys
import html
import math

class CommandTextEdit(QTextEdit):
    def __init__(self,
                text,
                margins,
                draw_rect,
                rect_border_radius = 0,
        ):
        super().__init__(text)
        
        self.draw_rect = draw_rect
        self.rect_border_radius = rect_border_radius
        self.document().setDocumentMargin(margins)
        
        self.setReadOnly(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.viewport().setAutoFillBackground(False)
    
    def setDrawRect(self, draw_rect):
        self.draw_rect = draw_rect
        
    def setRectBorderRadius(self, rect_border_radius):
        self.rect_border_radius = rect_border_radius
        
    def setDocumentMargin(self, margins):
        self.document().setDocumentMargin(margins)
    
    def sizeForWidth(self, width):
        ''' Returns the preferred size for this widget, for the given width '''
        doc = self.document().clone()
        
        doc.setTextWidth(99999)
        max_width = doc.idealWidth()
        if width > max_width:
            width = max_width
        doc.setTextWidth(width);
        
        height = doc.size().height()
        width = math.ceil(doc.idealWidth())
        
        return QSize(width, height)
        
    def paintEvent(self, event):
        if self.draw_rect == True:
            painter = QPainter(self.viewport())
            painter.setRenderHint(QPainter.Antialiasing, True)
            
            # color of rectangle border
            pen = QPen(QColor(0, 0, 0, 0))
            painter.setPen(pen)
        
            brush = self.palette().brush(QPalette.Base)
            painter.setBrush(brush)
        
            border_radius = self.rect_border_radius
            if border_radius > self.height() / 2:
                border_radius = self.height() /2
                
            painter.drawRoundedRect(self.rect(), border_radius, border_radius)
        
        super().paintEvent(event)
    
    def region(self):
        path = QtGui.QPainterPath()
        path.addRoundedRect(self.rect(), self.rect_border_radius, self.rect_border_radius)
        
        return path.toFillPolygon().toPolygon()
        
    def mouseMoveEvent(self, event):
        ''' 
        Override, so mouse move events without pressed buttons,
        get passed to parent. 
        Used for scrolling point removal.
        '''
        if event.buttons():
            super().mouseMoveEvent(event)
        else:
            event.ignore()
    
    def keyPressEvent(self, event):
        '''
        Override, so scroll events get passed to parent.
        '''
        next_page = event.matches(QtGui.QKeySequence.MoveToNextPage)
        previous_page = event.matches(QtGui.QKeySequence.MoveToPreviousPage)
        if next_page or previous_page:
            event.ignore()
        else:
            super().keyPressEvent(event)
    
if __name__ == "__main__":
    app = QApplication()
    window = CommandTextEdit("> - Starting Caster v 1.7.0 with `kaldi` Engine - ",
                            0,
                            True
                        )
    window.show()
    app.exec_()