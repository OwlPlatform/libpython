import struct
import time

import wm_data
import solver_world_model as swm

#The third argument is the origin name, which should be your solver or
#client's name
wm = swm.SolverWorldModel('localhost', 7009, 'Your name here')
# Time in milliseconds
t = round(time.time() * 1000)
#Make an attribute for gps location with an example value and the current time
attribs = wm_data.WMAttribute('location.gps', struct.pack('!d', 3.14), t)
#Making a solution with a single attribute
new_data = wm_data.WMData('bus.route.example_stop', [attribs])
# Set the second argument to true in pushData to create the object with the
# given URI if it does not already exist

print("Sending data")
wm.pushData([new_data], True)
