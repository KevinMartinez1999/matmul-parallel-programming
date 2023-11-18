import os
import subprocess
import numpy as np

def ejecutar_comando_n_veces(comando, n):
    for i in range(n):
        # Generar un nombre de archivo único para cada ejecución
        archivo_salida = f"salida_{i}.txt"
        # Ejecutar el comando y redirigir la salida al archivo
        subprocess.run(f"{comando} > {archivo_salida}", shell=True)
        # Leer el contenido del archivo de salida y guardarlo en un arreglo
        with open(archivo_salida, 'r') as file:
            contenido = file.read()
            # Guardar el contenido en un arreglo
            arreglo_salida.append(contenido)
        # Eliminar el archivo de salida
        os.remove(archivo_salida)

# Ejemplo de uso
comando = "./matmulseq_file"
n = 200
arreglo_salida = []
ejecutar_comando_n_veces(comando, n)
# Guardar el arreglo en un archivo de texto
with open("salida.txt", 'w') as file:
    for salida in arreglo_salida:
        file.write(salida)

a = np.loadtxt("salida.txt")
print("El promedio de los tiempos de ejecución es: ", np.mean(a), "milisegundos")
os.remove("salida.txt")