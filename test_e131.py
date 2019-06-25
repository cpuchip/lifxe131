import sacn
import time
import colorsys
import threading

print("Running e1.31 Lifx reciever")
# provide an IP-Address to bind to if you are using Windows and want to use multicast
receiver = sacn.sACNreceiver()
receiver.start()  # start the receiving thread

# define a callback function
@receiver.listen_on('universe', universe=1)  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
	print("Recieved DMX data: ==========================")
	print(len(packet.dmxData))  # print the received DMX data
	print(packet.sequence)

# optional: if you want to use multicast use this function with the universe as parameter
receiver.join_multicast(1)

#time.sleep(10)  # receive for 10 seconds
event = threading.Event()
try:
    print('Press Ctrl+C to exit')
    event.wait()
except KeyboardInterrupt:
    print('got Ctrl+C')

receiver.stop()