import time
import colorsys
import threading
import signal
import sys

import sacn
from lifxlan import LifxLAN

lightIdx = (0,3,3) # start stop step for incramenting through all your channels in DMX data

max_bright = 65535
max_bit = 65535
max_rgb = 255

numb_lights = 2
UNIVERSE = 1

# test power control
print("Discovering lights...")
lifx = LifxLAN(numb_lights)
original_powers = lifx.get_power_all_lights()
original_colors = lifx.get_color_all_lights()
lights = lifx.get_lights()

[l.get_label() for l in lights] # populate all the labels on the lights so we can sort them


#print(lights[0].get_label())
#print(lights[0])
#print(lights[1].get_label())
#print(lights[1])

def label(l):
	return l.label
lights.sort(key=label)
print(lights[0].label)
print(lights[1].label)

print("Running e1.31 Lifx reciever")
# provide an IP-Address to bind to if you are using Windows and want to use multicast
receiver = sacn.sACNreceiver()
receiver.start()  # start the receiving thread

# define a callback function
@receiver.listen_on('universe', universe=UNIVERSE)  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
	#print("Recieved DMX data: ==========================")
	#print(len(packet.dmxData))  # print the received DMX data
	#print(packet.dmxData[0:12])
	for idx in range(0,len(lights)):
		# color is [Hue, Saturation, Brightness, Kelvin], duration in ms
		start = lightIdx[0] + (idx + 1) * lightIdx[2]
		end = lightIdx[1] + (idx + 1) * lightIdx[2]
		#print(" ===== ====== =====")
		#print(start)
		#print(end)
		r, g, b = packet.dmxData[start:end]
		hsv = colorsys.rgb_to_hsv(r / max_rgb, g / max_rgb, b / max_rgb)
		color = (hsv[0]*max_bit, hsv[1]*max_bit, hsv[2]*max_bright, 3500)
		#print(" ====== light ====== ")
		#print(idx)
		#print(hsv)
		#print(color)
		lights[idx].set_color(color, 0, True)

# optional: if you want to use multicast use this function with the universe as parameter
receiver.join_multicast(1)

sigINT = False
def signal_handler(sig, frame):
		print("You pressed Ctrl+C!")
		receiver.stop()
		sigINT = True
		sys.exit()
signal.signal(signal.SIGINT, signal_handler)
print("Press Ctrl+C to quit")

while not sigINT:
	if sigINT:
		break

receiver.stop()

print("Restoring original color to all lights...")
for lightIdx in original_colors:
	color = original_colors[lightIdx]
	lightIdx.set_color(color)

print("Restoring original power to all lights...")
for lightIdx in original_powers:
	power = original_powers[lightIdx]
	lightIdx.set_power(power)
