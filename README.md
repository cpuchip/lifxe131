# lifxe131
A set of script used to enable you to control your Lifx lights through the sacn/e1.31 protocol like xLights

I'm working on turning this into a service that can be installed, configured and run a raspberry pi or other computer
to enable you to use Lifx smart light bulbs in an xLights show.

The goal is to run this on the same Raspberry Pi ( or another ) as with Falcon Pi Player ( https://github.com/FalconChristmas/fpp/releases/ ) where you'd upload your fseq files from xLights so that you can play your light show
with your normal ws2811 RGB LEDs and these lifx smart lights.

# configuration
For now you need to give your lifx bulbs a label that can be sorted in order, say 1, 2, 3, 4, ...
This script will discover all lifx bulbs on your network, sort them in alphanumerical order
and then replay any e1.31 dmx channel data received to it as lifxlan data packets to the discovered lights.

Still much work to be done, for now e131_receive.py has a header of configuration that you can do, later I'll
pull that out in a configuration file that you can update upon install or something.

current configuration options:

numb_lights = 2 # How many lights you have on your network so the automated light discovery knows when it's found them all
UNIVERSE = 1 # Which dmx universe it should be listening on
max_bright = 65535 # This value will change what's concidered max brightness. minimum is 1 maximum is 65535

I'm using the pip packages lifxlan and sacn to make this all work. props to them for doing all the hard work.