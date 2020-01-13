import time
import colorsys
#import threading
import signal
import sys

import sacn
from lifxlan import LifxLAN


########## START CONFIG SETTINGS ###########

UNIVERSE = 2 # Which dmx universe it should be listening on

first_channel = 0       # First DMX channel - 1 (to account for array position)

numb_lights = 3     # How many lights you have on your network?  All must be in the DMX data

max_bright = 0.7 # Brightness, from 0 - 1

########### END CONFIG SETTINGS ###########

channels_per_light = 3  # Red, Green, Blue
scale_up = 65535 # This value will change what's concidered max brightness. minimum is 1 maximum is 65535
max_rgb = 255
# test power control
print("Discovering lights...")
lifx = LifxLAN(numb_lights)
lights = lifx.get_lights()
original_powers = lifx.get_power_all_lights()
original_colors = lifx.get_color_all_lights()

def dmx_channels(idx):
	start = first_channel + idx * channels_per_light
	end = start + channels_per_light
	return start, end

lights.sort(key=lambda l: l.get_label())
for i, l in enumerate(lights):
	startChannel, endChannel = dmx_channels(i)
	print(f"{l.label} is assigned to DMX channels {startChannel + 1} to {endChannel}")

print("Running e1.31 Lifx reciever")
# provide an IP-Address to bind to if you are using Windows and want to use multicast
receiver = sacn.sACNreceiver()
receiver.start()  # start the receiving thread

# define a callback function
@receiver.listen_on('universe', universe=UNIVERSE)  # listens on universe 1
def callback(packet):  # packet type: sacn.DataPacket
	print("Recieved DMX data: ==> ",packet.dmxData[(first_channel):(first_channel + numb_lights*channels_per_light)])
	for idx, light in enumerate(lights):
		# color is [Hue, Saturation, Brightness, Kelvin], duration in ms
		start, end = dmx_channels(idx)
		rgb = packet.dmxData[start:end]
		hsb = [int(x * scale_up) for x in colorsys.rgb_to_hsv(*[c / max_rgb for c in rgb])]
		hsb[2] = hsb[2] * max_bright # Adjust the brightness
		color = tuple(hsb) + (3500,) # Add kelvin
		print(f"{light.label:20} set to {color} from RGB{rgb}")
		light.set_color(color, 0, True)

# optional: if you want to use multicast use this function with the universe as parameter
receiver.join_multicast(UNIVERSE)

def cleanup():
	receiver.stop()
	print("Restoring original colors and power to all lights...")
	for light in lights:
		light.set_color(original_colors[light])
		light.set_power(original_powers[light])

def signal_handler(sig, frame):
	print("You pressed Ctrl+C!")
	cleanup()
	sys.exit()

signal.signal(signal.SIGINT, signal_handler)
print("Press Ctrl+C to quit")


