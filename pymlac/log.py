#!/usr/bin/env python

"""
A simple logger.

TODO: Use python logging, etc.
"""


import os
import sys
import datetime
import traceback


# maximum length of filename (enforced)
MaxNameLength = 15


################################################################################
# A simple logger.
#
# Simple usage:
#     import log
#     log = log.Log('my_log.log', log.Log.DEBUG)
#     log('A line in the log at the default level (DEBUG)')
#     log('A log line at WARN level', Log.WARN)
#     log.debug('log line issued at DEBUG level')
#
# Based on the 'borg' recipe from [http://code.activestate.com/recipes/66531/].
#
# Log levels styled on the Python 'logging' module.
################################################################################

class Log(object):

    __shared_state = {}                # this __dict__ shared by ALL instances

    # the predefined logging levels
    CRITICAL = 50
    ERROR = 40
    WARN = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    _level_num_to_name = {NOTSET: 'NOTSET',
                          DEBUG: 'DEBUG',
                          INFO: 'INFO',
                          WARN: 'WARN',
                          ERROR: 'ERROR',
                          CRITICAL: 'CRITICAL'}

    def __init__(self, logfile=None, level=NOTSET, append=False):
        """Initialise the logging object.

        logfile the path to the log file
        level   logging level - don't log below this level
        append  True if log file is appended to
        """

        # make sure we have same state as all other log objects
        self.__dict__ = Log.__shared_state

        # don't allow logfile to change after initially set
        if not hasattr(self, 'logfile'):
            if logfile is None:
                logfile = '%s.log' % __name__
            try:
                if append:
                    self.logfd = open(logfile, 'a')
                else:
                    self.logfd = open(logfile, 'w')
            except IOError:
                # assume we have readonly filesystem
                basefile = os.path.basename(logfile)
                if sys.platform == 'win32':
                    #logfile = r'C:\%s' % basefile
                    logfile = os.path.join('C:\\', basefile)
                else:
                    #logfile = '~/%s' % basefile
                    logfile = os.path.join('~', basefile)

            # try to open logfile again
            if append:
                self.logfd = open(logfile, 'a')
            else:
                self.logfd = open(logfile, 'w')

            self.logfile = logfile
            self.level = level

            self.critical('='*55)
            self.critical('Log started on %s, log level=%s'
                 % (datetime.datetime.now().ctime(),
                    Log._level_num_to_name[level]))
            self.critical('-'*55)

    def __call__(self, msg=None, level=None):
        """Call on the logging object.

        msg    message string to log
        level  level to log 'msg' at (if not given, assume self.level)
        """

        # get level to log at
        if level is None:
            level = self.level

        # are we going to log?
        if level < self.level:
            return

        if msg is None:
            msg = ''

        # get time
        to = datetime.datetime.now()
        hr = to.hour
        min = to.minute
        sec = to.second
        msec = to.microsecond

        # caller information - look back for first module != <this module name>
        frames = traceback.extract_stack()
        frames.reverse()
        try:
            (_, mod_name) = __name__.rsplit('.', 1)
        except ValueError:
            mod_name = __name__
        for (fpath, lnum, mname, _) in frames:
            (fname, _) = os.path.basename(fpath).rsplit('.', 1)
            if fname != mod_name:
                break

        # get string for log level
        loglevel = Log._level_num_to_name[level]

        fname = fname[:MaxNameLength]
        self.logfd.write('%02d:%02d:%02d.%06d|%8s|%*s:%-4d|%s\n'
                         % (hr, min, sec, msec, loglevel, MaxNameLength, fname,
                            lnum, msg))
        self.logfd.flush()

    def critical(self, msg):
        """Log a message at CRITICAL level."""

        self(msg, Log.CRITICAL)

    def error(self, msg):
        """Log a message at ERROR level."""

        self(msg, Log.ERROR)

    def warn(self, msg):
        """Log a message at WARN level."""

        self(msg, Log.WARN)

    def info(self, msg):
        """Log a message at INFO level."""

        self(msg, Log.INFO)

    def debug(self, msg):
        """Log a message at DEBUG level."""

        self(msg, Log.DEBUG)

    def __del__(self):
        self.logfd.close()

