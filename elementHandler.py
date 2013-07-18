#!/usr/bin/python

import sys
from PyQt4 import QtCore, QtGui
from threading import Timer
import settings

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
            i.setFixedWidth(self.width()-settings.SCROLLBAR_WIDTH)

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