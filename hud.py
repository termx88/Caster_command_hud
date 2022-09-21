#! python
'''
Caster HUD Window module
'''
# pylint: disable=import-error,no-name-in-module
import html
import json
import os
import signal
import sys
import threading
import PySide2.QtCore
import PySide2.QtGui
import dragonfly
from xmlrpc.server import SimpleXMLRPCServer
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QTextEdit
from PySide2.QtWidgets import QTreeView
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QWidget
try:  # Style C -- may be imported into Caster, or externally
    BASE_PATH = os.getcwd().rsplit(os.path.sep + "castervoice", 1)[0]
    # BASE_PATH = os.path.realpath(__file__).rsplit(os.path.sep + "castervoice", 1)[0]
    if BASE_PATH not in sys.path:
        sys.path.append(BASE_PATH)
finally:
    from castervoice.lib.merge.communication import Communicator
    from castervoice.lib import settings

from command_log import CommandLog

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QPalette, QColor, QFont, QBrush, QRegion
from PySide2.QtWidgets import QStyleFactory, QStyle
from PySide2 import QtWidgets, QtCore

CLEAR_HUD_EVENT = PySide2.QtCore.QEvent.Type(PySide2.QtCore.QEvent.registerEventType(-1))
HIDE_HUD_EVENT = PySide2.QtCore.QEvent.Type(PySide2.QtCore.QEvent.registerEventType(-1))
SHOW_HUD_EVENT = PySide2.QtCore.QEvent.Type(PySide2.QtCore.QEvent.registerEventType(-1))
HIDE_RULES_EVENT = PySide2.QtCore.QEvent.Type(PySide2.QtCore.QEvent.registerEventType(-1))
SHOW_RULES_EVENT = PySide2.QtCore.QEvent.Type(PySide2.QtCore.QEvent.registerEventType(-1))
SEND_COMMAND_EVENT = PySide2.QtCore.QEvent.Type(PySide2.QtCore.QEvent.registerEventType(-1))


class RPCEvent(PySide2.QtCore.QEvent):

    def __init__(self, type, text):
        PySide2.QtCore.QEvent.__init__(self, type)
        self._text = text

    @property
    def text(self):
        return self._text


class RulesWindow(QWidget):

    _WIDTH = 600
    _MARGIN = 30

    def __init__(self, text):
        QWidget.__init__(self, f=(PySide2.QtCore.Qt.WindowStaysOnTopHint))
        x = dragonfly.monitors[0].rectangle.dx - (RulesWindow._WIDTH + RulesWindow._MARGIN)
        y = 300
        dx = RulesWindow._WIDTH
        dy = dragonfly.monitors[0].rectangle.dy - (y + 2 * RulesWindow._MARGIN)
        self.setGeometry(x, y, dx, dy)
        self.setWindowTitle("Active Rules")
        rules_tree = PySide2.QtGui.QStandardItemModel()
        rules_tree.setColumnCount(2)
        rules_tree.setHorizontalHeaderLabels(['phrase', 'action'])
        rules_dict = json.loads(text)
        rules = rules_tree.invisibleRootItem()
        for g in rules_dict:
            gram = PySide2.QtGui.QStandardItem(g["name"]) if len(g["rules"]) > 1 else None
            for r in g["rules"]:
                rule = PySide2.QtGui.QStandardItem(r["name"])
                rule.setRowCount(len(r["specs"]))
                rule.setColumnCount(2)
                row = 0
                for s in r["specs"]:
                    phrase, _, action = s.partition('::')
                    rule.setChild(row, 0, PySide2.QtGui.QStandardItem(phrase))
                    rule.setChild(row, 1, PySide2.QtGui.QStandardItem(action))
                    row += 1
                if gram is None:
                    rules.appendRow(rule)
                else:
                    gram.appendRow(rule)
            if gram:
                rules.appendRow(gram)
        tree_view = QTreeView(self)
        tree_view.setModel(rules_tree)
        tree_view.setColumnWidth(0, RulesWindow._WIDTH / 2)
        layout = QVBoxLayout()
        layout.addWidget(tree_view)
        self.setLayout(layout)


class HUDWindow(QMainWindow):

    def __init__(self, server):
        QMainWindow.__init__(self)
        self.server = server
        self.setup_xmlrpc_server()
        self.output = CommandLog()
        self.setCentralWidget(self.output)
        
        self.rules_window = None
        self.commands_count = 0
        self.drag_begin_pos = None
        
        self.setup_window()
        self.setup_command_log()
        self.setup_theme()
        
    def setup_window(self):
        window_frameless = True
        width = 300
        height = 200
        window_offset_x = 20
        window_offset_y = 30
        window_alignment = Qt.AlignRight | Qt.AlignBottom
        screen = 0
        
        self.setWindowTitle(settings.HUD_TITLE)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
           
        if window_frameless:
            print("setting frameless window: On")
            self.setWindowFlag(Qt.FramelessWindowHint, True)
            
        if not width:
            print("setting default width: 300")
            width = 300
        else:
            print("setting width: " + str(width))
        
        if not height:
            print("setting default height: 200")
            height = 200
        else:
            print("setting height: " + str(height))
        
        if not (type(window_offset_x) is int):
            print("setting default offset x: 30")
            window_offset_x = 30
        else:
            print("setting offset x: " + str(window_offset_x))
        
        if not (type(window_offset_y) is int):
            print("setting default offset y: 30")
            window_offset_y = 30
        else:
            print("setting offset y: " + str(window_offset_y))
        
        if not (type(screen) is int) or (screen >= len(qApp.screens()) or 
                screen < 0):
            screen = 0
        
        if not window_alignment:
            print("setting default alignment: top right")
            window_alignment = Qt.AlignRight | Qt.AlignTop
         
        size = QSize(width, height)
        
        screen_geometry = qApp.screens()[screen].geometry()
        screen_geometry.adjust(window_offset_x, window_offset_y, 
                                -window_offset_x, -window_offset_y)
        
        self.setGeometry(
            QStyle.alignedRect(
                Qt.LeftToRight,
                window_alignment,
                size,
                screen_geometry
            )
        )

    def setup_command_log(self):
        direction = QVBoxLayout.TopToBottom
        alignment = Qt.AlignRight | Qt.AlignBottom
        scroll_bar_off = False
        draw_frame = False
        border_radius = 5
        rect_outline_color = (0, 0, 0, 255)
        rect_outline_width = 2
        margins = 4
        spacing = ""
        force_disable_background = False
        
        if direction:
            print("setting direction: " + str(direction))
            self.output.setDirection(direction)
        if alignment:
            print("setting alignment: " + str(alignment))
            self.output.setAlignment(alignment) 
        if scroll_bar_off:
            print("setting scroll bar: off")
            self.output.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 
        else:
            print("setting scroll bar: on")
            self.output.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        if type(border_radius) is int:            
            print("setting border radius: " + str(border_radius))
            self.output.setTextEditBorderRadius(border_radius) 
        if rect_outline_color and rect_outline_width > 0:
            print("setting color outline color: " + str(rect_outline_color))
            self.output.setRectOutlineColor(QColor(*rect_outline_color))
        if type(rect_outline_width) is int:            
            print("setting rect outline width: " + str(rect_outline_width))
            self.output.setRectOutlineWidth(rect_outline_width)
        if type(margins) is int:
            print("setting margins: " + str(margins))
            self.output.setTextEditMargins(margins)
        if type(spacing) is int:
            print("setting spacing: " + str(spacing))
            self.output.setSpacing(spacing)
        print("setting draw frame: " + str(draw_frame))                
        self.output.setDrawFrame(draw_frame)
        print("setting force background off: " + str(force_disable_background))                
        self.output.setForceDisableBackground(force_disable_background)
    
    def setup_theme(self):
        background_color = (50, 0, 0, 10)
        text_color = ""
        font_size = ""
        font_family = ""
        rect_color = ""
        font_subpixel_aa = ""
        
        palette = self.palette()
        font = self.font()
        
        if background_color:
            print("setting background color: " + str(background_color))
            palette.setColor(QPalette.Window, QColor(*background_color))
        
        # setting background alpha 0, so it doesn't show through transparent rectangle
        if self.output.force_disable_background:
            default_color = palette.color(QPalette.Window)    
            default_color.setAlpha(0)
            palette.setColor(QPalette.Window, default_color)
        
        if text_color:
            print("setting text color: " + str(text_color))
            palette.setColor(QPalette.Text, QColor(*text_color))
        if font_size:
            print("setting font size: " + str(font_size))
            font.setPixelSize(font_size)
            # font.setPointSize(font_size)
        if font_family:
            print("setting font family: " + str(font_family))
            font.setFamily(font_family)
        if rect_color:
            print("setting rect color: " + str(rect_color))
            palette.setColor(QPalette.Base, QColor(*rect_color))
        if not font_subpixel_aa: 
            print("setting font aa: Off")
            font.setStyleStrategy(QFont.NoSubpixelAntialias)
        
        self.setFont(font)
        self.setPalette(palette)
        self.output.updateTextEdits()
        
    
    def event(self, event):
        if event.type() == SHOW_HUD_EVENT:
            self.show()
            return True
        if event.type() == HIDE_HUD_EVENT:
            self.hide()
            return True
        if event.type() == SHOW_RULES_EVENT:
            self.rules_window = RulesWindow(event.text)
            self.rules_window.show()
            return True
        if event.type() == HIDE_RULES_EVENT and self.rules_window:
            self.rules_window.close()
            self.rules_window = None
            return True
        if event.type() == SEND_COMMAND_EVENT:
            escaped_text = html.escape(event.text)
            if escaped_text.startswith('$'):
                formatted_text = '<font color="blue">&lt;</font><b>{}</b>'.format(escaped_text[1:])
                if self.commands_count == 0:
                    self.output.clear()
                self.output.append(formatted_text)
                
                self.commands_count += 1
                return True
            if escaped_text.startswith('@'):
                formatted_text = '<font color="purple">&gt;</font><b>{}</b>'.format(escaped_text[1:])
            elif escaped_text.startswith(''):
                formatted_text = '<font color="red">&gt;</font>{}'.format(escaped_text)
            else:
                formatted_text = escaped_text
            self.output.append(formatted_text)
            return True
        if event.type() == CLEAR_HUD_EVENT:
            self.commands_count = 0
            return True
        return QMainWindow.event(self, event)

    def mousePressEvent(self, event):
        if self.drag_begin_pos == None and (
                self.windowFlags() & Qt.FramelessWindowHint):
            if (event.button() == Qt.LeftButton or 
                event.button() == Qt.RightButton):
                self.drag_begin_pos = event.pos()
        
    def mouseReleaseEvent(self, event):
        if self.drag_begin_pos:
            if (event.buttons() != event.buttons() | Qt.LeftButton and 
                event.buttons() != event.buttons() | Qt.RightButton):
                self.drag_begin_pos = None
       
    def mouseMoveEvent(self, event):
        if self.drag_begin_pos:
            offset = event.globalPos() - self.drag_begin_pos
            self.move(offset)
        super().mouseMoveEvent(event)
    
    def forceDisableBackground(self):
        ''' 
        Sets a mask of what to draw. 
        Including everything, except the background.
        '''
        frame_geometry = self.frameGeometry()
        
        offset_x = self.x() - self.geometry().x()
        offset_y = self.y() - self.geometry().y()
        frame_geometry.moveTo(offset_x, offset_y)
        
        region = QRegion(frame_geometry)
        # output.viewport().childrenRegion() extends above, including titlebar
        # childrenRegion() includes scrollbar
        # Their intersection doesn't include neither a scrollbar nor a titlebar
        region -= self.output.viewport().childrenRegion().intersected(
                        self.childrenRegion())
        # alt solution to ^
        # viewport_region = self.output.viewport().childrenRegion().boundingRect()
        # region -= QRegion(0, 0, viewport_region.width(), viewport_region.height() + viewport_region.y())
        
        region += self.output.getBackgroundlessMask()
        self.setMask(region)
        
    def paintEvent(self, event):
        if self.output.force_disable_background == True:
            self.forceDisableBackground()
        super().paintEvent(event)
    
    def closeEvent(self, event):
        event.accept()

    def setup_xmlrpc_server(self):
        self.server.register_function(self.xmlrpc_clear, "clear_hud")
        self.server.register_function(self.xmlrpc_ping, "ping")
        self.server.register_function(self.xmlrpc_hide_hud, "hide_hud")
        self.server.register_function(self.xmlrpc_hide_rules, "hide_rules")
        self.server.register_function(self.xmlrpc_kill, "kill")
        self.server.register_function(self.xmlrpc_send, "send")
        self.server.register_function(self.xmlrpc_show_hud, "show_hud")
        self.server.register_function(self.xmlrpc_show_rules, "show_rules")
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()


    def xmlrpc_clear(self):
        PySide2.QtCore.QCoreApplication.postEvent(self, PySide2.QtCore.QEvent(CLEAR_HUD_EVENT))
        return 0

    def xmlrpc_ping(self):
        return 0

    def xmlrpc_hide_hud(self):
        PySide2.QtCore.QCoreApplication.postEvent(self, PySide2.QtCore.QEvent(HIDE_HUD_EVENT))
        return 0

    def xmlrpc_show_hud(self):
        PySide2.QtCore.QCoreApplication.postEvent(self, PySide2.QtCore.QEvent(SHOW_HUD_EVENT))
        return 0

    def xmlrpc_hide_rules(self):
        PySide2.QtCore.QCoreApplication.postEvent(self, PySide2.QtCore.QEvent(HIDE_RULES_EVENT))
        return 0

    def xmlrpc_kill(self):
        QApplication.quit()

    def xmlrpc_send(self, text):
        PySide2.QtCore.QCoreApplication.postEvent(self, RPCEvent(SEND_COMMAND_EVENT, text))
        return len(text)

    def xmlrpc_show_rules(self, text):
        PySide2.QtCore.QCoreApplication.postEvent(self, RPCEvent(SHOW_RULES_EVENT, text))
        return len(text)


def handler(signum, frame):
    """
    This handler doesn't stop the application when ^C is pressed,
    but it prevents exceptions being thrown when later
    the application is terminated from GUI.  Normally, HUD is started
    by the recognition process and can't be killed from shell prompt,
    in which case this handler is not needed.
    """
    pass


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    server_address = (Communicator.LOCALHOST, Communicator().com_registry["hud"])
    # allow_none=True means Python constant None will be translated into XML
    server = SimpleXMLRPCServer(server_address, logRequests=False, allow_none=True)
    app = QApplication(sys.argv)
    window = HUDWindow(server)
    window.show()
    exit_code = app.exec_()
    server.shutdown()
    sys.exit(exit_code)
