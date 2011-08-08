# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2011 Andrej A Antonov <polymorphm@qmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
assert unicode is not str

class InactiveGuard(object):
    def __init__(self, loop_idle, loop_quit, quit_time_len):
        self._time = None
        self._loop_idle = loop_idle
        self._loop_quit = loop_quit
        self._quit_time_len = quit_time_len
        self._is_started = False
    
    def _sleep_daemon(self):
        from time import sleep
        
        sleep(self._quit_time_len / 10.0)
        self._loop_idle(self._timeout)
    
    def _timeout(self):
        if self._is_started:
            from time import time
            from .daemon import start_daemon
            
            if abs(time() - self._time) < self._quit_time_len:
                start_daemon(self._loop_idle, self._sleep_daemon)
            else:
                self.stop()
                self._loop_quit()
    
    def event(self):
        from time import time
        
        self._time = time()
    
    def start(self):
        self.event()
        
        if not self._is_started:
            from .daemon import start_daemon
            
            self._is_started = True
            start_daemon(self._loop_idle, self._sleep_daemon)
    
    def stop(self):
        self._is_started = False
