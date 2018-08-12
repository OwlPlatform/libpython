#This class abstracts the details of connecting to a
#GRAIL3 aggregator as a solver.
#Solvers subscribe to the aggregator and then receive packets.

import struct
import socket
import sensor_sample as samples

class IDMask:
  #Takes in id and mask numbers
  def __init__(self, sensor_id, mask = 0xFFFFFFFF):
    """ID and mask for rule matching in the aggregator."""
    # Leave the upper 8 bytes 0 since we aren't support 128bit values.
    self.id = struct.pack('!QQ', 0, sensor_id)
    self.mask = struct.pack('!QQ', 0, mask)

class AggrRule:
  #Physical layer (1 byte), an array of transmitter/mask values, and an 8-byte update interval in milliseconds
  def __init__(self, phy_layer, txers, update_interval):
    self.phy_layer = phy_layer
    self.txers = txers
    self.update_interval = update_interval

class SolverAggregator:
  #Message constants
  KEEP_ALIVE            = 0
  CERTIFICATE           = 1
  ACK_CERTIFICATE       = 2 #There is no message for certificate denial
  SUBSCRIPTION_REQUEST  = 3
  SUBSCRIPTION_RESPONSE = 4
  DEVICE_POSITION       = 5
  SERVER_SAMPLE         = 6
  BUFFER_OVERRUN        = 7

  def __init__(self, host, port):
    self.connected = False
    self.host = host
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if self.socket is None:
        raise RuntimeError("Unable to create solver-aggregator socket!")
    self.socket.connect((host, port))
    # Make the solver-aggregator handshake
    handshake = b''
    ver_string = "GRAIL solver protocol"
    #The handshake is the length of the message, the protocol string, and the version (0).
    handshake += struct.pack('!L', len(ver_string))
    handshake += ver_string.encode('utf-8')
    handshake += b'\x00\x00'
    #Receive a handshake and then send one
    #TODO Should verify the bytes of the received message
    remote_handshake = self.socket.recv(len(handshake))
    if len(handshake) != len(remote_handshake):
        raise RuntimeError("Got bad handshake from aggregator!")
    # Return the handshake
    self.socket.send(handshake)
    self.connected = True

    self.available_packets = []
    self.cur_rules = []

  def close(self):
    """Close the connected socket."""
    self.socket.close()
    self.connected = False

  def handleMessage(self):
    """Handle the next message (currently of type unknown)"""
    # Get the message length
    in_bytes = self.socket.recv(4)
    # Session ends of the packet is malformed or no data is read
    if 4 != len(in_bytes):
        self.close()
        print("Solver Aggregator connection closed")
        return None
    inlen = struct.unpack('!L', (in_bytes))[0]
    # Attempt to receive the packet
    inbuff = self.socket.recv(inlen)
    # The next byte indicates the message type
    control = inbuff[0]
    if self.SUBSCRIPTION_RESPONSE == control:
      self.decodeSubResponse(inbuff[1:])
      return self.SUBSCRIPTION_RESPONSE
    elif self.SERVER_SAMPLE == control:
      self.decodeServerSample(inbuff[1:])
      return self.SERVER_SAMPLE
    else:
      # Other message (like keep alive) require no processing
      # TODO Check that this was a valid message type
      return control

  def decodeSubResponse(self, inbuff):
    """Decode a subscription response and store the current rules in
       self.cur_rules"""
    print("Got subscription response!")
    num_rules = struct.unpack('!L', inbuff[0:4])[0]
    rest = inbuff[4:]
    rules = []
    for i in range(num_rules):
      phy_layer, num_txers = struct.unpack('!BL', rest[0:5])
      txlist = []
      rest = rest[5:]
      for j in range(num_txers):
        txlist.append(rest[0:32])
        rest = rest[32:]
      update_interval = struct.unpack('!Q', rest[0:8])[0]
      rest = rest[8:]
      rule = AggrRule(phy_layer, txlist, update_interval)
      rules.append(rule)
    # Overwrite existing rules with new ones
    # TODO Verify that this is proper GRAIL behavior
    self.cur_rules = rules

  #Decode a server sample message
  def decodeServerSample(self, inbuff):
    """Decode a data message"""
    print("Decoding a server sample!")
    if (0 < len(inbuff)):
      phy_layer = inbuff[0]
      rest = inbuff[1:]
      txid = struct.unpack('!QQ', rest[0:16])
      rxid = struct.unpack('!QQ', rest[16:32])
      timestamp, rssi = struct.unpack('!df', rest[32:44])
      sense_data = rest[44:]
      self.available_packets.append(samples.SensorSample(phy_layer, txid, rxid, timestamp, rssi, sense_data))

  def sendSubscription(self, rules):
    """Subscribe to data from the aggregator"""
    # Start assembling a request message
    buff = struct.pack('!BL', self.SUBSCRIPTION_REQUEST, len(rules))
    for rule in rules:
      buff += struct.pack('!BL', rule.phy_layer, len(rule.txers))
      # Push each transmitter/mask pair
      for txer in rule.txers:
        buff += txer.id + txer.mask
      buff += struct.pack('!Q', rule.update_interval)
    # Send the message prepended with the length
    len_hdr = struct.pack('!L', len(buff))
    self.socket.send(len_hdr + buff)

    # Get the subscription response
    response = self.handleMessage()
    while (self.connected and
        self.SUBSCRIPTION_RESPONSE != response):
      response = self.handleMessage()
