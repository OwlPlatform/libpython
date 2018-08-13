#Transient specification - one attribute name an a list of name expressions

class TransientRequest:
  def __init___(self, name, expressions):
    #Attribute name
    self.name = name
    #Requested expressions
    self.expressions = expressions
