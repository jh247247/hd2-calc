#!/usr/bin/python3.3
import sys
import subprocess
import threading
import queue as Queue
import time

class nonBlockingSubprocess:
    outputQueue = Queue.Queue()
    queueHasData = threading.Event()
    def __init__(self, command):
        # Make process from given command
        self.__process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE)
        # Make independent thread for command.
        self.thread = threading.Thread(target=self.__enqueue_output,
                                  args=(self.__process.stdout,
                                        self.outputQueue))
        self.thread.daemon = True # thread dies with the program
        self.thread.start()

    # Helper function for the thread
    # reads the output of the process and pushes it onto the queue.
    def __enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
            self.queueHasData.set(); # queue no longer empty...

    # Output of process if buffered, so we kind of need this...
    def getline(self):
        retval = self.outputQueue.get_nowait()
        if self.outputQueue.empty():
            self.queueHasData.clear()
        return retval

    def hasData(self):
        return self.queueHasData.isSet()

    def write(self, input):
        self.__process.stdin.write(bytes(input,'utf-8'))

    def getProcessEvent(self):
        return self.queueHasData

# this is an automated test of this module.
def main():
    maxima = nonBlockingSubprocess(["maxima", "-q"])

    #makes things nicer to parse.
    maxima.write("display2d: false$");

    #read line without blocking
    i = 0
    while i != 5:
        try:
            line = maxima.getline()
        except Queue.Empty:
            maxima.write("integrate(sin(x),x);");
            time.sleep(1)
            i += 1
        else: # got line
            print(line)

if __name__ == '__main__':
    main()
