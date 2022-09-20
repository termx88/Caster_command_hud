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
                rect_outline_color = QColor(0, 0, 0, 0),
                rect_outline_width = 0
        ):
        super().__init__(text)
        
        self.draw_rect = draw_rect
        self.setRectOutlineColor(rect_outline_color)
        self.rect_outline_width = rect_outline_width
        self.setRectBorderRadius(rect_border_radius)
        self.setDocumentMargin(margins)
        
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
        self.document().setDocumentMargin(margins + self.rect_outline_width)
    
    def setRectOutlineColor(self, color):
        self.rect_outline_color = color
    
    def setRectOutlineWidth(self, new_width):
        base_document_margin = self.document().documentMargin() - self.rect_outline_width
        self.rect_outline_width = new_width
        self.setDocumentMargin(base_document_margin)
    
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
            
            brush = self.palette().brush(QPalette.Base)
            painter.setBrush(brush)
            
            border_radius = self.rect_border_radius
            
            pen = QPen(self.rect_outline_color)
            if border_radius == 0:
                pen.setWidthF(self.rect_outline_width * 2)
                painter.setPen(pen)
                painter.drawRect(self.rect())
            else:
                pen.setWidthF(self.rect_outline_width)
                painter.setPen(pen)
                
                if border_radius > self.height() / 2:
                    border_radius = self.height() /2
                    
                half_outline_width = self.rect_outline_width / 2
                rect = self.rect().adjusted(
                                    half_outline_width, half_outline_width, 
                                    -half_outline_width, -half_outline_width
                                )
                painter.drawRoundedRect(rect, border_radius, border_radius)
                if self.rect_outline_width > 1:
                    inner_radius = border_radius + half_outline_width
                    painter.drawRoundedRect(rect, inner_radius, inner_radius)
        
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
        Override, so page up and down events get passed to parent.
        '''
        next_page = event.matches(QtGui.QKeySequence.MoveToNextPage)
        previous_page = event.matches(QtGui.QKeySequence.MoveToPreviousPage)
        if next_page or previous_page:
            event.ignore()
        else:
            super().keyPressEvent(event)
            
    def wheelEvent(self, event):
        '''
        Override, so it would be impossible to zoom in the text edit.
        '''
        event.ignore()

    
if __name__ == "__main__":
    app = QApplication()
    window = CommandTextEdit("> - Starting Caster v 1.7.0 with `kaldi` Engine - ",
                            0,
                            True,
                            10,
                            QColor(0, 0, 0, 255),
                            10,
                        )
                        
                        
    window.show()
    # qApp.processEvents()
    window.setRectOutlineWidth(50)                    
    app.exec_()
