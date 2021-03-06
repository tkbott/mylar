# Author: Nic Wolfe <nic@wolfeden.ca>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import time
import threading
import traceback

from mylar import logger


class Scheduler:
    def __init__(self, action, cycleTime=datetime.timedelta(minutes=10), runImmediately=True,
                 threadName="ScheduledThread", silent=False, delay=None):

        if runImmediately:
            self.lastRun = datetime.datetime.fromordinal(1)
        else:
            self.lastRun = datetime.datetime.now()

        self.action = action
        self.cycleTime = cycleTime

        self.thread = None
        self.threadName = threadName
        self.silent = silent

        self.delay = delay

        self.initThread()
 
        self.abort = False

    def initThread(self):
        if self.thread == None or not self.thread.isAlive():
            self.thread = threading.Thread(None, self.runAction, self.threadName)

    def timeLeft(self):
        return self.cycleTime - (datetime.datetime.now() - self.lastRun)

    def forceRun(self):
        if not self.action.amActive:
            self.lastRun = datetime.datetime.fromordinal(1)
            return True
        return False

    def runAction(self):

        while True:

            currentTime = datetime.datetime.now()

            if currentTime - self.lastRun > self.cycleTime:
                self.lastRun = currentTime
                try:
                    if not self.silent:
                        logger.fdebug("Starting new thread: " + self.threadName)

                    if self.delay:
                        logger.info('delaying startup thread for ' + str(self.delay) + ' seconds to avoid locks.')
                        time.sleep(self.delay)

                    self.action.run()
                except Exception, e:
                    logger.fdebug("Exception generated in thread " + self.threadName + ": %s" % e )
                    logger.fdebug(repr(traceback.format_exc()))

            if self.abort:
                self.abort = False
                self.thread = None
                return

            time.sleep(1)
