#!/bin/bash
## begin license ##
#
# Seecr Functools a set of various functional tools
#
# Copyright (C) 2017-2018 Seecr (Seek You Too B.V.) https://seecr.nl
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

export LANG=en_US.UTF-8
export PYTHONPATH=.:"$PYTHONPATH"
export WEIGHTLESS_COMPOSE_TEST="PYTHON"
export TESTMODE=true

python2.7 _alltests.py "$@"
