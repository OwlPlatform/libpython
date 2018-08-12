import datetime

#Sensor sample from the aggregator to the solver interface
class SensorSample:
  def __init__(self, phy, device_id, receiver_id, timestamp, rssi, sense_data):
    self.phy_layer = phy
    self.device_id = device_id
    self.receiver_id = receiver_id
    self.timestamp = timestamp
    self.date = datetime.datetime.fromtimestamp(self.timestamp)
    self.rssi = rssi
    self.sense_data = sense_data

  def __str__(self):
    return "{}: (phy {}) {} -> {}, RSS: {}, {} bytes: {}".format(self.date, self.phy_layer, self.device_id, self.receiver_id, self.rssi, len(self.sense_data), self.sense_data)
