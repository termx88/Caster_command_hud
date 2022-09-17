from PySide2.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint, QRectF, QRect, QEvent
from PySide2.QtGui import QPainter, QPen, QColor, QFont, QBrush, QPalette, QTextDocument, QRegion
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QSizePolicy, QScrollArea, QLayout, QStackedLayout 
from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Qt

from command_text_edit import CommandTextEdit


class CommandLog(QScrollArea):
    def __init__(self,
                max_text_edits = 100,
                text_edit_margins = 4,
                draw_rect = True,
                rect_border_radius = 5,
        ):
        super().__init__()
        
        self.max_text_edits = max_text_edits
        
        self.draw_rect = draw_rect
        self.rect_border_radius = rect_border_radius
        self.text_edit_margins = text_edit_margins
        
        log = QWidget()
        self.setWidget(log)
        self.setWidgetResizable(True)
        
        self.layout = QVBoxLayout(log)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.viewport().setAutoFillBackground(False)
        
        self.rect_outline_color = QColor(0, 0, 0, 0)
        self.rect_outline_width = 0
        self.scroll_point_pos = None
        self.force_disable_background = False
        
    def setTextEditMargins(self, margins):
        '''
        Retroactively sets margins of text edits, updating scrollbar position
        '''
        if self.text_edit_margins != margins:
            self.text_edit_margins = margins
            if self.layout.count():
                normalized_position = self.getNormalizedScrollBarPosition()

                for i in range(self.layout.count()):
                    text_edit = self.layout.itemAt(i).widget()
                    text_edit.setDocumentMargin(margins)
                    self.resizeTextEdit(text_edit)
                
                self.setScrollBarToNormalizedPosition(normalized_position, True)
                
    def setTextEditBorderRadius(self, radius):
        ''' Retroactively sets border radius of text edits '''
        if self.rect_border_radius != radius:
            self.rect_border_radius = radius
            for i in range(self.layout.count()):
                text_edit = self.layout.itemAt(i).widget()
                text_edit.setRectBorderRadius(radius)
                text_edit.update()
    
    def setDrawFrame(self, draw_frame):
        if draw_frame == True:
            self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        else: 
            self.setFrameShape(QtWidgets.QFrame.NoFrame)
    
    def setDrawRect(self, draw_rect):
        ''' Retroactively sets if text edits draw a rectangle '''
        if self.draw_rect != draw_rect:
            self.draw_rect = draw_rect
            
            for i in range(self.layout.count()):
                text_edit = self.layout.itemAt(i).widget()
                text_edit.setDrawRect(draw_rect)
                text_edit.update()
                
    def setDirection(self, direction):     
        ''' Sets layout direction, updating scrollbar position '''
        if self.layout.direction() != direction:
            self.layout.setDirection(direction)
            
            if self.layout.count():
                normalized_position = self.getNormalizedScrollBarPosition()
                
                # inverting scroll bar position 
                # to match previously shown text edits
                maximum = self.verticalScrollBar().maximum()
                new_position = maximum * (1 - normalized_position)
                self.verticalScrollBar().setValue(new_position)    
    
    def setAlignment(self, alignment):
        ''' Retroactively sets alignment of text edits in layout '''
        if self.layout.alignment() != alignment:
            self.layout.setAlignment(alignment)
            for i in range(self.layout.count()):
                text_edit = self.layout.itemAt(i).widget()
                self.layout.setAlignment(text_edit, alignment)
            
    def setSpacing(self, spacing):
        ''' Retroactively sets spacing between text edits '''
        if self.layout.spacing() != spacing:
            if self.layout.count() == 0:
                self.layout.setSpacing(spacing)
            else:
                normalized_position = self.getNormalizedScrollBarPosition()    
                
                self.layout.setSpacing(spacing)
            
                self.setScrollBarToNormalizedPosition(normalized_position, True)
                    
    def setMaxTextEdits(self, max):
        self.max_text_edits = max
        self.clearTo(max)
    
    def getNormalizedScrollBarPosition(self):
        ''' Returns scroll bar position normalized to values between 0 and 1 '''
        scroll_bar = self.verticalScrollBar()
        if scroll_bar.maximum() == 0:
            if self.layout.direction() == QVBoxLayout.TopToBottom:
                return 1
            else:
                return 0
        return scroll_bar.value() / scroll_bar.maximum()
        
    def setScrollBarToNormalizedPosition(self, position, wait_for_update = False):
        # waiting for scrollbar to be updated
        if wait_for_update == True:
            qApp.processEvents()
            qApp.processEvents()
            # won't be 100 accurate for middle values, 
            # but will keep scrollbar at the bottom, when at bottom
                
        maximum = self.verticalScrollBar().maximum()
        new_position = maximum * position
        self.verticalScrollBar().setValue(new_position)
    
    def setRectOutlineColor(self, color):
        ''' Retroactively sets rectangle outline color'''
        if self.rect_outline_color != color:
            self.rect_outline_color = color
            
            for i in range(self.layout.count()):
                text_edit = self.layout.itemAt(i).widget()
                text_edit.setRectOutlineColor(color)
                text_edit.update()
        
    def setRectOutlineWidth(self, width):
        ''' Retroactively sets rectangle outline width'''
        if self.rect_outline_width != width:
            self.rect_outline_width = width
            if self.layout.count() > 0:        
                normalized_position = self.getNormalizedScrollBarPosition()    
                
                for i in range(self.layout.count()):
                    text_edit = self.layout.itemAt(i).widget()
                    text_edit.setRectOutlineWidth(width)
                    self.resizeTextEdit(text_edit)
                            
                self.setScrollBarToNormalizedPosition(normalized_position, True)
    
    def append(self, text):
        ''' Appends a new text edit to the end '''
        command_text_edit = CommandTextEdit(
                                    text, 
                                    self.text_edit_margins,             
                                    self.draw_rect,
                                    self.rect_border_radius,
                                    self.rect_outline_color,
                                    self.rect_outline_width
                        )
        
        self.layout.addWidget(command_text_edit, 0, self.layout.alignment())
        self.clearTo(self.max_text_edits)
        command_text_edit.show()
        self.resizeTextEdit(command_text_edit)
        
        if self.layout.direction() == QVBoxLayout.TopToBottom:
            self.scrollToBottom()
        
    def clearTo(self, num_to_keep):
        if self.layout.count() > num_to_keep:
            while self.layout.count() > num_to_keep:
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self.update()
    
    def clear(self):
        self.clearTo(0)
    
    def scrollToBottom(self):
        qApp.processEvents()
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateTextEdits()
        
    def updateTextEdits(self):
        for i in range(self.layout.count()):
            self.resizeTextEdit(self.layout.itemAt(i).widget())
        
    def resizeTextEdit(self, text):
        size = text.sizeForWidth(self.viewport().width())
        text.setFixedSize(size)
    
    """
    Scrolling point is drawn under the mouse when scrolling,
    when the window has a fully transparent or forcefully disabled background.
    Without it, scrolling and the mouse hitting a transparent area, 
    stops the scrolling.
    """
    
    def wheelEvent(self, event):
        if (self.palette().color(QPalette.Window).alpha() == 0 or 
            self.force_disable_background == True):
            self.enableScrollingPoint(event.position())    
        super().wheelEvent(event)
    
    def mouseMoveEvent(self, event):
        self.disableScrollingPoint()
        super().mouseMoveEvent(event)
    
    def leaveEvent(self, event):
        self.disableScrollingPoint()
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.scroll_point_pos:
            painter = QPainter(self.viewport())
            
            pen = QPen(QColor(0, 0, 0, 1))
            painter.setPen(pen)
        
            painter.drawPoint(self.scroll_point_pos) 
        
    def enableScrollingPoint(self, position):
        if self.scroll_point_pos == None:
            self.scroll_point_pos = position
            # both required
            self.setMouseTracking(True) 
            self.widget().setMouseTracking(True)
    
    def disableScrollingPoint(self):
        if self.scroll_point_pos:
            self.scroll_point_pos = None
            # both required
            self.setMouseTracking(False) 
            self.widget().setMouseTracking(False)
                
            self.update()    
    
    def setForceDisableBackground(self, toggle):
        self.force_disable_background = toggle
        
    def getBackgroundlessMask(self):
        ''' Returns a mask matching the widget excluding the background '''
        frame_geometry = self.frameGeometry()
        
        region = QRegion(frame_geometry)
        region -= self.childrenRegion()
        
        for i in range(self.layout.count()):
            text_edit = self.layout.itemAt(i).widget()
            text_edit_region = text_edit.region()
            
            text_edit_top_left = text_edit.rect().topLeft() 
            text_edit_top_left += QPoint(self.frameWidth(), self.frameWidth())
            
            offset = text_edit.mapTo(self.viewport(), text_edit_top_left)
            text_edit_region.translate(offset)
            region += text_edit_region
            
        if self.scroll_point_pos:
            region += QRegion(self.scroll_point_pos.x() + self.frameWidth(), 
                              self.scroll_point_pos.y() + self.frameWidth(),
                              1, 1)
        return region
    
if __name__ == "__main__":
    app = QApplication()
    runner = CommandLog()
    runner.resize(400, 400)
    
    runner.setWindowFlags(Qt.FramelessWindowHint)
    runner.show()
    
    runner.append("> - Starting Caster v 1.7.0 with `kaldi` Engine - ")
    runner.append('<font color="purple">&gt;</font> - Starting Caster v 1.7.0 with `kaldi` Engine - ')
    app.exec_()
