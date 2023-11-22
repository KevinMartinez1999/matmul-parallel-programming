import numpy as np
from ctypes import c_int, c_double, POINTER, CDLL, cast
from threading import Thread, Lock
import time
import sys

# Cargar la biblioteca compartida
mm_lib = CDLL("./mm.so")  # Ajusta la ruta según sea necesario

# Especificar los tipos de argumentos y el tipo de retorno de la función mm
mm_lib.mm.argtypes = [POINTER(POINTER(c_double)), POINTER(POINTER(c_double)), POINTER(POINTER(c_double)), c_int]
mm_lib.mm.restype = None

DEBUG_MODE = False

# Crear un Lock
mutex = Lock()

def multiply_matrices(double_pointer_a, double_pointer_b, double_pointer_c, matrix_size):
        mm_lib.mm(double_pointer_a, double_pointer_b, double_pointer_c, matrix_size)

def matrix_multiply_thread(double_pointer_a, double_pointer_b, double_pointer_c, matrix_size, start, end):
    for current_matrix in range(start, end+1):
        with mutex:
            a = double_pointer_a
            b = double_pointer_b
            c = double_pointer_c

        multiply_matrices(a, b, c, matrix_size)

        if DEBUG_MODE:
            # Imprimir el resultado de la multiplicación en Python
            with mutex:
                print(f"Matriz C (resultado de la multiplicación en Python para la matriz {current_matrix}):")
                for i in range(matrix_size):
                    row = [c[i][j] for j in range(matrix_size)]
                    print(row)

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 main.py <numero_de_workers> <numero_de_matrices>")
        sys.exit(1)

    num_workers = int(sys.argv[1])

    start_time = time.time()  # Tiempo de inicio
    fname = "../matrices_large.dat"  

    with open(fname, "r") as fh:
        # La primera línea indica el tamaño de la matriz
        nmats, matrix_size = map(int, fh.readline().split())
        
        if num_workers > nmats:
            num_workers = nmats
        
        # Leer las matrices fuera del bucle de creación de hilos
        matrices = []
        for _ in range(nmats):
            a = (POINTER(c_double) * matrix_size)()
            b = (POINTER(c_double) * matrix_size)()
            c = (POINTER(c_double) * matrix_size)()

            for i in range(matrix_size):
                row_a = list(map(float, fh.readline().split()))
                a[i] = cast((c_double * matrix_size)(*row_a), POINTER(c_double))

            for i in range(matrix_size):
                row_b = list(map(float, fh.readline().split()))
                b[i] = cast((c_double * matrix_size)(*row_b), POINTER(c_double))

            for i in range(matrix_size):
                c[i] = cast((c_double * matrix_size)(), POINTER(c_double))

            matrices.append((a, b, c))

    thread_list = []

    # Calcular las operaciones por hilo y el resto
    n_op_per_thread = nmats // num_workers
    op_remainder = nmats % num_workers

    # Crear y ejecutar hilos
    for t in range(num_workers):
        start = t * n_op_per_thread + min(t, op_remainder)
        end = (t + 1) * n_op_per_thread + min(t + 1, op_remainder) - 1

        # Crear matrices y punteros
        a, b, c = matrices[start]

        # Crear un hilo para cada rango de multiplicaciones de matrices
        args = (a, b, c, matrix_size, start, end)
        thread = Thread(target=matrix_multiply_thread, args=args)
        thread_list.append(thread)
        thread.start()

    # Esperar a que todos los hilos terminen
    for thread in thread_list:
        thread.join()

    end_time = time.time()  
    elapsed_time_ms = (end_time - start_time) * 1000
    print(elapsed_time_ms)

if __name__ == "__main__":
    main()
