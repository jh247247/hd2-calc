#!/usr/bin/python
import os
import sys
from PyQt4 import QtCore, QtGui
from threading import Timer
import settings
from elementHandler import ElementHandler, GuiMathElement
import mathProcess
import uuid
import mathRender

BACKUP_DIR_NAME = '/tmp/maxima/'

class MaximaElementHandler(ElementHandler):
    maxima = mathProcess.maximaProcess()

    def __init__(self, statusHandler=None):
        """
        Creates a list for storing the individual gui elements
        Might need restructuring later down the line for the math stuff,
        but this will do for now.
        """
        super(MaximaElementHandler,self).__init__()
        self.status = statusHandler

        # make backup dir
        if not os.path.exists(BACKUP_DIR_NAME):
            os.makedirs(BACKUP_DIR_NAME)

    def appendElement(self):
        super(MaximaElementHandler, self).appendElement()
        if len(self.elements) > 1:

            self.status.setMessage("Evaluating...")

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
            # set the textbox contents to what we receive.
            #self.elements[-2].text.setText(output[0].data.decode("utf-8"))

            self.saveElement(self.elements[-2])

            self.status.clearMessage()

    def renderTexOutput(self, element):
        # have to have some GUI stuff in here to hold the pic.
        elementDir = BACKUP_DIR_NAME + str(element.data.uuid) + '/'

        # make backup dir from uuid
        if not os.path.exists(elementDir):
            os.makedirs(elementDir)

        mathRender.render(element.data.texOutput, elementDir)

        # load up the output as an impage in the gui element.
        # Remember that output is always 1.png.
        outputImage = elementDir + mathRender.OUTPUT_PREFIX + '1.png'

        element.loadImage(outputImage)

    def saveElement(self, element):
        elementDir = BACKUP_DIR_NAME + str(element.data.uuid) + '/'
        # make backup dir from uuid
        if not os.path.exists(elementDir):
            os.makedirs(elementDir)

        # write data
        with open(elementDir + 'data', 'w+') as f:
            f.write(element.data.data.decode('utf-8') + '\n')

        # write TeX
        with open(elementDir + 'TeX', 'w+') as f:
            f.write(element.data.texOutput.decode('utf-8') + '\n')

        # render tex output to the same directory.
        self.renderTexOutput(element)
