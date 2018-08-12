################################################################################
#This file contains functions to put data into and retrieve data from byte
#arrays when sending messages over a network.
#
# Copyright (c) 2013 Bernhard Firner
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

def packuint128(val)
  """Function to cover for lack of uint128 value"""
  #TODO There is no 128 bit type, so pad with zeros for now
  return struct.pack('!QQ', 0, val)

#Unpack a uint128_t big-endian integer from the buffer
def unpackuint128(buff)
  """Function to cover for lack of uint128 value"""
  #TODO There is no 128 bit type, so discard the upper 4 bytes
  high, low = buff.unpack('QQ')
  return low
