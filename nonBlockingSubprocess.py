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
    queueHasData = False
    def __init__(self, command):
        # Make process from given command
        self.__process = subprocess.Popen(command,
                                          stdout=subprocess.PIPE,
                                          stdin=subprocess.PIPE,
                                          bufsize=1,
                                          close_fds=ON_POSIX)

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
        # while(True):
        #     print(out.read())
        for output in iter(out.read, b''):
            if output is not None:
                output = output.split(b'\n')
                for i in output:
                    if i is not '':
                        queue.put(i)
                self.queueHasData = True # queue no longer empty...
            time.sleep(SUBPROCESS_POLL_DELAY)

    # Output of process if buffered, so we kind of need this...
    def getline(self):
        retval = None
        try:
            retval = self.outputQueue.get_nowait()
        except Queue.Empty:
            self.queueHasData = False
        return retval

    def hasData(self):
        return self.queueHasData

    def write(self, input):
        self.__process.stdin.write(bytearray(input,'utf-8'))
        self.__process.stdin.flush()

    def getProcessEvent(self):
        return self.queueHasData

# this is an automated test of this module.
def main():

    maxima = nonBlockingSubprocess(["maxima", "-q"])

    #makes things nicer to parse.
    maxima.write("display2d: false$\n")
    maxima.write("integrate(sin(x),x);\n")

    #read line without blocking
    i = 0
    for i in range(0,5):
        maxima.write("integrate(sin(x),x);\n")

    time.sleep(1)
    while True:
        line = maxima.getline()
        if line is not None:
            print(line)
        if maxima.hasData() is False:
            quit()

if __name__ == '__main__':
    main()
