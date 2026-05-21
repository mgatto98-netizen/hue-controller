#!/usr/bin/python

import time
import random
from phue import Bridge


def festejo (lights,luces,minu):
  control=True
  while (control):
        seconds = time.time()
        result = time.localtime(seconds)
        if result.tm_min < minu+2:
         print (result.tm_min)
         for luz in luces:
          if random.randint(0,1)>0: 
            lights[luz].transitiontime = 1
            brillo=lights[luz].brightness
            color=lights[luz].xy
            lights[luz].xy=(0.3227,0.3290)
            lights[luz].brightness=0
            time.sleep(0.1)
            lights[luz].brightness=255
            time.sleep(0.5)
            lights[luz].brightness=0
            time.sleep(0.1)
            lights[luz].brightness=brillo
            lights[luz].xy=(color[0],color[1])
        else:
          control=False
           
	
b = Bridge('192.168.68.53')

# If the app is not registered and the button is not pressed, press the button
#and call connect() (this only needs to be run a single time)
#b.connect()

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
for h in range(20000):
	for luz in luces:
		#lights[luz].brightness=255
		indi = luces.index(luz) 
		
		colorini[indi]=colorini[indi]+1
		if colorini[indi]>3:
			colorini[indi]=1
	print(colorini)

	seconds = time.time()
	result = time.localtime(seconds)
	print ('Hora: ', result.tm_hour,':',result.tm_min)
	
	if result.tm_hour==0 and result.tm_min==0:
		print('Es la hora 00!!!')
		festejo (lights,luces,result.tm_min)
	
	print ('Sigo con las luces de la cena')	
		
		
	for luz in luces:
		indi = luces.index(luz) 
		lights[luz].brightness=random.randint(50,255)
		if (colorini[indi]==1):
			lights[luz].xy=(0.675,0.322)
		if (colorini[indi]==2):
			lights[luz].xy=(0.2151, 0.7106)
		if (colorini[indi]==3):
			lights[luz].xy=(0.3280,0.3286)

	time.sleep(50)
	
	
	




