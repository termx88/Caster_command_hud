import sys
from PySide2.QtCore import Qt, QSize
from PySide2.QtWidgets import QApplication, QStyle
from PySide2.QtGui import QColor, QPalette

from unittest.mock import Mock, patch
        
def hud_test():
    attrs = {'settings.HUD_TITLE': "HUD"}
    mock = Mock(**attrs)
    with patch.dict('sys.modules', {
            'castervoice' : mock,
            'castervoice.lib' : mock,
            'castervoice.lib.merge' : mock,
            'castervoice.lib.merge.communication' : mock,
            'castervoice.lib.merge.communication.Communicator' : mock,
            'dragonfly' : mock,
            }):
        from hud import HUDWindow
        huds_launch(HUDWindow)    
            
def huds_launch(HUDWindow):
    app = QApplication(sys.argv)
    windows = [
            HUDWindow(Mock()),
            HUDWindow(Mock()),
            HUDWindow(Mock()),
            HUDWindow(Mock()),
        ]
    
    setup_themes(windows)
    
    for window in windows:
        window.show()
    
    messages = [
        '<font color="blue">&lt;</font> numb one',
        '<font color="red">&gt;</font> Numbers: [<long>] numb <wnKK>, , 1',
        '<font color="blue">&lt;</font> numb two',
        '<font color="red">&gt;</font> Numbers: [<long>] numb <wnKK>, , 2',
        '<font color="blue">&lt;</font> numb three',
        '<font color="red">&gt;</font> Numbers: [<long>] numb <wnKK>, , 3',
        '<font color="blue">&lt;</font> numb four',
        '<font color="red">&gt;</font> Numbers: [<long>] numb <wnKK>, , 4',
        '<font color="blue">&lt;</font> numb five',
        '<font color="red">&gt;</font> Numbers: [<long>] numb <wnKK>, , 5',
        '<font color="blue">&lt;</font> numb six',
        '<font color="red">&gt;</font> Numbers: [<long>] numb <wnKK>, , 6',
        ]
    
    for i, message in enumerate(messages):
        for window in windows:
            window.output.append(message)

    app.exec_()

def setup_themes(windows):
    theme_window(
                window  = windows[0],   
                window_height = 200,
                alignment = Qt.AlignHCenter | Qt.AlignVCenter,  
                background_color = QColor(245, 245, 245, 255),         
                font_size = 8,                                      
                margins = 4,                                        
                scrollbar = True,
                frameless = False,
            )
    windows[0].output.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

    theme_window(
                window = windows[1], 
                window_height = 200,
                alignment = Qt.AlignRight | Qt.AlignVCenter, 
                rect_color = QColor(255, 255, 255, 150),     
                border_radius = 14,                        
                outline_color = QColor(0, 0, 0, 255),      
                outline_width = 2,                         
                force_disable_background = True,
                spacing = 3,
                #frameless = False,
            )
            
    theme_window(
                window = windows[2],  
                alignment = Qt.AlignHCenter | Qt.AlignBottom,   
                rect_color = QColor(240, 240, 240),              
                font_size = 18,                                     
                margins = 2,                                    
                force_disable_background = True,  
                scrollbar = True,     
                font_family = "Courier"
            )
            
    theme_window(
                window  = windows[3],
                window_width = 550,
                alignment = Qt.AlignRight | Qt.AlignBottom,     
                rect_color = QColor(50, 40, 48),                 
                background_color = QColor(21, 8, 0, 100),              
                text_color = QColor(210, 84, 0),                 
                border_radius = 10,  
                spacing = 10,
                #frameless = False,
            )
    
def theme_window(
                window, 
                alignment,
                window_width = 300,
                window_height = 300,
                rect_color = QColor(255, 255, 255, 0),
                background_color = QColor(255, 255, 255, 0),
                text_color = QColor(0, 0, 0),
                font_size = 14,
                border_radius = 5,
                margins = 10,
                spacing = 5,
                outline_color = QColor(0, 0, 0, 0),
                outline_width = 0,
                scrollbar = False,
                force_disable_background = False,
                font_family = "",
                frameless = True,
            ):
            
    size = QSize(window_width, window_height)
    screen_geometry = qApp.primaryScreen().geometry()
    if frameless:
        screen_geometry.adjust(400, 160, -30, -30)
    else:
        screen_geometry.adjust(400, 130, -30, -60)
    
    window.setGeometry(
        QStyle.alignedRect(
            Qt.LeftToRight,
            alignment,
            size,
            screen_geometry
        )
    )
    
    palette = window.palette()
    palette.setColor(QPalette.Base, rect_color)
    palette.setColor(QPalette.Window, background_color)
    palette.setColor(QPalette.Text, text_color)
    window.setPalette(palette)
    
    window.output.setTextEditBorderRadius(border_radius)
    window.output.setTextEditMargins(margins)
    window.output.setSpacing(spacing)
    
    window.output.setRectOutlineColor(outline_color)
    window.output.setRectOutlineWidth(outline_width)
    
    if scrollbar:
        window.output.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    else:
        window.output.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    window.output.setForceDisableBackground(force_disable_background)
    
    font = window.font()
    font.setPointSize(font_size)
    font.setFamily(font_family)
    window.setFont(font)
    window.repaint()
    window.output.updateTextEdits()
    window.setWindowFlag(Qt.FramelessWindowHint, frameless)
    
if __name__ == '__main__':
    hud_test()
