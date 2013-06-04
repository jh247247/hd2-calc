import abc
import nonBlockingSubprocess
import Queue
import time
import threading
import re


# items for the math-type classes, holds the label no, type and data
# if type/label is not availible, these get set to none
class mathElement(object):
    def __init__(self, data, label=None, type=None):
        self.data = data
        self.label = label
        self.type = type

class mathProcessBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parse(self, input):
        pass

    def clean_output(self, process, queue):
        while True:
            try:
                dirty = process.getline()
                clean = self.parse(dirty)
            except Queue.Empty:
                time.sleep(0.1) # give up processing time?
            except ValueError as inst:
                print("Error: " + str(inst))
                pass
            else:
                if clean != None:
                    self.cleanOutput.put(clean)

class maximaProcess(mathProcessBase):
    __process = nonBlockingSubprocess.nonBlockingSubprocess(["maxima","-q"])
    __parseRegex = re.compile("\([%]([oi])([0-9]+)\)\s?(.*?)$")
    cleanOutput = Queue.Queue()


    def __init__(self):
        # make things easier to parse.
        self.__process.write("display2d: false$")
        self.thread = threading.Thread(target=self.clean_output,
                                       args=(self.__process,
                                             self.cleanOutput))
        self.thread.daemon = True # thread dies with the program
        self.thread.start()

    # TODO: make this handle maxima errors (which span more than one line...)
    # usually something like: (%iN) (ErrorMessage)
    # (WrongInput)
    # hat showing where error is.

    # (I think we can just get rid of the last 2 lines, just need the error)
    # Fixed regex: \([%]([oi])([0-9]+)\)\s?(.*?)$
    def parse(self, input):
        # split string up into 2 parts, identifier and expression
        out = self.__parseRegex.search(input)
        # this should NEVER HAPPEN!
        # (although it will happen with errors where maxima points out errors..)
        if out == None:
            return None

        # only has the label type and num, not valid.
        if len(out.groups()) == 2:
            return None

        return mathElement(out.groups()[2], out.groups()[1], out.groups()[0])

    def write(self, input):
        self.__process.write(input)


maxima = maximaProcess()

maxima.write(b"integrate(cos(x),x,);\n") # should print an error.
maxima.write(b"integrate(sin(x),x);\n") # should print -cos(x)

print("Result1: " + str(maxima.cleanOutput.get().data))
print("Result2: " + str(maxima.cleanOutput.get().data))
