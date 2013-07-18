from PyQt4 import QtCore, QtGui
# Setup fonts to use (Since this is a high DPI device)
# Can be changed to suit tastes I guess...
FONT_STATUS = QtGui.QFont('Serif', 15, QtGui.QFont.Light)
FONT_GENERAL = QtGui.QFont('Serif', 15, QtGui.QFont.Light)
FONT_GENERAL_METRICS = QtGui.QFontMetrics(FONT_GENERAL)

SCROLLBAR_WIDTH = 30 # width of vertical scrollbar in pixels.
# this is for touchscreen interfaces.
