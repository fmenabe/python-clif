import sys
import time
import threading
import itertools
import unix.shell as shell
import clif.logger as logger
from contextlib import contextmanager

_SELF = sys.modules[__name__]

class Spinner(threading.Thread):
    spinner = itertools.cycle(['-', '\\', '|', '/'])

    def __init__(self, msg=None):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.msg = msg
        self.errors = []

    def _clean(self):
        sys.stdout.write('\033[0G%s' % (' ' * shell.width()))
        sys.stdout.flush()
        sys.stdout.write('\033[0G')
        sys.stdout.flush()

    def run(self):
        while not self._stop_event.isSet():
            # Just wait for a message or a stop
            if self.msg is not None:
                self._clean()
                sys.stdout.write("\033[0G%s %s" % (next(self.spinner), self.msg))
                sys.stdout.flush()
            self._stop_event.wait(0.1)

        self._clean()
        if self.errors:
            for error in self.errors:
                logger.error(error)
        sys.stdout.flush()

    def stop(self):
        self._stop_event.set()
        self.msg = None
        time.sleep(0.1)

    def info(self, msg):
        self.msg = msg
        time.sleep(0.2)

    def error(self, msg, quit=True):
        self.errors.append(msg)
        if quit:
            sys.exit(1)

def init():
    spinner = Spinner()
    spinner.start()
    setattr(_SELF, 'spinner', spinner)

stop = lambda: spinner.stop()
info = lambda msg: spinner.info(msg)
error = lambda msg, quit: spinner.error(msg, quit=quit)

@contextmanager
def spin():
    try:
        init()
        yield None
    except KeyboardInterrupt:
        sys.exit(1)
    finally:
        stop()
