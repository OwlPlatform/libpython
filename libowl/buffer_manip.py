################################################################################
#This file contains functions to put data into and retrieve data from byte
#arrays when sending messages over a network.
#
# Copyright (c) 2018 Bernhard Firner
# All rights reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# or visit http://www.gnu.org/licenses/gpl-2.0.html
#
################################################################################

def splitURIFromRest(buff):
  """Take in a buffer with a sized URI in UTF 16 format.
  Return the string that was at the beginning of the buffer and
  the rest of the buffer after the string"""
  #The first four bytes are for the length of the string
  strlen = struct.unpack('!L', buff[0:4])[0]
  bstr = buff[4:4+strlen]
  #Make another container for everything after the string
  rest = buff[4+strlen:]
  return bstr.decode('utf-16'), rest
