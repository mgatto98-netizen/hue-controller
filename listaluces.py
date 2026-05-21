#!/usr/bin/python

import time
import random
from phue import Bridge

b = Bridge('192.168.68.60')

# If the app is not registered and the button is not pressed, press the button
#and call connect() (this only needs to be run a single time)
b.connect()

lights = b.lights

lights_id = b.get_light_objects('id')
light_names = b.get_light_objects('name')


for l in lights_id:
    print(int(l) ,' ----> ', lights_id[int(l)].name)
       
    
grupos=b.get_group()
for g in grupos:
	nombre=b.get_group(int(g),'name')
	print(g,nombre)
	luces=b.get_group(int(g),'lights')
	for l in luces:
		print (' 	|----> ',int(l),') ',lights_id[int(l)].name)
			
			
	
	
	
	


    	

