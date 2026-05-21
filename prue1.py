from phue import Bridge

# 1. Conectar al Bridge (IP necesaria)
b = Bridge('192.168.68.54')

# 2. Si es la primera vez, presiona el botón del Bridge y ejecuta esto:
b.connect()

# 3. Obtener luces por habitación (Grupo)
# Hue considera las habitaciones como 'grupos'
def obtener_luces_habitacion(nombre_habitacion):
    group = b.get_group(nombre_habitacion)
    # 'lights' devuelve la lista de IDs de luces en esa habitación
    return group['lights']

# Ejemplo de uso
luces = obtener_luces_habitacion('Estudio')
print(f"Luces en el Salón: {luces}")

