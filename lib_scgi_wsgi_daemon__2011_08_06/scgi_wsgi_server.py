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

def run_scgi_wsgi_server(loop_idle, app, socket,
        inactive_guard=None,
        inactive_quit_time=None,
        loop_quit=None,
        start_daemon=None):
    assert inactive_guard is not None or \
            inactive_quit_time is None or \
            inactive_quit_time is not None and loop_quit is not None
    
    if inactive_guard is None and inactive_quit_time is not None:
        from .inactive_guard import InactiveGuard
        
        inactive_guard = InactiveGuard(loop_idle, loop_quit, inactive_quit_time)
        inactive_guard.start()
    
    if start_daemon is None:
        from .daemon import start_daemon
    
    pass # TODO: ...
