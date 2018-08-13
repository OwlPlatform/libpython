#This class abstracts the details of connecting to a
#GRAIL3 aggregator as a solver.
#Solvers subscribe to the aggregator and then receive packets.

import struct
import socket

import transient_request
import wm_data
import buffer_manip


class SolverWorldModel:
  #Message constants
  KEEP_ALIVE       = 0
  TYPE_ANNOUNCE    = 1
  START_TRANSIENT  = 2
  STOP_TRANSIENT   = 3
  SOLVER_DATA      = 4
  CREATE_URI       = 5
  EXPIRE_URI       = 6
  DELETE_URI       = 7
  EXPIRE_ATTRIBUTE = 8
  DELETE_ATTRIBUTE = 9
  VER_STRING = "GRAIL world model protocol"

  def __init__(self, host, port, origin, start_transient_callback = None, stop_transient_callback = None):
    # The origin string of this solver
    # This provides data provenance
    self.origin = origin
    self.connected = False
    self.host = host
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if self.socket is None:
        raise RuntimeError("Unable to create solver-aggregator socket!")
    self.socket.connect((host, port))
    handshake = b''
    # The handshake is the length of the message, the protocol string, and the version (0).
    handshake += struct.pack('!L', len(self.VER_STRING))
    handshake += self.VER_STRING.encode('utf-8')
    handshake += b'\x00\x00'
    # Send and receive handshakes
    self.socket.send(handshake)
    inshake = self.socket.recv(len(handshake))
    # TODO Can python's socket return without getting the full handshake?
    while (len(inshake) < len(handshake)):
      print ("Waiting for {} bytes more of handshake.".format(len(handshake) - len(inshake)))
      inshake += self.socket.recv(len(handshake) - len(inshake))

    self.connected = True
    if len(handshake) != len(inshake):
        raise RuntimeError("Solver-World Model handshake error! Verify world model port and url.")
    for i in range(len(handshake)):
      if handshake[i] != inshake[i]:
        self.connected = False
        raise RuntimeError("Solver-World Model handshake error! Verify world model port and url.")

    self.name_to_alias = {}
    self.alias_to_name = {}

    # Callback for when the world model requests transient data
    self.start_transient_callback = start_transient_callback
    # Callback for when the world model no longer wants a transient type
    self.stop_transient_callback = stop_transient_callback

  #Handle a message of currently unknown type
  def handleMessage(self):
    #Get the message length as n unsigned integer
    # Get the message length
    in_bytes = self.socket.recv(4)
    # Session ends of the packet is malformed or no data is read
    if 4 != len(in_bytes):
        self.close()
        print("Solver Aggregator connection closed")
        return None
    in_bytes = struct.unpack('!L', (in_bytes))[0]
    # Attempt to receive the packet
    inbuff = self.socket.recv(inlen)
    # The next byte indicates the message type
    control = inbuff[0]
    if control == self.START_TRANSIENT:
      if (self.start_transient_callback is not None):
        self.start_transient_callback.call(decodeStartTransient(inbuff[1:]))
    elif control == self.STOP_TRANSIENT:
      if (self.stop_transient_callback is not None):
        self.stop_transient_callback.call(decodeStopTransient(inbuff[1:]))
    return control

  def decodeStartTransient(self, inbuff):
    """Decode a start transient message"""
    num_aliases = struct.unpack('!L', inbuff[0:4])[0]
    rest = inbuff[4:]
    new_trans_requests = []
    for i in range(num_aliases):
      type_alias = struct.unpack('!L', rest[0:4])[0]
      total_expressions = struct.unpack('!L', rest[4:8])[0]
      t_request = TransientRequest(type_alias, [])
      rest = rest[8:]
      for j in range(total_expressions):
        exp, rest = buffer_manip.splitURIFromRest(rest)
        t_request.expressions.append(exp)
      new_trans_requests.append(t_request)
    return new_trans_requests

  def decodeStopTransient(self, inbuff):
    """Decode a stop transient message"""
    num_aliases = struct.unpack('!L', inbuff[0:4])[0]
    rest = inbuff[4:]
    new_trans_requests = []
    for i in range(num_aliases):
      type_alias = struct.unpack('!L', rest[0:4])[0]
      total_expressions = struct.unpack('!L', rest[4:8])[0]
      t_request = TransientRequest(type_alias, [])
      rest = rest[8:]
      for j in range(total_expressions):
        exp, rest = buffer_manip.splitURIFromRest(rest)
        t_request.expressions.append(exp)
      new_trans_requests.append(t_request)
    return new_trans_requests

  def close(self):
    """Close this connection"""
    self.socket.close()
    self.connected = False

  def addSolutionTypes(self, attributes, transient = False):
    """Add some SolutionType objects to the known list"""
    new_aliases = []
    for attr in attributes:
      # Add if this is new
      if (attr.name not in self.name_to_alias):
        new_alias = int(len(self.name_to_alias))
        self.name_to_alias[attr.name] = new_alias
        self.alias_to_name[new_alias] = attr.name
        # TODO This would be more readable as a map or actual type
        new_aliases.append([attr.name, new_alias, transient])
    # Need to let the world model know what types we can provide
    if (len(new_aliases) > 0):
      self.makeTypeAnnounce(new_aliases)

  def makeTypeAnnounce(self, type_info):
    """Send a message to the world model announcing the types provided by this
    solver and announcing the aliases from numbers to string to save space in
    future messages."""
    # Start assembling a type announce message
    buff = struct.pack('!BL', self.TYPE_ANNOUNCE, len(type_info))
    for info in type_info:
      # Pack the alias number, name as utf 16, and transient status
      buff += struct.pack('!L', info[1])
      type16 = info[0].encode('utf-16-be')
      buff += struct.pack('!L', len(type16))
      buff += type16
      buff += struct.pack('!B', info[2])
    #Add the origin string to the end of the message
    buff += self.origin.encode('utf-16-be')
    self.socket.send(struct.pack('!L', len(buff)) + buff)

  def pushData(self, wmdata_vector, create_uris = False):
    """Push URI attributes, automatically declaring new solution types
    as non-streaming, non-transient types if they were not previously
    declared."""
    buff = struct.pack('!BB', self.SOLVER_DATA, create_uris)

    # Find the total number of attributes being pushed
    total_solns = 0
    for wdata in wmdata_vector:
      total_solns += len(wdata.attributes)
    buff += struct.pack('!L', total_solns)

    #Now create each solution and push it back into the buffer
    for wmdata in wmdata_vector:
      #First make sure all of the solutions types have been declared
      self.addSolutionTypes(wmdata.attributes)
      #Now push back this attribute's data using an alias for the name
      for attr in wmdata.attributes:
        buff += struct.pack('!LQ', self.name_to_alias[attr.name], int(attr.creation))
        # The URI must be prepended with its size
        uri16 = wmdata.uri.encode('utf-16-be')
        buff += struct.pack('!L', len(uri16))
        buff += uri16
        buff += struct.pack('!L', len(attr.data))
        buff += attr.data
    #Send the message with its length prepended to the front
    self.socket.send(struct.pack('!L', len(buff)) + buff)

  ##
  #Create an object with the given name in the world model.
  def createURI(self, uri, creation_time):
    buff = struct.pack('!B', self.CREATE_URI)
    uri16 = uri.encode('utf-16-be')
    buff += struct.pack('!L', len(uri16))
    buff += uri16
    buff += struct.pack('!Q', creation_time)
    buff += self.origin.encode('utf-16-be')
    #Send the message with its length prepended to the front
    self.socket.send(struct.encode('!L', len(buff)) + buff)

  ##
  #Expire the object with the given name in the world model, indicating that it
  #is no longer valid after the given time.
  def expireURI(self, uri, expiration_time):
    buff = struct.pack('!B', self.EXPIRE_URI)
    uri16 = uri.encode('utf-16-be')
    buff += struct.pack('!L', len(uri16))
    buff += uri16
    buff += struct.pack('!Q', expiration_time)
    buff += self.origin.encode('utf-16-be')
    #Send the message with its length prepended to the front
    self.socket.send(struct.encode('!L', len(buff)) + buff)

  ##
  #Delete an object in the world model.
  def deleteURI(self, uri):
    buff = struct.pack('!B', self.DELETE_URI)
    uri16 = uri.encode('utf-16-be')
    buff += struct.pack('!L', len(uri16))
    buff += uri16
    buff += self.origin.encode('utf-16-be')
    #Send the message with its length prepended to the front
    self.socket.send(struct.encode('!L', len(buff)) + buff)

  #TODO Expire a URI's attribute
  #TODO Delete a URI's attribute
