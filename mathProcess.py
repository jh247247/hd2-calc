import abc
import nonBlockingSubprocess
import Queue
import time
import threading
import re


class mathElement(object):
    """
    Holder for the data returned by any type of math process.
    """
    def __init__(self, data, label=None, type=None):
        """
        Constructor for each math element.
        :param data: Compulsory. What data was returned my the math process.
        :param label: Optional. What label number this data has. What line
                      of outpout the REPL says it is.
        :param type: Optional. What type of data this contains; input, output or
                     something else.
        """
        self.data = data
        self.label = label
        self.type = type

class mathProcessBase(object):
    """
    Template for almost any type of math process that I am willing to target.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parse(self, input):
        """
        Generic parser for output of the math process
        """
        pass

    #TODO: modify this to parse multiple lines at a time.
    # Apparently it isn't wfast enough...
    def clean_output(self, process, queue):
        """
        Whenever the process has data, parse it.
        Apparently you need a poll delay otherwise it eats up CPU cycles like
        mad.
        """
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
                    self.cleanOutput.append(clean)

class maximaProcess(mathProcessBase):
    """
    Maxima implementation of the maxima parser.
    Needs some work, such as multiline responses and some error messages.
    """

    __process = nonBlockingSubprocess.nonBlockingSubprocess(["maxima","-q"])
    __parseRegex = re.compile("\([%]([oi])([0-9]+)\)\s?(.*?)$")
    cleanOutput = []


    def __init__(self):
        """
        Start up the maxima subProcess using nonBlockingSubprocess.
        Set some sane defaults so it wil be easy to parse later on.
        """
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
        """
        Implement the generic parser for output.
        Apply the regex and check it it spits anything out.
        """
        # if we get none, return none...
        if input == None:
            return None

        # split string up into 2 parts, identifier and expression
        out = self.__parseRegex.search(input)
        # this should NEVER HAPPEN!
        # (although it will happen with errors where maxima points out errors..)
        if out == None:
            # we know that there is something since input isn't None
            # so concatenate it with data!
            if len(self.cleanOutput) != 0:
                self.cleanOutput[len(self.cleanOutput) -1].data += str(input)
            return None

        # only has the label type and num, not valid.
        if len(out.groups()) == 2:
            return None

        return mathElement(out.groups()[2], out.groups()[1], out.groups()[0])

    def write(self, input):
        self.__process.write(input)

    def waitForOutput(self):
        while(len(self.cleanOutput) == 0): time.sleep(0.01)


maxima = maximaProcess()

maxima.write(b"integrate(cos(x),x,);\n") # should print an error.
maxima.write(b"integrate(sin(x),x);\n") # should print -cos(x)

maxima.waitForOutput()
print("Result1: " + str(maxima.cleanOutput.pop().data))
maxima.waitForOutput()
print("Result2: " + str(maxima.cleanOutput.pop().data))
