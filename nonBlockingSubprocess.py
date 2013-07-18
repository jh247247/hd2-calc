#!/usr/bin/python3.3
import sys
import subprocess
import threading
# maintain some backwards compat.
try:
    import Queue
except ImportError:
    import queue as Queue

import time
import fcntl
import os

# How much time should we wait before polling
SUBPROCESS_POLL_DELAY = 0.25


ON_POSIX = 'posix' in sys.builtin_module_names

class nonBlockingSubprocess:
    outputQueue = Queue.Queue()
    queueHasData = threading.Event()
    def __init__(self, command):
        # Make process from given command
        self.__process = subprocess.Popen(command,
                                          stdout=subprocess.PIPE,
                                          stdin=subprocess.PIPE,
                                          bufsize=1)

        fcntl.fcntl(self.__process.stdout.fileno(),
                    fcntl.F_SETFL,
                    os.O_NONBLOCK)

        # Make independent thread for command.
        self.thread = threading.Thread(target=self.__enqueue_output,
                                  args=(self.__process.stdout,
                                        self.outputQueue))
        self.thread.daemon = True # thread dies with the program
        self.thread.start()

    # Helper function for the thread
    # reads the output of the process and pushes it onto the queue.
    def __enqueue_output(self, out, queue):
        while(True):
            try:
                for output in iter(out.readline, b''):
                    if output is not None:
                        output = output.split(b'\n')
                        for i in output:
                            if i is not '':
                                queue.put(i)
                                # queue no longer empty...
                                self.queueHasData.set()
                time.sleep(SUBPROCESS_POLL_DELAY)
            except IOError:
                # there is nothing to read right now (python 2.7 error)
                time.sleep(SUBPROCESS_POLL_DELAY)


    # Output of process if buffered, so we kind of need this...
    # This method is optionally blocking, if blocking is not desired,
    # set timeout to 0 as None means wait forever.
    def getline(self, timeout=None):
        self.queueHasData.wait(timeout)
        retval = None
        try:
            retval = self.outputQueue.get_nowait()
        except Queue.Empty:
            self.queueHasData.clear()
        return retval

    def hasData(self):
        return self.queueHasData.isSet()

    def write(self, input):
        print(bytearray(input,'utf-8'))
        self.__process.stdin.write(bytearray(input,'utf-8'))
        self.__process.stdin.flush()

    def getProcessEvent(self):
        return self.queueHasData

# this is an automated test of this module.
def main():

    maxima = nonBlockingSubprocess(["ls"])

    #makes things nicer to parse.
    maxima.write("display2d: false$\n")
    maxima.write("integrate(sin(x),x);\n")

    #read line without blocking
    i = 0
    for i in range(0,5):
        maxima.write("integrate(sin(x),x);\n")

    while True:
        line = maxima.getline()
        if line is not None:
            print(line)
        if maxima.hasData() == False:
            quit()

if __name__ == '__main__':
    main()
