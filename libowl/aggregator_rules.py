import struct

class IDMask
  #Takes in id and mask numbers
  def __init__(sensor_id, mask = 0xFFFFFFFF)
    self.id = struct.pack('!QQ', 0, sensor_id)
    self.mask = struct.pack('!QQ', 0, mask)

class AggrRule
  #Physical layer (1 byte), an array of transmitter/mask values, and an 8-byte update interval in milliseconds
  def __init__(phy_layer, txers, update_interval)
    self.phy_layer = phy_layer
    self.txers = txers
    self.update_interval = update_interval
