#!/usr/bin/python
# -*- coding: utf-8 -*-

# Para usar este programa se debe estar
# en entorno conda "hue" (conda activate hue)
# y ejecutar python anonuevo2.py
# Chequear si el ip del bridge es el mismo y registrar la app con el boton en el bridge.
# Ultimo ip: 192.168.68.55 (12/2025)


import time
import random
from collections import deque
from phue import Bridge

def festejo(lights, luces, minu):
    control = True
    while control:
        seconds = time.time()
        result = time.localtime(seconds)
        if result.tm_min < minu + 2:
            print(result.tm_min)
            for luz in luces:
                if random.randint(0, 1) > 0:
                    lights[luz].transitiontime = 1
                    brillo = lights[luz].brightness
                    color = lights[luz].xy
                    lights[luz].xy = (0.3227, 0.3290)
                    lights[luz].brightness = 0
                    time.sleep(0.1)
                    lights[luz].brightness = 255
                    time.sleep(0.5)
                    lights[luz].brightness = 0
                    time.sleep(0.1)
                    lights[luz].brightness = brillo
                    lights[luz].xy = (color[0], color[1])
        else:
            control = False


b = Bridge('192.168.68.55')

# If the app is not registered and the button is not pressed, press the button
# and call connect() (this only needs to be run a single time)
# b.connect()

lights = b.get_light_objects('id')

# Array de luces que participan
luces = [1, 2, 3, 5, 6]

# Posibles colores
colores = [1, 2, 3]

# Inicialización de colores
colorini = [random.choice(colores) for _ in luces]
print(colorini)

# Encender luces y asignar color inicial
b.set_light(luces, 'on', True)
for luz in luces:
    lights[luz].brightness = 255
    lights[luz].transitiontime = 600
    indi = luces.index(luz)
    if colorini[indi] == 1:
        lights[luz].xy = (0.675, 0.322)  # Rojo
    elif colorini[indi] == 2:
        lights[luz].xy = (0.2151, 0.7106)  # Verde
    elif colorini[indi] == 3:
        lights[luz].xy = (0.3280, 0.3286)  # Blanco

time.sleep(5)

# Historial para evitar repetición inmediata
historial_colores = {luz: deque(maxlen=2) for luz in luces}

# Bucle principal
for h in range(20000):
    for luz in luces:
        # Elegir color evitando repeticiones inmediatas
        colores_disponibles = [c for c in colores if c not in historial_colores[luz]]
        nuevo_color = random.choice(colores_disponibles)
        historial_colores[luz].append(nuevo_color)
        
        # Ajustar el brillo con un rango aleatorio
        brillo = random.randint(50, 255)
        lights[luz].brightness = brillo

        # Aplicar color
        if nuevo_color == 1:
            lights[luz].xy = (0.675, 0.322)  # Rojo
        elif nuevo_color == 2:
            lights[luz].xy = (0.2151, 0.7106)  # Verde
        elif nuevo_color == 3:
            lights[luz].xy = (0.3280, 0.3286)  # Blanco

    # Garantizar que al menos una luz entre 1, 2 o 3 sea blanca
    luces_controladas = [1, 2, 3]
    if not any(lights[luz].xy == (0.3280, 0.3286) for luz in luces_controladas):
        luz_a_cambiar = random.choice(luces_controladas)
        lights[luz_a_cambiar].xy = (0.3280, 0.3286)  # Blanco

    seconds = time.time()
    result = time.localtime(seconds)
    print('Hora: ', result.tm_hour, ':', result.tm_min)

    if result.tm_hour == 0 and result.tm_min == 0:
        print('Es la hora 00!!!')
        festejo(lights, luces, result.tm_min)

    print('Sigo con las luces de la cena')

    # Espera aleatoria para hacerlo menos predecible
    time.sleep(random.uniform(45, 55))

