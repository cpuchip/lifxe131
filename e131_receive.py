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

max_bright = 0.8 # Brightness, from 0 - 1

# If r + g + b > this number, adjust max_bright by the percentage between the override and 3 * max_rgb_per_color
# i.e. for 255 * 3, max_bright will be set to max_bright_override
# for 200 * 3 or lower, max_bright will not be adjusted
# for in between, will be adjusted proportionally
override_max_bright_total_rgb = 200 * 3
max_bright_override = 1.0

########### END CONFIG SETTINGS ###########

channels_per_light = 3  # Red, Green, Blue
scale_up = 65535 # This value will change what's concidered max brightness. minimum is 1 maximum is 65535
max_rgb_per_color = 255
max_rgb_total = max_rgb_per_color * 3
override_scaling = 1/(max_rgb_total - override_max_bright_total_rgb)
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
if len(sys.argv) > 1:
    receiver = sacn.sACNreceiver(sys.argv[1])
else:
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
        hsb = [int(x * scale_up) for x in colorsys.rgb_to_hsv(*[c / max_rgb_per_color for c in rgb])]
        if sum(rgb) > override_max_bright_total_rgb:
            adjust_perc =  (sum(rgb) - override_max_bright_total_rgb) * override_scaling
            bright_adj = max_bright + ((max_bright_override - max_bright) * adjust_perc)
        else:
            adjust_perc = 0
            bright_adj = max_bright
        hsb[2] = round(hsb[2] * bright_adj) # Adjust the brightness
        color = tuple(hsb) + (3500,) # Add kelvin
        print(f"{light.label:20} set to {color} from RGB{rgb} - Adjust % {adjust_perc} bright_adj {bright_adj}")
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


