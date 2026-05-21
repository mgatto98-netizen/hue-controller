#!/usr/bin/python

import time
import random
from phue import Bridge

b = Bridge('192.168.68.55')

# If the app is not registered and the button is not pressed, press the button
#and call connect() (this only needs to be run a single time)
b.connect()

lights = b.get_light_objects('id')
luces=[4]

#b.set_light( luces, 'on', True)
lights[4].transitiontime = 1
lights[4].on=True

for i in range(3):
	print(i)
	lights[4].brightness=100
	lights[4].hue=15000
	time.sleep(1)
	lights[4].brightness=0
	time.sleep(0.5)
	

