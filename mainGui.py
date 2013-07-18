#!/usr/bin/python
import sys
from PyQt4 import QtCore, QtGui
from threading import Timer
from elementHandler import ElementHandler
import settings
import maximaElementHandler

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

        self.elements = None

        self.scroll = QtGui.QScrollArea(self)
        # We want things to always show, makes size calculations easier.
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # This is some stylesheet hackery to get things how I want it,
        # Apparently We cant just go
        # self.scroll.verticalScrollBar().setFixedWidth(SCROLLBAR_WIDTH)
        # Oh well. This works.
        self.scroll.setStyleSheet("QScrollBar:vertical { width: " + \
                                  str(settings.SCROLLBAR_WIDTH) + "px; }")
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

    def setElementHandler(self, handler):
        self.elements = handler
        self.scroll.setWidget(self.elements)


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
        self.__parentBar.setFont(settings.FONT_STATUS)
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



def main():
    app = QtGui.QApplication(sys.argv)
    app.setFont(settings.FONT_GENERAL)
    main = mainWindow()
    elements = maximaElementHandler.MaximaElementHandler()
    main.setElementHandler(elements)
    main.getStatusObject().setTempMessage('Hello1!');
    main.getStatusObject().setTempMessage('Hello2!');
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
