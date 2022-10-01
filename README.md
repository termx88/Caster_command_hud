# Caster_command_hud
## Customization Examples:
Windows | Linux
| :---: | :---: |
<img src="./art/windows.png"/> | <img src="./art/linux.png"/> |

## Usage Examples:
Dragging by background | Clicking through backgroundless window
| :---: | :---: |
<img src="./art/dragging.gif"/> | <img src="./art/click_through.gif"/>

## Usage Instructions:
* Clone this repo.
### With Caster
* You have to be using Caster with hud support. Currently that's the [DropPy2 branch](https://github.com/dictation-toolbox/Caster/tree/DropPy2).
* In settings.toml ([user dir docs](https://caster.readthedocs.io/en/latest/readthedocs/User_Dir/Caster_User_Dir/)) change HUD_PATH to point to the hud.py gotten from this repo.
* If Caster is already running with a hud instance. Close hud and reboot caster.
### Testing
* Running `test_runner.py` will open 4 windows with different settings (like in the screenshots)
* requirements.txt in master doesn't include PySide2, so might need to install it. If needed run `pip install PySide2` or `python -m pip install PySide2`. And try running `test_runner.py` again.

## Settings explanation: 
### window
* WINDOW_FRAMELESS \<bool> - setting to True, disables window decorations (frame, titlebar) (macOS and Windows require this to be True, for a transparent background)
* WIDTH \<int> - width of the window
* HEIGHT \<int> - height of the window
* WINDOW_OFFSET_X \<int> - horizontal offset away from screen edge
* WINDOW_OFFSET_Y \<int> - vertical offset away from screen edge
* WINDOW_ALIGNMENT \<PySide2.QtCore.Qt.Alignment> - alignment of the window position on the screen (ex. Qt.AlignBottom | Qt.AlignRight, would align it to the bottom right corner of the screen)
* SCREEN \<int> - screen on which to open window, invalid values default to 0

### command log
* DIRECTION \<PySide2.QtWidgets.QBoxLayout.Direction> - direction in which command text edits are laid out (ex. QVBoxLayout.TopToBottom, would make new command text edits be added below previous ones)
* ALIGNMENT \<PySide2.QtCore.Qt.Alignment> - alignment of the command text edits in the window (ex. Qt.AlignRight | Qt.AlignBottom would start filling command text edits from bottom to top, and align them to the right side of the window)
* SCROLL_BAR_OFF \<bool> - setting to True, disables scroll_bar
* DRAW_FRAME \<bool> - setting to True, draws a simple frame around the main widget (different from the window frame, which allows to resize windows. This one is purely visual)
* BORDER_RADIUS \<float> - radius of the rectangle's corners (uses absolute measurements)
* RECT_OUTLINE_COLOR \<tuple*> - rectangle outline color 
* RECT_OUTLINE_WIDTH \<float> -  rectangle outline width, setting to 0 disables outline
* RECT_MARGINS \<float> - margins of the command text edits
* SPACING \<float> - spacing between command text edits
* FORCE_DISABLE_BACKGROUND \<bool> - sets a mask which disables the background of the window (required on linux, to be able to click through the window. For Windows and MacOS (testing needed) it's better to set background_color alpha to 0). Might also disable window decorations on some setups and cause jittery updates.

\* RECT_OUTLINE_COLOR (is tuple of ints (R, G, B, A), but maybe should be PySide2.QtGui.QColor)

### palette
* BACKGROUND_COLOR \<tuple*> - the background color of the window (ex. (50, 0, 0, 10), would be a lightly red almost fully transparent window.) Setting the alpha of this to 0 is the preferred way to disable the background on Windows and MacOS (testing needed)
* TEXT_COLOR \<tuple*> - the color of the text
* FONT_SIZE \<float> - size of the font in points
* FONT_FAMILY \<str> - the family name of the font
  > The family name may optionally also include a foundry name, e.g. “Helvetica [Cronyx]”. If the family is available from more than one foundry and the foundry isn’t specified, an arbitrary foundry is chosen. If the family isn’t available a family will be set using the font matching algorithm. 

  [cited from qt docs](https://doc.qt.io/qtforpython-5/PySide2/QtGui/QFont.html#PySide2.QtGui.PySide2.QtGui.QFont.setFamily)
* RECT_COLOR \<tuple*> - color of the rectangle
* FONT_SUBPIXEL_AA \<bool> - setting to True enables subpixel anti aliasing

\* BACKGROUND_COLOR, TEXT_COLOR, RECT_COLOR (are tuple of ints (R, G, B, A), but maybe should be PySide2.QtGui.QColor)
