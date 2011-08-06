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

def safe_print(*args, **kwargs):
    sep = kwargs.pop('sep', None)
    end = kwargs.pop('end', None)
    file = kwargs.pop('file', None)
    assert not kwargs
    
    if sep is None:
        sep = ' '
    if end is None:
        end = '\n'
    if file is None:
        from sys import stdout as sys_stdout
        file = sys_stdout
    
    def safe_conv(value):
        if isinstance(value, bytes):
            safe_value = value
        elif isinstance(value, unicode):
            safe_value = value.encode(file.encoding, 'replace')
        else:
            safe_value = unicode(value).encode(file.encoding, 'replace')
        
        return safe_value
    
    print_bytes = \
            safe_conv(sep).join(safe_conv(v) for v in args) + \
            safe_conv(end)
    
    file.write(print_bytes)
    file.flush()
