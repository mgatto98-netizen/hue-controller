#!/usr/bin/python

import time
import random


seconds = time.time()
local_time = time.ctime(seconds)
print("Local time:", local_time)	

result = time.localtime(seconds)
print("result:", result)
print("\nyear:", result.tm_year)
print("tm_hour:", result.tm_hour)

control=True

while (control):
	seconds = time.time()
	result = time.localtime(seconds)
	if result.tm_hour==19 and result.tm_min==45:
		print('Es la hora!!!')
		control=False
	else:
		print('no es la hora')
		time.sleep(1)



print ('termine')


