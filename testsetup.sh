#!/bin/bash
## begin license ##
#
# "Seecr Deps" to handle dependencies in python projects.
#
# Copyright (C) 2014-2015 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Seecr Deps"
#
# "Seecr Deps" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Seecr Deps" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Seecr Deps"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

set -e
mydir=$(cd $(dirname $0);pwd)

source /usr/share/seecr-tools/functions.d/test

rm -rf tmp build

definePythonVars

$PYTHON setup.py install --root tmp
cp -r test tmp/test

removeDoNotDistribute tmp
find tmp -type f -exec sed -e "
    s,^binDir = .*$,binDir = '$mydir/tmp/usr/local/bin',;
    " -i {} \;

export SEECRTEST_USR_BIN="${mydir}/tmp/usr/bin"
if [ -z "$@" ]; then
    runtests "alltests.sh"
else
    runtests "$@"
fi

rm -rf tmp build
