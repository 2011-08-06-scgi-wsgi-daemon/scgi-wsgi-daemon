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

def run(app,
            socket=None,
            socket_path=None,
            lock_path=None,
            pid_path=None,
            socket_backlog=None,
            use_daemonize=None,
            inactive_guard=None,
            inactive_quit_time=None,
            loop_idle=None,
            loop_quit=None,
        ):
    from .safe_print import safe_print
    from .scgi_wsgi_server import ScgiWsgiServer
    
    assert socket is not None or socket_path is not None
    
    if use_daemonize is None:
        use_daemonize = False
    
    if lock_path is not None:
        from .lock import new_lock_fd, NBLockError
        
        try:
            lock = new_lock_fd(lock_path, ex=True, nb=True)
        except NBLockError:
            from sys import stderr
            safe_print(u'Another scgi-wsgi-daemon is already running',
                    file=stderr)
            exit(1)
    
    if socket is None:
        from .unix_socket import new_unix_socket
        
        safe_print(u'Initializing UNIX socket...')
        socket = new_unix_socket(socket_path, socket_backlog=socket_backlog)
    
    if use_daemonize:
        from .daemonize import daemonize
        
        safe_print(u'Daemonize...')
        daemonize()
    else:
        safe_print(u'Listening...')
    
    if pid_path is not None:
        from .write_pid import write_pid
        
        write_pid(pid_path)
    
    if loop_idle is None:
        from .loop import Loop
        
        main_loop = Loop()
        loop_idle = main_loop.idle
        loop_quit = main_loop.quit
    else:
        main_loop = None
    
    server = ScgiWsgiServer(loop_idle, app, socket,
            inactive_guard=inactive_guard,
            inactive_quit_time=inactive_quit_time,
            loop_quit=loop_quit)
    
    server.start()
    
    if main_loop is not None:
        main_loop.run()
