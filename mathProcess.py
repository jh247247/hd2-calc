#!/usr/bin/python
import abc
import nonBlockingSubprocess
import time
import threading
import re
import uuid

try:
    import Queue
except ImportError:
    import queue as Queue


class mathElement(object):
    """
    Holder for the data returned by any type of math process.
    """
    # generate uuid for saving later.
    uuid = uuid.uuid1()
    def __init__(self, data=None, texOutput=None):
        """
        Constructor for each math element.
        :param data: Compulsory. What data was returned my the math process.
        :param texOutput: Tex representaion of data for rendering later.
        """
        self.data = data
        self.texOutput = texOutput

    def defined(self):
        if (self.data != None and
            self.texOutput != None):
            return True
        else:
            return False

    def __str__(self):
        """
        Return a string in the same format as was given by
        """
        return ("UUID: " + str(self.uuid) + "\n"
                "Data: " + str(self.data) + "\n" +
                "Tex: " + str(self.texOutput) + "\n")

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
            else:
                if clean != None:
                    self.cleanOutput.append(clean)

class maximaProcess(mathProcessBase):
    """
    Maxima implementation of the maxima parser.
    Needs some work, such as multiline responses and some error messages.
    """

    __process = nonBlockingSubprocess.nonBlockingSubprocess(["maxima","-q"])

    hasOutput = threading.Event()

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

        #self.__parseRegex = re.compile("\([%]([oi])([0-9]+)\)\s(.*?)$")

        # Put potential errors that the tex parser can return here.
        self.__errorTex = ['$$\mathbf{false}$$\n']

        # this variable will be set to true when tex mode is being parsed.
        self.texMode = False
        # This is the element being currently worked on.
        self.inProgress = mathElement()


    def __identParse(self, input):
        """
        Parse the identifier for the current mathElement.
        If we already have a identifier, discard whatever the ident for the given
        string and return the rest.
        """

        if input == None:
            return None

        # Search for a closing bracket, if we find one, return substring
        # after bracket.
        for i, c in enumerate(input):
            if chr(c) == ')':
                return input[i+1:].strip(b' \n')

            # No closing bracket found...
        return input

    def __texParse(self, input):
        # If input is a known error, tex output is nothing.
        if input in self.__errorTex:
            self.texMode = False
            self.inProgress.texOutput = ''

        # Check for tex identifiers. Set texMode to appropriate value.
        if chr(input[0]) == '$' and chr(input[-1]) == '$' \
           and len(input) is not 2:
            pass
        elif chr(input[0]) == '$':
            self.texMode = True
        elif chr(input[-1]) == '$':
            self.texMode = False

        # Append input string to end of texOutput.
        if self.inProgress.texOutput == None:
            self.inProgress.texOutput = input
        else:
            self.inProgress.texOutput += input

    def parse(self, input):
        """
        Implement the generic parser for output.
        Apply the regex and check it it spits anything out.
        If the parser doesn't spit anything out, test if it is tex output.
        If it is, add it to the tex field.
        If it isn't pass it onto another function for it to handle.
        """

        if self.texMode == False and self.inProgress.defined():
            print(self.inProgress)
            tempElement = self.inProgress
            self.inProgress = mathElement()
            self.hasOutput.set()
            return tempElement

        if input == None:
            return None

        input = input.strip(b' \n')
        if len(input) == 0:
            return None

        # parse identifier
        if chr(input[0]) == '(':
            input = self.__identParse(input)
            if len(input) == 0:
                return None

        # Check for tex input.

        if input[0:2] == b'$$' or self.texMode == True:
            self.__texParse(input)
            return None

        if self.inProgress.data == None:
            if input[0:5] == b'false':
                self.inProgress.data = input[5:]
            else:
                self.inProgress.data = input
        else:
            self.inProgress.data += input

        return None

    def write(self, input):
        input += '\n' # We don't want to care about the newline when we input
        self.__process.write(input)

        # We also want the tex output.
        self.__process.write('tex(%);\n')

        # NOTE: this is a blocking method. It WILL wait for output.
    def getOutput(self):
        # when we return, cleanOutput should be empty.
        self.hasOutput.wait()
        retVal = self.cleanOutput
        self.cleanOutput = []
        self.hasOutput.clear()
        return retVal

    # testcases...
def test():
    maxima = maximaProcess()
    # maxima.write(b"integrate(cos(x),x,);") # should print an error.
    # maxima.write(b"integrate(sin(x),x);") # should print -cos(x)

    maxima.write("diff(f(t),t,2);")
    maxima.write("laplace(%o2,t,s);")

    time.sleep(1)

    # we want to have many test cases later on.
    # there really should be a better way to do this though.
    i = 0;

    for output in maxima.getOutput():
        i += 1
        print('***** Result' + str(i) + ' *****\n' + str(output))

if __name__ == '__main__':
    test()
