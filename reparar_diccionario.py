import re

def natural_keys(text):
    '''
    Función auxiliar para dividir el texto en trozos de números y texto.
    Esto permite un orden natural: 1, 2, 10 en lugar de 1, 10, 2
    '''
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

def reparar_y_ordenar_diccionario(archivo_entrada, archivo_salida):
    try:
        # 1. Leer y separar por .mp4
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            contenido = f.read()
            # Añadimos un salto de línea después de cada .mp4
            # (Limpiamos posibles espacios en blanco previos)
            lista_palabras = [p.strip() + '.mp4' for p in contenido.split('.mp4') if p.strip()]

        # 2. Ordenar de forma natural
        lista_ordenada = sorted(lista_palabras, key=natural_keys)

        # 3. Guardar el archivo
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lista_ordenada))

        print(f"¡Diccionario reparado y ordenado correctamente en: {archivo_salida}!")

    except Exception as e:
        print(f"Error: {e}")

# Ejecución
reparar_y_ordenar_diccionario('reylag_diccionario.txt', 'diccionario_limpio.txt')
