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
        if len(self.elements) > 1:
            input = self.elements[-2].text.toPlainText()
            # make sure input is terminated by something.
            if input.endswith(';') == False and\
               input.endswith('$') == False:
                input += ';'
            self.maxima.write(input)
            output = self.maxima.getOutput()
            # length of output should be 1. If not something weird is going on.
            # even then, we can't do anything about it.
            if len(output) > 1:
                print("Error: Length of output is greater than expected!")
            self.elements[-2].data = output[0]
            self.elements[-2].text.setText(output[0].data.decode("utf-8"))
