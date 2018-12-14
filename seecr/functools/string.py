## begin license ##
#
# Seecr Functools a set of various functional tools
#
# Copyright (C) 2018 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Seecr Functools"
#
# "Seecr Functools" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Seecr Functools" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Seecr Functools"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from .core import reduce

def strip(s, chars=None):
    """
    Return a string with leading and trailing characters removed. If chars is None, whitespace characters are removed. If given chars must be a string (or unicode).
    """
    return s.strip(chars)

def rstrip(s, chars=None):
    """
    Return a string with trailing characters removed. If chars is None, whitespace characters are removed. If given chars must be a string (or unicode).
    """
    return s.rstrip(chars)

def split(s, sep, maxsplit=-1):
    """
    Return an iterable of the words of the string s:
     - sep:
       Specifies a string to be used as the word separator (required);

     - maxsplit:
       * Absent or -1:
         All possible splits are made.

       * Present:
         At most maxsplit number of splits occur, and the remainder of the string is returned as the final element.

    The returned iterable will then have one more item than the number of non-overlapping occurrences of the separator.

    Splitting of an empty string will always result in an empty string.

    If s is given, operate on that string, otherwise returns a transducer.
    """
    if sep is None:
        raise ValueError('separator must not be None')

    return s.split(sep, maxsplit)
