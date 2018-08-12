import solver_aggregator as sa

sq = sa.SolverAggregator('localhost', 7008)

#Request packets from physical layer 1, don't specify a transmitter ID
# or mask (request all packet), and request packets every 1000
# milliseconds
sq.sendSubscription([sa.AggrRule(1, [], 1000)])
#For reference, a mask would look like this:
#sq.sendSubscription([sa.AggrRule(1, [sa.IDMask(0, 0x00000000)], 1000)])

while (sq.handleMessage()):
  if (len(sq.available_packets) > 0):
    for packet in sq.available_packets:
      print (packet)
    # Clear the packets
    sq.available_packets = []

print ("connection closed")
