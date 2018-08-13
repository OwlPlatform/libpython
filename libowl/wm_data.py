#Solution types used when communicating with a GRAIL world model

class WMAttribute:
  def __init__(self, name, data, creation, expiration = 0, origin = "empty", transient = False):
    #Name of this attribute
    self.name = name
    #Binary buffer of attribute data
    self.data = data
    #The creation and expiration dates of this attribute
    #in milliseconds since midnight Jan 1, 1970
    self.creation = creation
    self.expiration = expiration
    #The origin (creating agent) of this data
    self.origin = origin
    #Is this a transient type
    self.transient = transient

  def __str__(self):
    return "{}, {}, {}, {}, {}\n".format(self.name, self.creation, self.expiration, self.origin, self.data)

class WMData:
  def __init__(self, uri, attributes, ticket = 0):
    #The object that this data modifies
    self.uri = uri
    #The attributes of the object
    self.attributes = attributes
    #The request ticket that this data is associated with
    self.ticket = ticket

  def __str__(self):
    str = "{}:\n".format(self.uri)
    str += "\tAttribute,\tCreated,\tExpires,\tOrigin,\tData"
    for attr in self.attributes:
      str += "\n\t{}".format(attr)
    return str
