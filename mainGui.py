#!/usr/bin/python
import sys
from PyQt4 import QtCore, QtGui
from threading import Timer

# Setup fonts to use (Since this is a high DPI device)
# Can be changed to suit tastes I guess...
FONT_STATUS = QtGui.QFont('Serif', 15, QtGui.QFont.Light)
FONT_GENERAL = QtGui.QFont('Serif', 15, QtGui.QFont.Light)
FONT_GENERAL_METRICS = QtGui.QFontMetrics(FONT_GENERAL)

SCROLLBAR_WIDTH = 30 # width of vertical scrollbar in pixels.
# this is for touchscreen interfaces.

class mainWindow(QtGui.QMainWindow):
    """
    Main window for the HDCalc application. Should ideally be a skeleton
    for other modules to be 'plugged in' with minimal change to the code.
    """
    def __init__(self):
        """
        Initialise basic gui elements. Others can be added later
        according to the users tastes.
        """
        super(mainWindow, self).__init__();
        self.__initStatus()
        self.__initWindow()

        self.elements = ElementHandler(self)

        self.scroll = QtGui.QScrollArea(self)
        # We want things to always show, makes size calculations easier.
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # This is some stylesheet hackery to get things how I want it,
        # Apparently We cant just go
        # self.scroll.verticalScrollBar().setFixedWidth(SCROLLBAR_WIDTH)
        # Oh well. This works.
        self.scroll.setStyleSheet("QScrollBar:vertical { width: " + \
                                  str(SCROLLBAR_WIDTH) + "px; }")
        self.scroll.setWidget(self.elements)
        self.scroll.setWidgetResizable(True)

        self.setCentralWidget(self.scroll)

    def __initStatus(self):
        """
        The statusbar for the main window is handled by an external class,
        it can be grabbed by other classes to send notfications etc.

        The statusbar is used to show messages such as 'Processing', 'Plotting',
        'Error:' and other messages as seen fit.
        """

        self.statusBar = StatusHandler(self.statusBar());
    # DUMMY FOR x86 PLATFORM
    def __initWindow(self):
        """
        This code is specifically used to initialise the window for desktop
        platforms, setting it to the same size as the device screen.

        This gives an accurate representation of the screen as is would be
        seen on the device.
        """

        self.resize(840, 480)
        self.setWindowTitle("Hello, World!")
        self.show()

    ## INITS END HERE

    def getStatusObject(self):
        return self.statusBar


class StatusHandler:
    """
    This class handles the status bar of the main window.

    Main focus is to allow certain messages to be shown for a specified amount
    of time etc. Note that there is no limit to the timeframe for which the
    message is displayed...
    """

    __parentBar = None
    __previousMessage = None
    DEFAULT_MESSAGE = 'Ready'
    messageStack = []
    timer = None

    def __init__(self, parentBar):
        """Initialise the status bar to sane defaults."""
        self.__parentBar = parentBar
        self.__parentBar.setFont(FONT_STATUS)
        self.clearMessage()

    def setMessage(self, message):
        """Simply set the message for the statusbar."""
        self.__parentBar.showMessage(message);

    def clearMessage(self):
        """Clear the message back to the default message"""
        self.setMessage(self.DEFAULT_MESSAGE)

    def setTempMessage(self, message, time=5):
        """
        Displays a message for a specified amount of time in seconds.

        TODO: Might want to add a stack of messages or something to handle
        multiple messages being added.
        """
        # save current message

        # if timer is running...
        if self.timer != None and self.timer.isAlive():
            # save current message and requested time onto the stack
            self.messageStack.append([message,time])
        else:
            # save previous (permanent) message
            self.__previousMessage = self.__parentBar.currentMessage()

            # set our new temp message to the statusbar
            self.setMessage(message);

            # make a timer for the specified time and start it.
            # calls to restore previous message after completion.
            self.timer = Timer(time, self.__setPreviousMessage)
            self.timer.start()

    def __setPreviousMessage(self):
        """
        Restore the previous message to the statusbar if there
        is nothing on the stack.

        If there is, start a new timer for that message and quit.
        """

        # no more messages in the stack
        if len(self.messageStack) == 0:
            # Sweet! We can go back to out previous message!
            self.setMessage(self.__previousMessage);
            self.timer = None
        else:
            # still have a message in the stack!
            [newMessage, newTime] = self.messageStack.pop();
            # Set new temp message
            self.setMessage(newMessage);
            # Start a timer to check for new massages later.
            self.timer = Timer(newTime, self.__setPreviousMessage)
            self.timer.start()

        # xorg doesn't seem to like this line
        # however, it isn't fatal, so it doesn't matter right now.
        self.__parentBar.repaint()

# Everything has to start somewhere. This app starts here.

class ElementHandler(QtGui.QWidget):
    def __init__(self, parent=None):
        """
        Creates a list for storing the individual gui elements
        Might need restructuring later down the line for the math stuff,
        but this will do for now.
        """
        super(ElementHandler,self).__init__()
        self.elements = []

        # Create a vertical layout so we can scroll.
        self.elementLayout = QtGui.QVBoxLayout(self)
        self.setLayout(self.elementLayout)
        self.elementLayout.setAlignment(QtCore.Qt.AlignBottom)

        self.appendElement()

    def appendElement(self):
        """
        Appends a new element and finalizes the previous one.
        """
        newElement = guiMathElement(self)
        self.elementLayout.addWidget(newElement)
        # Finalize the previous element so wierd stuff doesn't happen.
        if len(self.elements) != 0:
            self.elements[-1].finalize()
        self.elements.append(newElement)

    def resizeEvent(self,event):
        """
        If this is resized, ensure that the inner widgets are properly
        resized as well.
        """

        super(ElementHandler, self).resizeEvent(event)

        self.resize(event.size())
        for i in self.elements:
            i.setFixedWidth(self.width()-SCROLLBAR_WIDTH)

        # Have to do this to redraw the layout.
        self.elementLayout.activate()



class guiMathElement(QtGui.QWidget):
    # This should be about 1-2 lines for our text size.
    INITIAL_HEIGHT = 66
    def __init__(self, parent=None):
        """
        Init stuff to be used in this gui element.
        """
        super(guiMathElement,self).__init__(parent)
        self.__initChildren()

    def __initChildren(self):
        """
        Inits child widgets.
        self.text is the textbox.
        """
        self.text = QtGui.QTextEdit()
        # Magic number comes from added gui elements and text.
        self.text.setFixedHeight(self.INITIAL_HEIGHT)

        # connect textchanges signal to our own private slot.
        # This resizes the textBox as new text is added.
        self.text.textChanged.connect(self.__textChanged)
        self.text.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                                QtGui.QSizePolicy.Fixed)


        self.layout = QtGui.QHBoxLayout(self)
        self.layout.addWidget(self.text)
        self.setLayout(self.layout)

    def __textChanged(self):
        """
        This function is only called by the signal textChanged from the self.text
        textbox. It resizes the textbox and the containing widget to make sure there are no
        scroll bars as they are terrible on a touchscreen.
        """
        # base resizing of the widget on the changing text.
        # A sprinkling of magic numbers to keep things nice looking.
        baseHeight = self.text.document().size().height()
        if baseHeight >= self.INITIAL_HEIGHT:
            # Some magic numbers to make things look nice.
            self.setFixedHeight(baseHeight+10)
            self.text.setFixedHeight(baseHeight+5)
        self.text.ensureCursorVisible()


    def finalize(self):
        """
        This finalizes the code in the text box.
        Should only be called once the code is rendered.
        Also greys out the box so that text cannot be edited.
        """
        self.text.setReadOnly(True)
        self.text.setEnabled(False)

def main():
    app = QtGui.QApplication(sys.argv)
    app.setFont(FONT_GENERAL)
    main = mainWindow()
    main.getStatusObject().setTempMessage('Hello1!');
    main.getStatusObject().setTempMessage('Hello2!');
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
