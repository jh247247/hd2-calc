#!/usr/bin/python

import sys
from PyQt4 import QtCore, QtGui
from threading import Timer
import settings
from elementHandler import ElementHandler, GuiMathElement
import mathProcess

class MaximaElementHandler(ElementHandler):
    maxima = mathProcess.maximaProcess()
    def __init__(self, parent=None):
        """
        Creates a list for storing the individual gui elements
        Might need restructuring later down the line for the math stuff,
        but this will do for now.
        """
        super(MaximaElementHandler,self).__init__(parent)

    def appendElement(self):
        super(MaximaElementHandler, self).appendElement()
        self.maxima.write(self.elements[-1].text.toPlainText())
