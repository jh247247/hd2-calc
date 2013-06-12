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
    def __init__(self, data, label=None, type=None,texOutput=None):
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
        self.texOutput = texOutput

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
    # Apparently it isn't fast enough...
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
                process.queueHasData.wait()
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
#    __texRegex = re.compile("[$$]?(.*?)[$$]?$")
    __errorTex = '$$\mathbf{false}$$\n'
    hasDataEvent = threading.Event()
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
        self.texMode = False

    def parseTex(self, input):
        if input == self.__errorTex:
            return ''

        # Dont want no newlines here!
        input = input.rstrip()

        # if input is invalid ()
        if input == '':
            return None

        if input[len(input)-1] == '$':
            self.texMode = False
        elif input[0] == '$':
            self.texMode = True
        elif self.texMode == False:
            return None
        else:
            return input



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

        # This will happen on multiline returns.
        if out == None:
            tex =  self.parseTex(input)
            if tex != None:
                self.cleanOutput[len(self.cleanOutput) -1].texOutput = tex
                return None

            # we know that there is something since input isn't None
            # so concatenate it with data!
            if len(self.cleanOutput) != 0:
                self.cleanOutput[len(self.cleanOutput) -1].data += '\n' + input.rstrip('\n')
            return None

        # allocate memory early so we don't have to worry later.
        outputList = out.groups()

        # only has the label type and num, not valid.
        if len(outputList) == 2 or outputList[2] == 'false' or len(outputList[2]) == 0:
            return None

        tex = self.parseTex(outputList[2])
        if tex != None:
            self.cleanOutput[len(self.cleanOutput) -1].texOutput = tex
            return None

        return mathElement(outputList[2], outputList[1], outputList[0])

    def write(self, input):
        input += '\n' # We don't want to care about the newline when we input
        self.__process.write(input)

        # We also want the tex output.
        self.__process.write('tex(%);\n')

    def getOutput(self):
        return self.cleanOutput

    # testcases...
def test():
    maxima = maximaProcess()

    maxima.write(b"integrate(cos(x),x,);") # should print an error.
    maxima.write(b"integrate(sin(x),x);") # should print -cos(x)

    while len(maxima.getOutput()) < 2:
        pass

    # we want to have many test cases later on.
    # there really should be a better way to do this though.
    i = 0;

    for output in maxima.getOutput():
        i += 1
        print('Result' + str(i) + ': ')
        print(output.data)
        print(output.texOutput)

if __name__ == '__main__':
    test()
