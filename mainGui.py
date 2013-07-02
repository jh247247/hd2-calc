import sys
from PySide import *
from threading import Timer

# Setup fonts to use (Since this is a high DPI device)
# Can be changed to suit tastes I guess...
FONT_STATUS = QtGui.QFont('Serif', 15, QtGui.QFont.Light)
FONT_GENERAL = QtGui.QFont('Serif', 15, QtGui.QFont.Light)
FONT_GENERAL_METRICS = QtGui.QFontMetrics(FONT_GENERAL)

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
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("QScrollBar:vertical { width: 30px; }")
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
        """Clear the mssage back to the default message"""
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
        super(ElementHandler,self).__init__()
        self.elements = []

        self.elementLayout = QtGui.QVBoxLayout(self)
        self.setLayout(self.elementLayout)
        self.elementLayout.setAlignment(QtCore.Qt.AlignBottom)

        self.appendElement()


    def appendElement(self):
        newElement = guiMathElement(self)
        self.elementLayout.addWidget(newElement)
        newElement.setFixedWidth(self.width()-55)
        self.elements.append(newElement)



class guiMathElement(QtGui.QWidget):
    INITIAL_HEIGHT = 100
    def __init__(self, parent=None):
        super(guiMathElement,self).__init__(parent)
        self.__initChildren()
        self.__initAnimation()
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                           QtGui.QSizePolicy.Expanding)
        self.setFixedWidth(parent.width())

        print FONT_GENERAL_METRICS.height()

    def __initChildren(self):
        self.setMaximumHeight(self.INITIAL_HEIGHT)
        self.text = QtGui.QTextEdit()
        # Magic number comes from added gui elements and text.
        self.text.setFixedHeight(self.INITIAL_HEIGHT)
        self.text.textChanged.connect(self.__textChanged)
        self.text.setSizePolicy(QtGui.QSizePolicy.Expanding, \
                                QtGui.QSizePolicy.Fixed)

        self.goRenderButton = QtGui.QPushButton(">>")
        self.goRenderButton.clicked.connect(self.__slideLeft)
        self.goRenderButton.setMaximumHeight(self.INITIAL_HEIGHT)
        self.goRenderButton.setSizePolicy(QtGui.QSizePolicy.Fixed, \
                                          QtGui.QSizePolicy.Expanding)

        self.layout = QtGui.QHBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.goRenderButton)
        self.setLayout(self.layout)

    def __initAnimation(self):
        self.slideLeftAnim = QtCore.QPropertyAnimation(self, "geometry")
        self.slideRightAnim = QtCore.QPropertyAnimation(self, "geometry")

        self.slideLeftAnim.setDuration(250)
        self.slideRightAnim.setDuration(250)

        self.slideRightAnim.setEasingCurve(QtCore.QEasingCurve.OutQuad)

        self.slideRightAnim.setEasingCurve(QtCore.QEasingCurve.OutQuad)

    def __slideLeft(self):
        w = self.width()
        h = self.height()

        x = self.x()
        y = self.y()

        self.slideLeftAnim.setStartValue(QtCore.QRect(x,y,x+w,y+h))
        self.slideLeftAnim.setEndValue(QtCore.QRect(x-w,y,x+w,y+h))
        self.slideLeftAnim.start()


    def __slideRight(self):
        w = self.width()
        h = self.height()

        x = self.x()
        y = self.y()

        self.slideRightAnim.setStartValue(QtCore.QRect(x,y,x+w,y+h))
        self.slideRightAnim.setEndValue(QtCore.QRect(x+w,y,x+w+w,y+h))

        self.slideRightAnim.start()

    def __textChanged(self):
        h = self.text.document().size().height()+5
        if h > self.INITIAL_HEIGHT:
            self.setFixedHeight(h)

    def resizeEvent(self,event):
        super(guiMathElement,self).resizeEvent(event)

def main():
    app = QtGui.QApplication(sys.argv)
    app.setFont(FONT_GENERAL)
    main = mainWindow()
    main.getStatusObject().setTempMessage('Hello1!');
    main.getStatusObject().setTempMessage('Hello2!');
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
