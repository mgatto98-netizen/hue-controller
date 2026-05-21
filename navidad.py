#!/usr/bin/python

# Para usar este programa se debe estar
# en entorno conda "hue" (conda activate hue)
# y ejecutar python navidad.py
# Chequear si el ip del bridge es el mismo y registrar la app con el boton en el bridge.
# ESTE SCRIPT NO CONTIENE EL EFECTO DE LUCES A LAS 12 DE LA NOCHE.

import time
import random
from phue import Bridge

b = Bridge('192.168.68.50')

# If the app is not registered and the button is not pressed, press the button
#and call connect() (this only needs to be run a single time)
b.connect()

lights = b.get_light_objects('id')

#rojo 1 = (0.675,0.322)
#verde 2 =(0.2151, 0.7106)
#blanco 3 =(0.3280,0.3286)

#array de luces que participan
luces=[1,2,3,5,6]

colores=[1,2,3]

colorini=[0,0,0,0,0]

for i in range(0,len(luces)):
	a=random.choice(colores)
	colorini[i]=a
print(colorini)

#inicio!!!
b.set_light( luces, 'on', True)
for luz in luces:
	lights[luz].brightness=255
	lights[luz].transitiontime = 600
	indi = luces.index(luz) 
	if (colorini[indi]==1):
		lights[luz].xy=(0.675,0.322)
	if (colorini[indi]==2):
		lights[luz].xy=(0.2151, 0.7106)
	if (colorini[indi]==3):
		lights[luz].xy=(0.3280,0.3286)

time.sleep(5)

#bucle
for h in range(100):
	for luz in luces:
		#lights[luz].brightness=255
		indi = luces.index(luz) 
		
		colorini[indi]=colorini[indi]+1
		if colorini[indi]>3:
			colorini[indi]=1
	print(colorini)
		
	for luz in luces:
		indi = luces.index(luz) 
		lights[luz].brightness=random.randint(50,255)
		if (colorini[indi]==1):
			lights[luz].xy=(0.675,0.322)
		if (colorini[indi]==2):
			lights[luz].xy=(0.2151, 0.7106)
		if (colorini[indi]==3):
			lights[luz].xy=(0.3280,0.3286)

	time.sleep(70)
	
	
	




