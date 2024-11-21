import itertools
import os
import sys
import numpy as np
import pygame
from clases import Actions, Cell, Entorno, Food_object
from vars import BROWN, FOOD_STATUS, GREEN, HEALTH_STATUS, HUNGER_STATUS, ENERGY_STATUS, INITIAL_FOOD_NUMBER, RADIUS, RED, SEMILLA, SEXUAL_STATUS, WIDTH,HEIGHT,\
    INITIAL_CELLS_NUMBER, random_generator
import random
import threading
import time

def read_states_order_from_file(file_path="states_order.txt"):
    """
    Lee el states_order desde un archivo de texto y lo asigna a una lista.
    """
    states_order = []
    try:
        with open(file_path, "r") as file:
            contenido = file.read()
        states_order = [tuple(line.split(","))
                                for line in contenido.strip().splitlines()]
    except FileNotFoundError:
        print(f"El archivo {file_path} no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error al leer {file_path}: {e}")
    return states_order


def write_q_table_to_txt(q_table, acciones, states_order, file_path="./Tablas/q_table.txt"):
        """
        Escribe la tabla Q en un archivo de texto, incluyendo el orden de estados y la identificación de la célula.
        """
        tam_q_table = 6000
        print("Voy a escribir la tabla")
        contenido = []            
        # Escribir la tabla Q en un formato legible
        for state_idx, state in enumerate(q_table):
            # Asegurar que cada fila tenga la longitud igual al número de acciones
            if len(state) == len(acciones):
                # Escribe el estado y la fila de valores en la misma línea, separados por ":"
                contenido.append(f"{state}\n")
            else:
                print(f"--¡ERROR!-- [TABLA {str(id)}] : La fila {state_idx} no coincide con el número de acciones. El state es: {state}\n")
                sys.exit()

        if len(contenido) != tam_q_table:
            print(f"--¡ERROR!-- [TABLA {id}] Ha petado. El content tiene \
                  {len(contenido)} y deberia tener {tam_q_table}S\n-----------------------\\n")

        with open(file_path, "w") as file:
            file.writelines(contenido)

def calculate_exploration_factor(iteracion):
        initial_exploration = 1.0  # Comienza explorando mucho
        decay_rate = 0.995  # Disminuye progresivamente
        exploration_factor = initial_exploration * (decay_rate**iteracion)
        return max(0.000001, exploration_factor)  # No dejar que baje de 0.1


def clase_prueba_simulacion():
    # Inicializar Pygame
    pygame.init()

    # Dimensiones de la ventana
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulación de Células")

    # Crear una lista de células y de comida
    cells = []
    foods = []

    # Generar todas las combinaciones posibles de los estados
    all_combinations = list(
    itertools.product(
        HEALTH_STATUS.values(),
        HUNGER_STATUS.values(),
        ENERGY_STATUS.values(),
        FOOD_STATUS.values(),
        SEXUAL_STATUS.values(),
    )
    )

    acciones = [
            Actions().search_food,
            Actions().search_partner,
            Actions().to_breed,
            Actions().rest,
            Actions().eat,
            Actions().explore
    ]
    # Lista células
    for id in range(INITIAL_CELLS_NUMBER):
        multiplicadores = {
            "impulsito": 1.05,
            "longevidad": 1.05,
            "percepcion": 1.05,
        }
        random_generator.shuffle(all_combinations)
        cell = Cell(
            id = id,
            position_x=random_generator.randint(0, WIDTH),
            position_y=random_generator.randint(1, HEIGHT),
            radius=RADIUS,
            color=RED,
            speed_x=3,
            speed_y=3,
            health=100,
            age=0,
            hunger=20,  # Saciado
            energy=100,
            libid=0,
            herencia=multiplicadores,
            actions=acciones,
        )
        cells.append(cell)

    # Lista comida
    for _ in range(INITIAL_FOOD_NUMBER):
        food = Food_object(
            position_x=random_generator.randint(0, WIDTH),
            position_y=random_generator.randint(1, HEIGHT),
            color=GREEN,
            food_reserve=200,
            radius=RADIUS,
            energy_of_food=10,
            satiating_value=10,
        )
        foods.append(food)

    entorno = Entorno(
        cells_list=cells, food_list=foods, exploration_factor=0
    )  

    entorno.next_id = INITIAL_CELLS_NUMBER

    for cell in cells:
        cell.entorno = entorno  # Ahora asignamos el entorno a cada célula
        cell.start()  # Iniciar el hilo de cada célula

    # Bucle principal
    running = True
    while running and len(entorno.cells_list) > 0:
        pygame.time.delay(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        win.fill(BROWN)

        # Dibujar las células y la comida
        for cell in cells:
            if cell.alive:
                cell.draw(win)

        for food in foods:
            food.draw(win)

        pygame.display.update()
    
    print(f"Keys diccionario: {entorno.diccionario_elementos.keys()}")
    # Escribir las tablas
    entorno.write_tables_to_file()
    pygame.quit()

# TODO: meterle velocidad en base a la edad que tenga

# Inicializar Pygame
    pygame.init()

    # Dimensiones de la ventana
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulación de Células")

    # Crear una lista de células y de comida
    cells = []
    foods = []



    # Generar todas las combinaciones posibles de los estados
    all_combinations = list(
    itertools.product(
        HEALTH_STATUS.values(),
        HUNGER_STATUS.values(),
        ENERGY_STATUS.values(),
        FOOD_STATUS.values(),
        SEXUAL_STATUS.values(),
    )
    )

    acciones = [
            Actions().search_food,
            Actions().search_partner,
            Actions().to_breed,
            Actions().rest,
            Actions().eat,
            Actions().explore
    ]
    # Lista células
    for id in range(INITIAL_CELLS_NUMBER):
        multiplicadores = {
            "impulsito": 1.05,
            "longevidad": 1.05,
            "percepcion": 1.05,
        }
        random_generator.shuffle(all_combinations)
        cell = Cell(
            id = id,
            position_x=random_generator.randint(0, WIDTH),
            position_y=random_generator.randint(1, HEIGHT),
            radius=RADIUS,
            color=RED,
            speed_x=3,
            speed_y=3,
            health=100,
            age=0,
            hunger=20,  # Saciado
            energy=100,
            libid=0,
            herencia=multiplicadores,
            actions=acciones,
        )
        cells.append(cell)

    # Lista comida
    for _ in range(INITIAL_FOOD_NUMBER):
        food = Food_object(
            position_x=random_generator.randint(0, WIDTH),
            position_y=random_generator.randint(1, HEIGHT),
            color=GREEN,
            food_reserve=200,
            radius=RADIUS,
            energy_of_food=10,
            satiating_value=10,
        )
        foods.append(food)

    entorno = Entorno(
        cells_list=cells, food_list=foods, exploration_factor=0
    )  

    entorno.next_id = INITIAL_CELLS_NUMBER

    for cell in cells:
        cell.entorno = entorno  # Ahora asignamos el entorno a cada célula
        cell.start()  # Iniciar el hilo de cada célula

    # Bucle principal
    running = True
    print("Se ejecuta el bucle principal")
    while running:
        #pygame.time.delay(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        win.fill(BROWN)

        # Dibujar las células y la comida
        for cell in cells:
            if cell.alive:
                cell.draw(win)

        for food in foods:
            food.draw(win)

        pygame.display.update()

    pygame.quit()

def entrenamiento_escritura_tablas():
   
# TODO: meterle velocidad en base a la edad que tenga
# TODO: puede que sea mucha presion que solo mejore si va hacia la comida mas cercana, se 

    acciones = [
            Actions().search_food,
            Actions().search_partner,
            Actions().to_breed,
            Actions().rest,
            Actions().eat,
            Actions().explore
    ]
    

    # Bucle principal
    running = True
    iteraciones = 50000
    pygame.init()
    
    for iteracion in range(iteraciones):
        inicio_iteracion = time.time()
        print("Iteracion numero: "+str(iteracion))
        # Inicializar Pygame

        # Dimensiones de la ventana
        win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Simulación de Células")

        # Crear una lista de células y de comida
        cells = []
        foods = []

        # Generar todas las combinaciones posibles de los estados
        # all_combinations = list(
        # itertools.product(
        #     HEALTH_STATUS.values(),
        #     HUNGER_STATUS.values(),
        #     ENERGY_STATUS.values(),
        #     FOOD_STATUS.values(),
        #     SEXUAL_STATUS.values(),
        # )
        # )

        # Lista células
        print("Initial number: "+str(INITIAL_CELLS_NUMBER))
        for id in range(INITIAL_CELLS_NUMBER):
            multiplicadores = {
                "impulsito": 1.05,
                "longevidad": 1.05,
                "percepcion": 1.05,
            }
            #random_generator.shuffle(all_combinations)
            cell = Cell(
                id = id,
                position_x=random_generator.randint(0, WIDTH),
                position_y=random_generator.randint(1, HEIGHT),
                radius=RADIUS,
                color=RED,
                speed_x=3,
                speed_y=3,
                health=100,
                age=0,
                hunger=20,  # Saciado
                energy=100,
                libid=0,
                #states_order=all_combinations,
                herencia=multiplicadores,
                actions=acciones,
            )
            cells.append(cell)

        # Lista comida
        for _ in range(INITIAL_FOOD_NUMBER):
            food = Food_object(
                position_x=random_generator.randint(0, WIDTH),
                position_y=random_generator.randint(1, HEIGHT),
                color=GREEN,
                food_reserve=200,
                radius=RADIUS,
                energy_of_food=10,
                satiating_value=10,
            )
            foods.append(food)

        entorno = Entorno(
            cells_list=cells, food_list=foods, exploration_factor= calculate_exploration_factor(iteracion)
        )  # TODO: hacer que esto sea un hilo para que se vayan creando nuevas comidas

        print("Factor exploracion: "+str(entorno.exploration_factor))
        entorno.next_id = INITIAL_CELLS_NUMBER

        for cell in cells:
            cell.entorno = entorno  # Ahora asignamos el entorno a cada célula
            cell.start()  # Iniciar el hilo de cada célula
        
        
        #pygame.time.delay(0)
        while running and len(entorno.cells_list) > 0:
            #print("Numero de celulas: "+str(len(entorno.cells_list)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            win.fill(BROWN)

            # Dibujar las células y la comida
            for cell in cells:
                if cell.alive:
                    cell.draw(win)

            for food in foods:
                food.draw(win)

            pygame.display.update()

        print(f"Keys diccionario: {entorno.diccionario_elementos.keys()}")
        # Escribir las tablas
        entorno.write_tables_to_file()
        # Detener el cronómetro y calcular el tiempo transcurrido
        fin_iteracion = time.time()
        duracion_iteracion = fin_iteracion - inicio_iteracion
        print(f"Tiempo de ejecución de la iteración {iteracion}: {duracion_iteracion:.4f} segundos")
        
        # Guardar el tiempo en un archivo de texto
        with open("tiempos_iteraciones.txt", "a") as file:
            file.write(f"Iteración {iteracion}: {duracion_iteracion:.4f} segundos\n")
            
    pygame.quit() 


def escritura_tabla_completa():
    acciones = [
            Actions().search_food,
            Actions().search_partner,
            Actions().to_breed,
            Actions().rest,
            Actions().eat,
            Actions().explore
    ]

    # Escribo tabla q inicial
    print("Escribo tabla q inicial")
    ruta_lectura_tabla_0 = "./Tablas/Tabla_celula_0.txt"    
    ruta_lectura_tabla_0_states_order = "./Orden/Tabla_celula_0.txt" 
    states_order = read_states_order_from_file(file_path=ruta_lectura_tabla_0_states_order)
    
    if len(states_order) == 0:
        sys.exit()
    try:
        with open(ruta_lectura_tabla_0) as file:
            lines = file.readlines()
        print(f"Hay {len(lines)} lineas")
        q_table = []
        for line in lines:
            # Extraer los valores después de ":"
            values = line.replace("[", "").replace("]", "").split()
            row = []
            for v in values:
                try:
                    row.append(float(v))
                except ValueError:
                    print(f"Warning al leer primera tabla: No se pudo convertir '{v}' a float en la línea: {line.strip()}")
            # Verificar si la longitud de la fila es igual al número de acciones
            if len(row) == len(acciones):
                q_table.append(row)
            else:
                print(f"Warning al leer primera tabla: La fila tiene una longitud incorrecta y se omitirá.")
        # Convertir a array de numpy si todas las filas son uniformes
        if q_table and all(len(row) == len(q_table[0]) for row in q_table):
            q_table = np.array(q_table)
        else:
            raise ValueError("La tabla Q leída no es uniforme.")
    except FileNotFoundError:
            print(f"El archivo {ruta_lectura_tabla_0} no existe. Se genera una nueva tabla Q.")

    print("Tamaño tabla q al acabar: "+str(len(q_table)))
    
    carpeta = "./Tablas"

    # Lista los elementos
    elementos = os.listdir(carpeta)

    for elemento in elementos:
        ruta_lectura_tabla = os.path.join(carpeta, elemento)
        print(f"Leo la tabla  {ruta_lectura_tabla}")
        try:

            with open(ruta_lectura_tabla) as file:
                lines = file.readlines()
            

            linea = 0
            for line in lines:
                # Buscar líneas que contengan datos de la tabla Q
                values = line.replace("[", "").replace("]", "").split()
                row = []
                for v in values:
                    try:
                        linea_q_table = np.array(q_table[linea])
                        row.append(float(v))

                    except ValueError:
                        print(f"Warning al sumar: No se pudo convertir '{v}' a float en la línea: {line.strip()}")
                # Verificar si la longitud de la fila es igual al número de acciones
                row = np.array(row)
                suma = linea_q_table + row
                if len(suma) == len(acciones):
                    q_table[linea] = suma
                else:
                    print(f"Warning al sumar: La fila tiene una longitud incorrecta y se omitirá. \nLen row: {len(row)}\n Len acciones: {len(acciones)}")
                    sys.exit()
                linea += 1
            # Convertir a array de numpy si todas las filas son uniformes
        except FileNotFoundError:
                ...#print(f"El archivo {ruta_lectura_tabla_0} no existe. Se genera una nueva tabla Q.")
    
    write_q_table_to_txt(
        q_table=q_table,
        acciones=acciones,
        states_order=states_order
    )

if __name__ == "__main__":
    clase_prueba_simulacion()
    #entrenamiento_escritura_tablas()
    #escritura_tabla_completa()

#TODO: tener en cuenta que la tabla se guarda segun el orden, asi que igual se deberia guardar tmb eso en el fichero de texto