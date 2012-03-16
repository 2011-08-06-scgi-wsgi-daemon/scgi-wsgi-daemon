# -*- mode: python; coding: utf-8 -*-
#
# Copyright 2011, 2012 Andrej A Antonov <polymorphm@qmail.com>
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

UPLOAD_CONTENT_LENGTH_LIMIT = 2000000

class ScgiWsgiServer(object):
    _UPLOAD_CONTENT_LENGTH_LIMIT = UPLOAD_CONTENT_LENGTH_LIMIT
    
    def __init__(self, loop_idle, app, socket,
            inactive_guard=None,
            inactive_quit_time=None,
            loop_quit=None):
        assert inactive_guard is not None or \
                inactive_quit_time is None or \
                inactive_quit_time is not None and loop_quit is not None
        
        from .daemon import start_daemon
        
        if inactive_guard is None and inactive_quit_time is not None:
            from .inactive_guard import InactiveGuard
            
            inactive_guard = InactiveGuard(
                    loop_idle, loop_quit, inactive_quit_time)
        
        self._loop_idle = loop_idle
        self._app = app
        self._socket = socket
        self._inactive_guard = inactive_guard
        self._loop_quit = loop_quit
        self._is_started = False
    
    def _inactive_guard_event(self):
        if self._inactive_guard is not None:
            self._inactive_guard.event()
    
    def _inactive_guard_start(self):
        if self._inactive_guard is not None:
            self._inactive_guard.start()
    
    def _inactive_guard_stop(self):
        if self._inactive_guard is not None:
            self._inactive_guard.stop()
    
    def _format_scgi_error_response(self, text):
        data = 'Status: 500 Internal Server Error\r\n' \
                'Content-Type: text/plain;charset=utf-8\r\n' \
                '\r\n' + \
                text.encode('utf-8', 'replace')
        
        return data
    
    def _wsgi_wrap_daemon(self, fd, environ, upload_content, conn, address):
        from cStringIO import StringIO
        from sys import stderr
        
        assert environ.get('REQUEST_METHOD')
        if 'SCRIPT_NAME' not in environ:
            environ['SCRIPT_NAME'] = ''
        if 'PATH_INFO' not in environ:
            environ['PATH_INFO'] = ''
        assert environ.get('SERVER_NAME')
        assert environ.get('SERVER_PORT')
        
        environ['wsgi.version'] = (1, 0)
        environ['wsgi.url_scheme'] = 'https' \
                if environ.get('HTTPS', 'off') in ('on', '1') else 'http'
        environ['wsgi.input'] = StringIO(upload_content)
        environ['wsgi.errors'] = stderr
        environ['wsgi.multithread'] = True
        environ['wsgi.multiprocess'] = False
        environ['wsgi.run_once'] = False
        
        environ['scgi_wsgi_daemon.loop_idle'] = self._loop_idle
        environ['scgi_wsgi_daemon.loop_quit'] = self._loop_quit
        environ['scgi_wsgi_daemon.inactive_guard'] = self._inactive_guard
        environ['scgi_wsgi_daemon.fd'] = fd
        environ['scgi_wsgi_daemon.upload_content'] = upload_content
        environ['scgi_wsgi_daemon.conn'] = conn
        environ['scgi_wsgi_daemon.address'] = address
        
        headers_set = []
        headers_sent = []
        
        def write(data):
            assert headers_set, u'write() before start_response()'
            
            if not headers_sent:
                status, response_headers = headers_sent[:] = headers_set
                
                fd.write('Status: ' + status + '\r\n')
                for header_name, header_value in response_headers:
                    fd.write(header_name + ': ' + header_value + '\r\n')
                fd.write('\r\n')
            
            fd.write(data)
            fd.flush()
        
        def start_response(status, response_headers, exc_info=None):
            if exc_info is not None:
                try:
                    raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    exc_info = None
            
            assert not headers_set, u'Headers already set!'
            
            headers_set[:] = status, response_headers
            
            return write
        
        try:
            result = self._app(environ, start_response)
            try:
                for data in result:
                    if data:
                        write(data)
                if not headers_sent:
                    write('')
            finally:
                fd.close()
                conn.close()
                
                if hasattr(result, 'close'):
                    result.close()
        except:
            from traceback import format_exc
            
            error_text = unicode(format_exc())
            data = error_text.encode('utf-8', 'replace')
            
            if not headers_sent:
                headers_set[:] = \
                        'Status: 500 Internal Server Error', \
                        (('Content-Type', 'text/plain;charset=utf-8'),)
            write(data)
    
    def _conn_daemon(self, conn, address):
        fd = conn.makefile('b')
        
        try:
            def read_until(until_str):
                read_str = ''
                
                while True:
                    byte = fd.read(1)
                    if byte:
                        read_str += byte
                        if read_str.endswith(until_str):
                            result = read_str[:-len(until_str)]
                            
                            return result
                    else:
                        break
            
            all_size_str = read_until(':')
            assert all_size_str is not None
            all_size = int(all_size_str)
            
            headers_buf = fd.read(all_size)
            assert len(headers_buf) == all_size
            headers_sep = fd.read(1)
            assert headers_sep == ','
            
            environ_list = headers_buf.split('\0')
            assert not environ_list[-1]
            environ_list = environ_list[:-1]
            environ = {}
            while environ_list:
                key = environ_list.pop(0)
                value = environ_list.pop(0)
                environ[key] = value
            content_length = int(environ['CONTENT_LENGTH'])
            
            if content_length <= self._UPLOAD_CONTENT_LENGTH_LIMIT:
                upload_content = fd.read(content_length)
            else:
                error_text = u'Error: Upload too large'
                error_data = self._format_scgi_error_response(error_text)
                
                fd.write(error_data)
                fd.flush()
                
                return
            
            self._wsgi_wrap_daemon(fd, environ, upload_content, conn, address)
        except:
            from traceback import format_exc
            
            error_text = unicode(format_exc())
            error_data = self._format_scgi_error_response(error_text)
            
            fd.write(error_data)
            fd.flush()
    
    def _socket_accept_daemon(self):
        from socket import timeout
        
        try:
            conn, address = self._socket.accept()
        except timeout:
            self._loop_idle(self._socket_accept, None)
        else:
            self._loop_idle(self._socket_accept, (conn, address))
    
    def _socket_accept(self, accept_result):
        if self._is_started:
            from .daemon import start_daemon
            
            if accept_result is not None:
                self._inactive_guard_event()
                
                conn, address = accept_result
                start_daemon(self._loop_idle, self._conn_daemon, conn, address)
            
            start_daemon(self._loop_idle, self._socket_accept_daemon)
    
    def start(self):
        if not self._is_started:
            from .daemon import start_daemon
            
            self._is_started = True
            self._inactive_guard_start()
            
            start_daemon(self._loop_idle, self._socket_accept_daemon)
    
    def stop(self):
        self._is_started = False
        self._inactive_guard_stop()
