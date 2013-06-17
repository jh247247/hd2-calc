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
    def __init__(self, data, label=None, type=None, texOutput=None):
        """
        Constructor for each math element.
        :param data: Compulsory. What data was returned my the math process.
        :param label: Optional. What label number this data has. What line
                      of outpout the REPL says it is.
        :param type: Optional. What type of data this contains; input, output or
                     something else.
        :param texOutput: Tex representaion of data for rendering later.
        """
        self.data = data
        self.label = label
        self.type = type
        self.texOutput = texOutput

    def __str__(self):
        """
        Return a string in the same format as was given by
        """
        return ("Type: " + str(self.type) + "\n"
                "Label: " +str(self.label) + "\n" +
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
                pass
            else:
                if clean != None:
                    self.cleanOutput.append(clean)

class maximaProcess(mathProcessBase):
    """
    Maxima implementation of the maxima parser.
    Needs some work, such as multiline responses and some error messages.
    """


    def __init__(self):
        """
        Start up the maxima subProcess using nonBlockingSubprocess.
        Set some sane defaults so it wil be easy to parse later on.
        """
        self.__process = nonBlockingSubprocess.nonBlockingSubprocess(["maxima","-q"])

        self.cleanOutput = []

        # make things easier to parse.
        self.__process.write("display2d: false$")
        self.thread = threading.Thread(target=self.clean_output,
                                       args=(self.__process,
                                             self.cleanOutput))
        self.thread.daemon = True # thread dies with the program
        self.thread.start()

        self.__parseRegex = re.compile("\([%]([oi])([0-9]+)\)\s?(.*?)$")

        # Put potential errors that the tex parser can return here.
        self.__errorTex = ['$$\mathbf{false}$$\n']

        # block while parsing output
        self.texMode = False

        self.parseDone = threading.Event()



    def __parseTex(self, input):

        if input in self.__errorTex:
            return ''

        # Dont want no newlines here!
        input = input.rstrip()

        # if input is invalid ()
        if len(input) == 0:
            return None

        # Check tex string end for status
        if input[-1] == '$' and input[0] != '$':
            self.texMode = False
            self.parseDone.set();
        elif input[0] == '$' and input[-1] != '$':
            # check tex string start for next line.
            self.texMode = True
        elif input[0] == '$' and input[-1] == '$':
            self.parseDone.set()
        elif self.texMode == False and input[0] != '$' and input[-1] != '$':
            return None

        return input

    def __parseRegexFail(self, input):
        """
        If regex for parsing falis, give it here and check whether or not it
        falls into any other categories.
        """
        # Output is tex. Need to add it to the end of the tex part.
        tex =  self.__parseTex(input)
        if self.__texAppend(input) == True:
            # If success, quit.
            return

        # we know that there is something since input isn't None
        # so concatenate it with data!
        if len(self.cleanOutput) != 0:
            self.cleanOutput[-1].data += '\n' + input.rstrip('\n')
            return

    def __texAppend(self, input):
        """
        This is only ever called to set the previous output.
        Appends the tex string given or creates it if it is None.
        """
        if input == None or len(self.cleanOutput) == 0:
            return False

        if self.cleanOutput[-1].texOutput == None:
            self.cleanOutput[-1].texOutput = input
        else:
            self.cleanOutput[-1].texOutput += input

        return True


    def parse(self, input):
        """
        Implement the generic parser for output.
        Apply the regex and check it it spits anything out.
        If the parser doesn't spit anything out, test if it is tex output.
        If it is, add it to the tex field.
        If it isn't pass it onto another function for it to handle.
        """

        # if we get none, return none...
        if input == None:
            return None

        # split string up into 2 parts, identifier and expression
        out = self.__parseRegex.search(input)

        # This will happen on multiline returns.
        if out == None:
            self.__parseRegexFail(input)
            return None

        # allocate memory early so we don't have to worry later.
        outputList = out.groups()

        # only has the label type and num, not valid.
        if (len(outputList) == 2 or
            outputList[2] == 'false' or
            len(outputList[2]) == 0):
            return None

        # wait a sec, this output looks like TEX!
        # If it gets here, it means that this is the first line of tex output.
        # So instead of adding, set the tex variable to this.
        tex = self.__parseTex(outputList[2])
        if self.__texAppend(tex) == True:
            return None

        return mathElement(outputList[2], outputList[1], outputList[0])

    def write(self, input):
        input += '\n' # We don't want to care about the newline when we input
        self.__process.write(input)

        # We also want the tex output.
        self.__process.write('tex(%);\n')

    def getOutput(self):
        self.parseDone.wait()
        # Quick hack to make sure the last element is fully defined.
        if self.cleanOutput[-1].texOutput == None:
            time.sleep(0.01); # kind of need a delay for more things to happen
            return self.getOutput()
        return self.cleanOutput

    # testcases...
def test():
    maxima = maximaProcess()

    # maxima.write(b"integrate(cos(x),x,);") # should print an error.
    # maxima.write(b"integrate(sin(x),x);") # should print -cos(x)

    maxima.write(b"diff(f(t),t,2);") # should print an error.
    maxima.write(b"laplace(%o2,t,s);") # should print an error.

    while len(maxima.getOutput()) < 2:
        pass


    # we want to have many test cases later on.
    # there really should be a better way to do this though.
    i = 0;

    for output in maxima.getOutput():
        i += 1
        print('***** Result' + str(i) + ' *****\n' + str(output))

if __name__ == '__main__':
    test()
