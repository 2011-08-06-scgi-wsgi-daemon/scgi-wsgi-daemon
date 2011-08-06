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

def daemonize():
    from os import (
        EX_OK,
        devnull,
        O_RDWR,
        fork,
        open as os_open,
        close as os_close,
    )
    
    if fork():
        exit(EX_OK)
    
    for fd in range(0, 3):
        try:
            os_close(fd)
        except OSError:
            pass
    
    os_open(devnull, O_RDWR)
    os_open(devnull, O_RDWR)
    os_open(devnull, O_RDWR)
