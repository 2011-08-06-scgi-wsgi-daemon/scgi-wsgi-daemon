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

class Loop(object):
    def __init__(self):
        from Queue import Queue
        
        self._queue = Queue()
    
    def idle(self, target, *args, **kwargs):
        self._queue.put((target, args, kwargs))
    
    def run(self):
        while True:
            idle = self._queue.get()
            try:
                if idle:
                    target, args, kwargs = idle
                    target(*args, **kwargs)
                else:
                    break
            finally:
                self._queue.task_done()
    
    def quit(self):
        self._queue.put(None)
