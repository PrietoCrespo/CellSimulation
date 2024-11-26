from abc import abstractmethod
import itertools
import math
import os
import random
import sys
import time
import pygame
import uuid
from vars import *
import numpy as np
import threading
from vars import random_generator


class Cell(threading.Thread):
    def __init__(
        self,
        id=None,
        position_x=None,
        position_y=None,
        radius=None,
        color=None,
        speed_x=None,
        speed_y=None,
        health=None,
        age=None,
        hunger=None,
        energy=None,
        libid=None,
        herencia=None,
        entorno=None,
        actions=None,
    ):
        super().__init__()
        # self.id = uuid.uuid4()  # Genera un ID único
        self.id = id
       # print("ID creacion celula: "+str(self.id))
        self.position_x = position_x
        self.position_y = position_y
        self.radius = 10
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.last_move_x = None
        self.last_move_y = None
        self.health = health
        self.age = age
        self.hunger = hunger
        self.energy = energy
        self.libid = libid
        self.actions = actions
        self.impulsito = herencia.get("impulsito")
        self.life_expectancy = random_generator.randint(
            RANGO_EDAD_MAXIMA[0], RANGO_EDAD_MAXIMA[1]
        ) * herencia.get("longevidad")  # Quiza meterle algo random tmb
        self.perception = random_generator.randint(
            RANGO_PERCEPCION[0], RANGO_PERCEPCION[1]
        ) * herencia.get("percepcion")
        self.shorter_foods = (
            list()
        )  # Empieza vacio, pues no se le ha pasado aun. Se actualiza por tick
        self.alive = True
        self.entorno = entorno

        # Genero states order
        self.read_states_order_from_file()
        # Genero tabla q
        self.read_q_table_from_txt()

        '''n_estados = len(HEALTH_STATUS) * \
            len(HUNGER_STATUS) * len(ENERGY_STATUS) * len(SEXUAL_STATUS) * len(FOOD_STATUS)
        self.q_table = np.zeros((n_estados, len(self.actions)))'''
        # ------------------
        self.cd_reproduction = 0

        # Desde las vars
        self.food_from_bite = FOOD_FROM_BITE
        self.max_health = MAX_HEALTH
        self.max_hunger = MAX_HUNGER

    def run(self):
        """Método principal del hilo que se ejecuta en bucle."""
        while self.alive:
            # Aquí va la lógica de comportamiento de la célula.
            shorter_foods, food_distances = Actions().check_food(self, self.entorno)
            self.shorter_foods = shorter_foods  # Actualizo shorter foods

            estados = self.get_states() #Obtiene el estado de cada atributo

            estado_ant = self.get_state(estados) # Obtiene el estado a partir del orden de estados
            
            exploration_factor = self.entorno.exploration_factor # TODO: esto deberia limpiarlo de aqui
            # Genera un número aleatorio entre 0 y 1
            random_value = random_generator.random()
            if random_value < exploration_factor:
                accion = self.actions[random_generator.randint(
                    0, len(self.actions) - 1)]
            else:
                accion = self.get_action_from_state(estado_ant)
            self.update_qtable(accion)
            Actions().avoid_collision(self, self.entorno)
            self.life_update()
            # Controlar la velocidad del hilo (30 ms)
            time.sleep(0.0001)
            

    def read_q_table_from_txt(self):
        """
        Lee una tabla Q desde un archivo de texto y actualiza la tabla Q actual de la célula.
        El formato debe coincidir con el generado por write_q_table_to_txt.
        """
        ruta_lectura = "./Tablas/Tabla_celula_" + str(self.id) + ".txt"
        try:
            with open(ruta_lectura) as file:
                lines = file.readlines()

            q_table = []
            if len(lines) == TAMAÑO_Q_TABLE: # El fichero está completo

                for line in lines:
                    # Extraer los valores después de ":"
                    values = line.replace("[", "").replace("]", "").split()
                    if len(values) != len(self.actions):
                        print(f"--¡ERROR!-- [TABLA {self.id}]: El tamaño de los valores ({len(values)}) no coincide con los de acciones ({len(self.actions)}). Los valores son  '{values}'\n")
                        sys.exit()
                    row = []
                    for v in values:
                        try:
                            row.append(float(v))
                        except ValueError:
                            print(f"--¡ERROR!-- [TABLA {self.id}]: No se pudo convertir '{v}' a float en la línea: {line.strip()}\n")
                            sys.exit()
                    # Verificar si la longitud de la fila es igual al número de acciones
                    if len(row) == len(self.actions):
                        q_table.append(row)
                    else:
                        print(f"--¡ERROR!-- [TABLA {self.id}]: La fila tiene una longitud incorrecta. \
                                            La fila es: {row}\n")
                        sys.exit()
            else:
                with open(ruta_lectura) as file:
                    lines = file.readlines()
                if len(lines) == TAMAÑO_Q_TABLE: # El fichero está completo

                    for line in lines:
                        # Extraer los valores después de ":"
                        values = line.replace("[", "").replace("]", "").split()
                        if len(values) != len(self.actions):
                            print(f"--¡ERROR!-- [TABLA {self.id}]: El tamaño de los valores ({len(values)}) no coincide con los de acciones. Los valores son  '{values}'\n")
                            sys.exit()
                        row = []
                        for v in values:
                            try:
                                row.append(float(v))
                            except ValueError:
                                print(f"--¡ERROR!-- [TABLA {self.id}]: No se pudo convertir '{v}' a float en la línea: {line.strip()}\n")
                                sys.exit()
                        # Verificar si la longitud de la fila es igual al número de acciones
                        if len(row) == len(self.actions):
                            q_table.append(row)
                        else:
                            print(f"--¡ERROR!-- [TABLA {self.id}]: La fila tiene una longitud incorrecta. \
                                                La fila es: {row}\n")
                            sys.exit()
                else:
                    print (f"--¡ERROR!-- [TABLA {self.id}]: El tamaño del fichero no \
                        es valido. Tiene de tamaño: {len(lines)}")
            # Convertir a array de numpy si todas las filas son uniformes
            if len(q_table) > 0:
                self.q_table = np.array(q_table)
                if len(self.q_table) != TAMAÑO_Q_TABLE:
                    print (f"--¡ERROR!-- [TABLA {self.id}]: El tamaño de la tabla \
                        no es valido. Tiene de tamaño: {len(self.q_table)}")
                    sys.exit()
            else:
                print(f"--¡ERROR!-- [TABLA {self.id}]:La tabla Q leída no es uniforme. ")
                sys.exit()
            
        
        except FileNotFoundError:
            n_estados = len(HEALTH_STATUS) + \
                len(HUNGER_STATUS) + len(ENERGY_STATUS) + \
                len(SEXUAL_STATUS) + len(FOOD_STATUS)
            self.q_table = np.zeros((n_estados, len(self.actions)))
        except IndexError:
            print(f"--¡ERROR!-- [TABLA {self.id}]: Ha petado al acceder al indice.")

    def write_q_table_to_txt(self, file_path="q_table.txt"):
        """
        Escribe la tabla Q en un archivo de texto, incluyendo el orden de estados y la identificación de la célula.
        """
        if len(self.q_table) != TAMAÑO_Q_TABLE:
            print(f"--¡ERROR!-- [TABLA {str(self.id)}] : al escribir la tabla Q esta tiene un tamaño de\
                    {str(len(self.q_table))}, cuando debería ser {TAMAÑO_Q_TABLE}")
            sys.exit()

        contenido = []
        for state_idx, state in enumerate(self.q_table):
            if len(state) == len(self.actions):
                if len(self.states_order[state_idx]) != 5:
                    print(f"--¡ERROR!-- [TABLA {str(self.id)}] : Ha petado ya que la fila de states order no tiene 5 elementos. Celula {self.id}")
                    sys.exit()
                else:
                    contenido.append(f"{state}\n")
            else:
                print(f"--¡ERROR!-- [TABLA {str(self.id)}] : La fila {state_idx} no coincide con el número de acciones. El state es: {state}\n")
                sys.exit()

        if len(contenido) != TAMAÑO_Q_TABLE:
            print(f"--¡ERROR!-- [TABLA {self.id}] Ha petado. El content tiene \
                  {len(contenido)} y deberia tener {TAMAÑO_Q_TABLE}S\n-----------------------\\n")

        with open(file_path, "w") as file:
            file.writelines(contenido)


    @staticmethod
    def generate_states_order():
        """
        Genera todas las combinaciones posibles de estados de vida, hambre, energía,
        cercanía de comida y estado sexual.
        """

        combined_list = (
            list(HEALTH_STATUS.values())
            + list(HUNGER_STATUS.values())
            + list(ENERGY_STATUS.values())
            + list(FOOD_STATUS.values())
            + list(SEXUAL_STATUS.values())
        )

        # Mezclar la lista combinada
        random.shuffle(combined_list)

        # Devolver la lista mezclada
        return combined_list
                
        

    def write_states_order_to_file(self, file_path="states_order.txt"):
        """
        Escribe el states_order en un archivo de texto.
        """

        contenido = []
        for state in self.states_order:
            line = ",".join(state)
            contenido.append(f"{line}\n")

        with open(file_path, "w") as file:
            file.writelines(contenido)
        # print(f"El orden de los estados se ha guardado en {file_path}")

    def read_states_order_from_file(self, file_path="states_order.txt"):
        """
        Lee el states_order desde un archivo de texto y lo asigna a self.states_order.
        """
        try:
            with open(file_path, "r") as file:
                contenido = file.read()  # Lee todo el contenido del archivo de una vez

            # Procesa el contenido después de cerrar el archivo
            self.states_order = [tuple(line.split(","))
                                 for line in contenido.strip().splitlines()]

        except FileNotFoundError:
            print("Genero states order")
            self.states_order = self.generate_states_order()
            print(f"Orden: {str(self.states_order)[:200]}")

    def print_q_table(self):
        for state_idx, state in enumerate(self.q_table):
            formatted_row = "\t".join(f"{val:.4f}" for val in state)
            # print(f"State {self.states_order(state_idx)}: {formatted_row}\n")

    def update_color(self):
        # Asegúrate de que age y life_expectancy sean valores válidos
        t = min(
            1, self.age / self.life_expectancy
        )  # Normalizamos la edad a un valor entre 0 y 1

        # Interpolar entre RED y BLACK
        r = int(RED[0] * (1 - t) + BLACK[0] * t)
        g = int(RED[1] * (1 - t) + BLACK[1] * t)
        b = int(RED[2] * (1 - t) + BLACK[2] * t)

        # Actualizamos el color de la célula
        self.color = (r, g, b)

    def move(self, actions: "Actions"):
        actions.move_random(self)

    def get_main_attributes(self):
        _, food_distances = Actions().check_food(self, self.entorno)
        _, partner_distances = Actions().check_partner(self, self.entorno)

        return {
            "health": self.health,
            "energy": self.energy,
            "hunger": self.hunger,
            "food_distance": food_distances,
            "partners": partner_distances
        }

    def draw(self, win):
        if self.alive:
            pygame.draw.circle(
                win,
                self.color,
                (int(self.position_x), int(self.position_y)),
                self.radius,
            )

    def life_update(self):  # Actualiza cada tick
        """
        Devuelve 'True' si está vivo el individuo.
        Devuelve 'False' si ha muerto.
        """
        # Actualizo edad
        if (self.age + 0.1) < self.life_expectancy:
            self.age += PASO_EDAD  # 0.1 año por cada tick
        else:
            self.alive = False
        # Actualizacion libido
        self.libido()

        # Actualizo energia
        energia = 0.5
        if self.energy - energia > 0:
            self.energy -= energia
            self.energy = round(self.energy, 2)

        # Si pasa hambre
        if (
            self.hunger >= 0.7 * self.max_hunger
        ):  # Si está pasando más hambre de la cuenta, le resta vida
            self.health -= 1
            if self.health <= 0:
               # print("Murió de hambre")
                self.alive = False

        if not self.alive:
            # print("Murio con la siguiente tabla q:\n\n" + str(self.q_table))
            # Escribo la tabla q en un archivo
            ruta_escritura_q_table = "./Tablas/Tabla_celula_" + \
                str(self.id) + ".txt"
            
            self.entorno.diccionario_elementos[self.id] = {
                "tabla_q": self.q_table,
                "states_order": self.states_order 
            }


            ruta_escritura_order = "./Orden/Orden_celula_" + \
                str(self.id) + ".txt"
            
            # Borra la celula del entorno
            self.entorno.delete_cell_by_id(self.id
                                           )
            # print("Orden estados:\n\n" + str(self.states_order))
        self.energy = round(self.energy, 2)
        self.hunger = round(self.hunger, 2)
        self.update_color()

    def libido(self):
        age = self.age
        impulsito = self.impulsito
        mu = self.life_expectancy / 3  # Edad en la que la líbido es máxima
        sigma = self.life_expectancy / 6  # Controla el ancho de la campana

        if self.cd_reproduction == 0:
            if self.age > 0.2 * self.life_expectancy:  # Si está en edad fértil
                self.libid = (
                    100 * math.exp(-((age - mu) ** 2) /
                                   (2 * sigma**2)) * impulsito
                )
            else:
                self.libid = 0
        else:
            self.cd_reproduction -= 1

    def get_states(self):
        """
        Devuelve los estados de vida, comida, energia, sexual y cercania comida de la celula.
        """
        health_status = self.get_health_status()
        hunger_status = self.get_hunger_status()
        energy_status = self.get_energy_status()
        sexual_status = self.get_sexual_status()
        food_proximity = self.get_food_proximity()

        return {
            "Health_status": health_status,
            "Hunger_status": hunger_status,
            "Energy_status": energy_status,
            "Sexual_status": sexual_status,
            "Food_proximity": food_proximity,
        }

    def get_combined_state(self):
        health_status = self.get_health_status()
        hunger_status = self.get_hunger_status()
        energy_status = self.get_energy_status()
        sexual_status = self.get_sexual_status()
        food_status = self.get_food_proximity()
        # Combinar en una tupla que represente el estado
        # return (health_status, hunger_status, energy_status, sexual_status, food_status)
        return (health_status, hunger_status, energy_status, food_status, sexual_status)

    def get_state(self, states_dict: dict):
        """
        Recibe el diccionario con los estados de la celula de cada tipo y devuelve
        el "estado real"
        """

        for state in self.states_order:
            if state in states_dict.values():
                return state
            

    def get_best_action(self, puntuaciones: list):
        """
        Devuelve la mejor accion (columna) de una accion en la tabla q.
        """
        # Valor maximo de las puntuaciones
        # print("Puntuaciones: "+str(puntuaciones))
        valor_max = np.max(puntuaciones)
        # Encuentra todos los indices de valor maximo
        indices_max = np.where(puntuaciones == valor_max)[0]

        if len(indices_max) > 1:
            indice = random_generator.choice(indices_max)
        else:
            indice = np.argmax(puntuaciones)

        # print("Self actions: " + str(self.actions))
        # print("Indice: " + str(indice))
        return self.actions[indice]

    def get_action_from_state(self, state):
        """

        Recibe el diccionario con los estados de la celula y devuelve la MEJOR accion a realizar basandose
        en la tabla q. Para ello primero calcula cual es su "estado real"

        States_dict contiene los estados de la celula de cada uno de los tipos (energia, salud, etc.)
        """
        try:
            index = self.states_order.index(state)  # Indice del estado actual
            # Tabla del estado
            tabla_puntuaciones = self.q_table[index]
        except IndexError as ex:
            print(f"\nIndice celula: {self.id}")
            print(f"Error: {str(ex)}")
            print(f"Tabla q: {self.q_table}")
            print(f"Tamaño tabla q: {len(self.q_table)}")
            print(f"States: {state}")
            print(f"Indice: {index}\n")

        return self.get_best_action(tabla_puntuaciones)

    def calculo_pesos(self, estados):
        health_status = estados['Health_status']
        energy_status = estados['Energy_status']
        hunger_status = estados['Hunger_status']
        sexual_status = estados['Sexual_status']
        food_status = estados['Food_proximity']

        # Calculo peso health
        if health_status == "very_low":
            weight_health = 0
        elif health_status == "low":
            weight_health = 0.5
        elif health_status == "medium":
            weight_health = 1
        elif health_status == "high":
            weight_health = 1.5
        else:
            weight_health = 2

        # Calculo peso hambre
        if hunger_status == "very_low":
            weight_hunger = 0
        elif hunger_status == "low":
            weight_hunger = 0.5
        elif hunger_status == "medium":
            weight_hunger = 1
        elif hunger_status == "high":
            weight_hunger = 1.5
        else:
            weight_hunger = 2

        # Calculo peso energia
        if energy_status == "very_low":
            weight_energy = 0
        elif energy_status == "low":
            weight_energy = 0.5
        elif energy_status == "medium":
            weight_energy = 1
        elif energy_status == "high":
            weight_energy = 1.5
        else:
            weight_energy = 2

        # Calculo peso sexual
        if sexual_status == "non":
            weight_sexual = 0
        elif sexual_status == "very_low":
            weight_sexual = 0.2
        elif sexual_status == "low":
            weight_sexual = 0.5
        elif sexual_status == "medium":
            weight_sexual = 1
        elif sexual_status == "high":
            weight_sexual = 3
        else:
            weight_sexual = 4

        # Calculo peso sexual
        if sexual_status == "non":
            weight_sexual = 0
        elif sexual_status == "very_low":
            weight_sexual = 0.2
        elif sexual_status == "low":
            weight_sexual = 0.5
        elif sexual_status == "medium":
            weight_sexual = 1
        elif sexual_status == "high":
            weight_sexual = 1.5
        else:
            weight_sexual = 2

        # Calculo peso sexual
        if sexual_status == "non":
            weight_sexual = 0
        elif sexual_status == "very_low":
            weight_sexual = 0.2
        elif sexual_status == "low":
            weight_sexual = 0.5
        elif sexual_status == "medium":
            weight_sexual = 1
        elif sexual_status == "high":
            weight_sexual = 1.5
        else:
            weight_sexual = 2

        # Calculo peso food
        if food_status == "so_close":
            weight_food = 0
        elif food_status == "very_close":
            weight_food = 0.2
        elif food_status == "close":
            weight_food = 0.5
        elif food_status == "medium_distance":
            weight_food = 1
        elif food_status == "far":
            weight_food = 1.5
        else:
            weight_food = 2

        return {
            "weight_health": weight_health,
            "weight_energy": weight_energy,
            "weight_hunger": weight_hunger,
            "weight_sexual": weight_hunger,
            "weight_food": weight_food
        }

    def update_qtable(self, accion):
        """
        Realiza la accion. Si mejora el estado del bicho, palante. Si empeora, menos puntos.
        Se comprueba la vida, el hambre y la energía, y se otorgan recompensas en función de cómo mejoren estos
        atributos, junto con la distancia a la comida y a la pareja más cercana.
        """

        # Obtener atributos antes de la acción
        #estado_ant = self.get_combined_state()
        estados_antes_accion = self.get_states()
        estado_ant = self.get_state(estados_antes_accion)
        atributos_ant = self.get_main_attributes()
        accion(self, self.entorno)  # Realizo la acción
        atributos_act = self.get_main_attributes()
        estados_antes_accion = self.get_states()
        estado_act = self.get_state(estados_antes_accion)
        # Comparación de los atributos antes y después de la acción
        delta_health = atributos_act["health"] - atributos_ant["health"]
        delta_energy = atributos_act["energy"] - atributos_ant["energy"]
        # Queremos que disminuya
        delta_hunger = atributos_ant["hunger"] - atributos_act["hunger"]

        # Solo nos interesa la comida más cercana
        if len(atributos_ant["food_distance"]) > 0 and len(atributos_act["food_distance"]) > 0:
            min_food_dist_ant = atributos_ant["food_distance"][0]
            min_food_dist_act = atributos_act["food_distance"][0]
            # Queremos que disminuya la distancia a la comida más cercana
            delta_food_distance = min_food_dist_ant - min_food_dist_act
        else:
            delta_food_distance = 0

        # Solo nos importa la pareja más cercana
        if len(atributos_ant["partners"]) > 0 and len(atributos_act["partners"]) > 0:
            min_dist_ant = atributos_ant["partners"][0]
            min_dist_act = atributos_act["partners"][0]
            # Queremos que disminuya la distancia a la pareja más cercana
            delta_partners = min_dist_ant - min_dist_act
        else:
            delta_partners = 0

        # Cálculo de la recompensa en base a los cambios en los atributos
        weights = self.calculo_pesos(estados_antes_accion)
        # Ajusta el peso según la importancia
        valor_health = delta_health * weights["weight_health"]
        # Ajusta el peso según la importancia
        valor_energy = delta_energy * weights["weight_energy"]
        # Recompensa más si disminuye el hambre
        valor_hunger = delta_hunger * weights["weight_hunger"]
        # Recompensa por acercarse a la comida más cercana
        valor_food_distance = delta_food_distance * weights["weight_food"]
        # Recompensa por acercarse a la pareja más cercana
        valor_sexual = delta_partners * weights["weight_sexual"]

        recompensa = valor_health + valor_hunger + \
            valor_energy + valor_food_distance + valor_sexual

        # Resto del código para la actualización de la tabla Q
        learning_rate = 0.1
        discount_factor = 0.9

        index_estado_ant = self.states_order.index(estado_ant)
        index_accion_ant = self.actions.index(accion)

        action_act = self.get_action_from_state(estado_ant)

        index_estado_act = self.states_order.index(estado_act)
        index_accion_act = self.actions.index(action_act)

        valor_estado_accion_ant = self.q_table[index_estado_ant][index_accion_ant]
        valor_estado_accion_act = self.q_table[index_estado_act][index_accion_act]

        valor_funcion_tabla_q = valor_estado_accion_ant + learning_rate * (
            recompensa
            + (discount_factor * valor_estado_accion_act)
            - valor_estado_accion_ant
        )
        tamaño_q_table_ant = len(self.q_table)
        
        self.q_table[index_estado_ant][index_accion_ant] = round(
            valor_funcion_tabla_q, 2) 
        if tamaño_q_table_ant != len(self.q_table):
            raise Exception(
                "El tamaño de la tabla q ha variado al actualizarla")

    def get_health_status(self):
        if self.health < 0.2 * MAX_HEALTH:
            return HEALTH_STATUS["very_low"]
        elif self.health < 0.4 * MAX_HEALTH:
            return HEALTH_STATUS["low"]
        elif self.health < 0.6 * MAX_HEALTH:
            return HEALTH_STATUS["medium"]
        elif self.health < 0.8 * MAX_HEALTH:
            return HEALTH_STATUS["high"]
        else:
            return HEALTH_STATUS["very_high"]

    def get_hunger_status(self):
        if self.hunger < 0.2 * MAX_HUNGER:
            return HUNGER_STATUS["very_low"]
        elif self.hunger < 0.4 * MAX_HUNGER:
            return HUNGER_STATUS["low"]
        elif self.hunger < 0.6 * MAX_HUNGER:
            return HUNGER_STATUS["medium"]
        elif self.hunger < 0.8 * MAX_HUNGER:
            return HUNGER_STATUS["high"]
        else:
            return HUNGER_STATUS["very_high"]

    def get_energy_status(self):
        if self.energy < 0.2 * MAX_ENERGY:
            return ENERGY_STATUS["very_low"]
        elif self.energy < 0.4 * MAX_ENERGY:
            return ENERGY_STATUS["low"]
        elif self.energy < 0.6 * MAX_ENERGY:
            return ENERGY_STATUS["medium"]
        elif self.energy < 0.8 * MAX_ENERGY:
            return ENERGY_STATUS["high"]
        else:
            return ENERGY_STATUS["very_high"]

    def get_sexual_status(self):
        if self.libid == 0:
            return SEXUAL_STATUS["non"]
        elif self.libid < 0.2 * MAX_LIBID:
            return SEXUAL_STATUS["very_low"]
        elif self.libid < 0.4 * MAX_LIBID:
            return SEXUAL_STATUS["low"]
        elif self.libid < 0.6 * MAX_LIBID:
            return SEXUAL_STATUS["medium"]
        elif self.libid < 0.8 * MAX_LIBID:
            return SEXUAL_STATUS["high"]
        else:
            return SEXUAL_STATUS["very_high"]

    def get_food_proximity(self):
        _, distances = Actions().check_food(self, self.entorno)
        if not distances:  # Si no hay alimentos cercanos
            return FOOD_STATUS["very_far"]

        shorter_distance = min(
            distances
        )  # Encuentra la distancia más corta a la comida

        # Definir umbrales para las categorías de proximidad
        if shorter_distance < (self.radius + FOOD_RADIUS):
            return FOOD_STATUS["so_close"]
        elif shorter_distance < (self.perception / 5):
            return FOOD_STATUS["very_close"]
        elif shorter_distance < (self.perception / 3):
            return FOOD_STATUS["close"]
        elif shorter_distance < (self.perception / 2):
            return FOOD_STATUS["medium_distance"]
        elif shorter_distance < self.perception:
            return FOOD_STATUS["far"]
        else:
            return FOOD_STATUS["very_far"]


class Entorno:
    def __init__(
        self,
        cells_list: list,
        food_list: list,
        exploration_factor,
    ) -> None:

        random_generator.seed(SEMILLA)
        self.next_id = 0
        self.cells_list = cells_list
        self.food_list = food_list
        self.exploration_factor = exploration_factor
        # Para que cuando se acabe se escriban todas
        self.diccionario_elementos = {}

    def get_food(self, id):
        for food in self.food_list:
            if food.id == id:
                return food
        return None

    def find_food_index_by_id(self, food_list, id):
        for index, food in enumerate(food_list):
            if food.id == id:
                return index
        return None

    def find_cell_index_by_id(self, id):
        for index, cell in enumerate(self.cells_list):
            if cell.id == id:
                return index
        return None

    def delete_cell_by_id(self, id):
        index = self.find_cell_index_by_id(id)
        self.cells_list.pop(index)

    def write_states_order_to_txt(self, states_order, id):
        """
        Escribe el states_order en un archivo de texto.
        """
        ruta_escritura = "./Orden/Tabla_celula_" + str(id) + ".txt"

        contenido = []
        for state in states_order:
            line = ",".join(state)
            contenido.append(f"{line}\n")

        with open(ruta_escritura, "w") as file:
            file.writelines(contenido)

    def write_q_table_to_txt(self, q_table, id):
        ruta_escritura = "./Tablas/Tabla_celula_" + str(id) + ".txt"

        if len(q_table) != TAMAÑO_Q_TABLE:
            print(f"--¡ERROR!-- [TABLA {str(id)}] : al escribir la tabla Q esta tiene un tamaño de\
                    {str(len(q_table))}, cuando debería ser {TAMAÑO_Q_TABLE}")
            sys.exit()
        
        contenido = []
        for state_idx, state in enumerate(q_table):
            if len(state) == 6:
                contenido.append(f"{state}\n")
            else:
                print(f"--¡ERROR!-- [TABLA {str(id)}] : La fila {state_idx} no coincide con el número de acciones. El state es: {state}\n")
                sys.exit()

        if len(contenido) != TAMAÑO_Q_TABLE:
            print(f"--¡ERROR!-- [TABLA {id}] Ha petado. El content tiene \
                  {len(contenido)} y deberia tener {TAMAÑO_Q_TABLE}S\n-----------------------\\n")

        with open(ruta_escritura, "w") as file:
            file.writelines(contenido)


    def write_tables_to_file(self):
        keys = self.diccionario_elementos.keys()
        for key in keys:
            tabla_q = self.diccionario_elementos[key]["tabla_q"]
            states_order = self.diccionario_elementos[key]["states_order"]
            print(f"Se escribe las tablas de la celula {key}")
            self.write_q_table_to_txt(tabla_q, key)
            self.write_states_order_to_txt(states_order, key)

class Food_object:
    def __init__(
        self,
        position_x=None,
        position_y=None,
        color=None,
        food_reserve=None,
        radius=None,
        energy_of_food=None,
        satiating_value=None,
    ):
        self.id = uuid.uuid4()
        self.position_x = position_x
        self.position_y = position_y
        self.color = color
        self.food_reserve = food_reserve
        self.radius = radius
        self.energy_of_food = (
            energy_of_food  # Valor de energia que tiene cada punto de comida
        )
        # Valor saciante de cada valor de comida
        self.satiating_value = satiating_value

    def draw(self, win):
        pygame.draw.circle(
            win, self.color, (int(self.position_x), int(
                self.position_y)), self.radius
        )


class Actions:
    # Movement actions
    def move_right(self, cell: Cell, *args):
        if cell.position_x + cell.speed_x + cell.radius <= WIDTH:
            cell.position_x += cell.speed_x
        cell.last_move_x = +cell.speed_x

    def move_left(self, cell: Cell, *args):
        if cell.position_x - cell.speed_x - cell.radius >= 0:
            cell.position_x -= cell.speed_x
        cell.last_move_x = -cell.speed_x

    def move_up(self, cell: Cell, *args):
        if cell.position_y - cell.speed_y - cell.radius >= 0:
            cell.position_y -= cell.speed_y
        cell.last_move_y = -cell.speed_y

    def move_towards(
        self, cell: Cell, target_x: int, target_y: int
    ):
        dx = target_x - cell.position_x
        dy = target_y - cell.position_y
        dist = math.sqrt(dx**2 + dy**2)
        if dist != 0:
            dx = dx / dist
            dy = dy / dist

        new_position_x = cell.position_x + dx * cell.speed_x
        new_position_y = cell.position_y + dy * cell.speed_y

        if 0 <= new_position_x <= WIDTH:
            cell.position_x = new_position_x
        if 0 <= new_position_y <= HEIGHT:
            cell.position_y = new_position_y

    def move_down(self, cell: Cell, *args):
        if cell.position_y + cell.speed_y + cell.radius <= HEIGHT:
            cell.position_y += cell.speed_y
        cell.last_move_y = +cell.speed_y

    def move_up_right(self, cell: Cell, *args):
        if (
            cell.position_x + cell.speed_x + cell.radius <= WIDTH
            and cell.position_y - cell.speed_y - cell.radius >= 0
        ):
            cell.position_x += cell.speed_x
            cell.position_y -= cell.speed_y
        cell.last_move_x = +cell.speed_x
        cell.last_move_y = -cell.speed_y

    def move_up_left(self, cell: Cell, *args):
        if (
            cell.position_x - cell.speed_x - cell.radius >= 0
            and cell.position_y - cell.speed_y - cell.radius >= 0
        ):
            cell.position_x -= cell.speed_x
            cell.position_y -= cell.speed_y
        cell.last_move_x = -cell.speed_x
        cell.last_move_y = -cell.speed_y

    def move_down_right(self, cell: Cell, *args):
        if (
            cell.position_x + cell.speed_x + cell.radius <= WIDTH
            and cell.position_y + cell.speed_y + cell.radius <= HEIGHT
        ):
            cell.position_x += cell.speed_x
            cell.position_y += cell.speed_y
        cell.last_move_x = +cell.speed_x
        cell.last_move_y = +cell.speed_y

    def move_down_left(self, cell: Cell, *args):
        if (
            cell.position_x - cell.speed_x - cell.radius >= 0
            and cell.position_y + cell.speed_y + cell.radius <= HEIGHT
        ):
            cell.position_x -= cell.speed_x
            cell.position_y += cell.speed_y
        cell.last_move_x = -cell.speed_x
        cell.last_move_y = +cell.speed_y

    def move_random(self, cell: Cell, *args):
        accion = random_generator.randint(0, 7)
        acciones = [
            self.move_right,
            self.move_left,
            self.move_up,
            self.move_down,
            self.move_up_right,
            self.move_up_left,
            self.move_down_right,
            self.move_down_left,
        ]
        acciones[accion](cell)

    # q table actions

    def search_food(self, cell: Cell, entorno: Entorno, *args):
        """
        Busca comida. Si encuentra comida cercana, se mueve hacia ella. Si no encuentra nada, se mueve random_generator.
        """
        shorter_foods, food_distances = self.check_food(cell, entorno)
        if shorter_foods:
            target_food = shorter_foods[0]
            self.move_towards(cell, target_food.position_x,
                              target_food.position_y)
        else:
            self.move_random(cell)

    def search_partner(self, cell: Cell, entorno: Entorno, *args):
        """
        Busca pareja. Si encuentra pareja cercana, se mueve hacia ella. Si no encuentra nada, se mueve random_generator.
        """
        shorter_partners, shorter_partner_distances = self.check_partner(
            cell, entorno)
        if shorter_partners:
            target_partner = shorter_partners[0]
            self.move_towards(
                cell, target_partner.position_x, target_partner.position_y
            )
        else:
            self.move_random(cell)

    def cruce(self, cell_1: Cell, cell_2: Cell):
        """
        Devuelve el states_order y los multiplicadores de herencia tras el cruce
        """
        # -------States order primero-------
        states_order_1 = cell_1.states_order
        states_order_2 = cell_2.states_order

        if random_generator.randint(0, 1) == 0:
            padre_principal = states_order_1
            padre_secundario = states_order_2
        else:
            padre_principal = states_order_2
            padre_secundario = states_order_1

        n_mantenidos = random_generator.randint(
            3, len(padre_principal) - 2
        )  # Elijo el numero de valores del padre que se van a mantener
        posiciones = random_generator.sample(
            range(len(padre_principal)), n_mantenidos
        )  # Elijo las posiciones del padre que se van a mantener
        states_order_hijo = [-1] * len(
            padre_principal
        )  # Lo inicializo a -1 el array entero

        for posicion in posiciones:  # Guardo lo del padre
            states_order_hijo[posicion] = padre_principal[posicion]

        # Llenar las posiciones restantes con valores del padre_secundario
        for i, valor in enumerate(states_order_hijo):
            if valor == -1:
                valor_secundario = padre_secundario[i]
                # Si el valor de padre_secundario ya está en states_order_hijo, buscar en adyacentes
                if valor_secundario in states_order_hijo:
                    # Buscar en adyacentes
                    encontrado = False
                    offset = 1
                    while not encontrado:
                        # Buscar a la izquierda
                        izquierda = (i - offset) % len(padre_secundario)
                        if padre_secundario[izquierda] not in states_order_hijo:
                            states_order_hijo[i] = padre_secundario[izquierda]
                            encontrado = True
                            break
                        # Buscar a la derecha
                        derecha = (i + offset) % len(padre_secundario)
                        if padre_secundario[derecha] not in states_order_hijo:
                            states_order_hijo[i] = padre_secundario[derecha]
                            encontrado = True
                            break
                        offset += 1
                else:
                    # Si el valor de padre_secundario no está en states_order_hijo, asignarlo
                    states_order_hijo[i] = valor_secundario
        # TODO: añadir mutacion aqui para que sea mas complejo
        # ----------------------------------
        impulsito_1 = cell_1.impulsito
        life_expectancy_1 = cell_1.life_expectancy
        perception_1 = cell_1.perception

        # Variables del segundo padre
        impulsito_2 = cell_2.impulsito
        life_expectancy_2 = cell_2.life_expectancy
        perception_2 = cell_2.perception

        # Crear hijo con blending crossover
        alpha = (
            0.5  # Puedes ajustar este valor para mayor o menor influencia de los padres
        )
        impulsito_hijo = alpha * impulsito_1 + (1 - alpha) * impulsito_2
        life_expectancy_hijo = (
            alpha * life_expectancy_1 + (1 - alpha) * life_expectancy_2
        )
        perception_hijo = alpha * perception_1 + (1 - alpha) * perception_2

        multiplicadores = {
            "impulsito": 1.05,
            "longevidad": 1.05,
            "percepcion": 1.05,
        }

        return states_order_hijo, multiplicadores

    def explore(self, cell: Cell, *args):
        """
        Explora otras zonas moviéndose aleatoriamente o siguiendo la dirección del último movimiento.
        Esto aumenta la probabilidad de encontrar comida en nuevas áreas.
        """
        if cell.last_move_x is not None and cell.last_move_y is not None:
            # Explora siguiendo la dirección del último movimiento con algo de aleatoriedad
            dx = cell.last_move_x + \
                random_generator.uniform(-1, 1) * cell.speed_x
            dy = cell.last_move_y + \
                random_generator.uniform(-1, 1) * cell.speed_y
        else:
            # Si no hay un movimiento previo, se mueve aleatoriamente
            dx = random_generator.uniform(-1, 1) * cell.speed_x
            dy = random_generator.uniform(-1, 1) * cell.speed_y

        # Calcula la nueva posición de la célula
        new_position_x = cell.position_x + dx
        new_position_y = cell.position_y + dy

        # Mantén la célula dentro de los límites del entorno
        if 0 <= new_position_x <= WIDTH:
            cell.position_x = new_position_x
        if 0 <= new_position_y <= HEIGHT:
            cell.position_y = new_position_y

    def cruce_viable(self, sex_status_1, sex_status_2):
        probabilidad = 0

        if (
            sex_status_1 == SEXUAL_STATUS["high"]
            and sex_status_2 == SEXUAL_STATUS["high"]
        ):
            probabilidad = 1.0  # 100%
        elif (
            sex_status_1 == SEXUAL_STATUS["high"]
            and sex_status_2 == SEXUAL_STATUS["medium"]
        ) or (
            sex_status_1 == SEXUAL_STATUS["medium"]
            and sex_status_2 == SEXUAL_STATUS["high"]
        ):
            probabilidad = 0.75  # 75%
        elif (
            sex_status_1 == SEXUAL_STATUS["high"]
            and sex_status_2 == SEXUAL_STATUS["low"]
        ) or (
            sex_status_1 == SEXUAL_STATUS["low"]
            and sex_status_2 == SEXUAL_STATUS["high"]
        ):
            probabilidad = 0.5  # 50%
        elif (
            sex_status_1 == SEXUAL_STATUS["medium"]
            and sex_status_2 == SEXUAL_STATUS["medium"]
        ):
            probabilidad = 0.50  # 50%
        elif (
            sex_status_1 == SEXUAL_STATUS["medium"]
            and sex_status_2 == SEXUAL_STATUS["low"]
        ) or (
            sex_status_1 == SEXUAL_STATUS["low"]
            and sex_status_2 == SEXUAL_STATUS["medium"]
        ):
            probabilidad = 0.20  # 20%
        elif (
            sex_status_1 == SEXUAL_STATUS["low"]
            and sex_status_2 == SEXUAL_STATUS["low"]
        ):
            probabilidad = 0.05  # 5%

        # Generar un número aleatorio entre 0 y 1
        random_value = random_generator.random()

        # Verificar si el cruce es viable basándose en la probabilidad
        return random_value <= probabilidad

    def to_breed(self, cell: Cell, entorno: Entorno, *args):
        """
        Los individuos tienen que estar sexualmente activos.
        Dependiendo del nivel de actividad sexual, hay mas posibilidades o menos de que se reproduzcan.
        Cruza dos individuos y crea una nueva celula entre la celula principal y la mas cercana que tenga.
        Consume mucha energia del padre principal que quiere reproducirse, ya que es el que hace toda al accion.
        Pone libido a 0.
        """
        shorter_partners, shorter_partner_distances = self.check_partner(
            cell, entorno)
        estado_sex_cell = cell.get_sexual_status()

        if shorter_partners and shorter_partner_distances[0] < cell.radius * 2:
            # Verificar que la célula principal no sea "non_fertil"
            if estado_sex_cell != SEXUAL_STATUS["non"]:
                if shorter_partners:  # Si hay mas individuos
                    partner = shorter_partners[0]
                    estado_sex_partner = partner.get_sexual_status()
                    if estado_sex_partner != SEXUAL_STATUS["non"]:
                        # Se cruzan si es viable, sino no se cruzan
                        if self.cruce_viable(estado_sex_cell, estado_sex_partner):
                            dx = partner.position_x - cell.position_x
                            dy = partner.position_y - cell.position_y
                            distance = math.sqrt(dx**2 + dy**2)

                            if distance < cell.radius + partner.radius:
                                # Cruce
                                acciones = [
                                    Actions().search_food,
                                    Actions().search_partner,
                                    Actions().to_breed,
                                    Actions().rest,
                                    Actions().eat,
                                    Actions().explore
                                ]

                                states_order_hijo, multiplicadores = self.cruce(
                                    cell, partner
                                )

                                # Calculamos la posición del hijo cerca de los padres
                                hijo_x = (
                                    cell.position_x + partner.position_x
                                    # Cerca de los padres
                                ) / 2 + random_generator.randint(-10, 10)
                                hijo_y = (
                                    cell.position_y + partner.position_y
                                ) / 2 + random_generator.randint(-10, 10)

                                # Nos aseguramos de que la posición esté dentro de los límites
                                hijo_x = max(0, min(WIDTH, hijo_x))
                                hijo_y = max(0, min(HEIGHT, hijo_y))

                                hijo = Cell(
                                    id=entorno.next_id,
                                    position_x=hijo_x,
                                    position_y=hijo_y,
                                    radius=RADIUS,
                                    color=RED,
                                    speed_x=3,
                                    speed_y=3,
                                    health=100,
                                    age=0,
                                    hunger=20,  # Saciado
                                    energy=100,
                                    libid=0,
                                    # states_order=states_order_hijo,
                                    herencia=multiplicadores,
                                    actions=acciones,
                                )
                                entorno.next_id += 1
                                entorno.cells_list.append(hijo)
                                hijo.entorno = entorno
                                hijo.start()
                                energy_to_sub = 40

                                cell.libid = 0
                                cell.cd_reproduction = 0  

                                if cell.energy - energy_to_sub > 0:
                                    cell.energy -= energy_to_sub
                                else:
                                    cell.energy = 0

                                partner_index = entorno.find_cell_index_by_id(
                                    partner.id
                                )
                                entorno.cells_list[
                                    partner_index
                                ].libid = 0  # Libido a 0 porque se ha reproducido
                                entorno.cells_list[partner_index].cd_reproduction = 50

                                if (
                                    entorno.cells_list[partner_index].energy
                                    - energy_to_sub
                                    > 0
                                ):
                                    entorno.cells_list[
                                        partner_index
                                    ].energy -= energy_to_sub
                                else:
                                    entorno.cells_list[partner_index].energy = 0

    def move_to_partner(self, cell: Cell, *args): ...

    def move_to_food(self, cell: Cell, *args): ...

    def rest(self, cell: Cell, *args):
        """
        La celula se queda quieta, lo que aumenta la energia
        """
        if cell.energy + 5 < 100:
            cell.energy += 5
        else:
            cell.energy = 100

    def run_away(self, cell: Cell, *args): ...

    def eat(self, cell: Cell, entorno: Entorno, *args):
        # Come y recupera energia
        shorter_foods = cell.shorter_foods

        cell.food_from_bite = 10

        # if distance < cell.radius + partner.radius:
        if shorter_foods:
            comida = shorter_foods[0]

            dx = comida.position_x - cell.position_x
            dy = comida.position_y - cell.position_y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < cell.radius + comida.radius:  # Si puede comer
                if comida.food_reserve > cell.food_from_bite:
                    cell.energy += (
                        comida.energy_of_food * cell.food_from_bite
                    )  # Recupera energia
                    cell.hunger -= (
                        comida.satiating_value * cell.food_from_bite
                    )  # Se sacia lo que se puede saciar por un bocado
                    comida.food_reserve -= cell.food_from_bite

                elif comida.food_reserve > 0:
                    cell.energy += comida.food_reserve * comida.energy_of_food
                    cell.hunger -= (
                        comida.satiating_value * comida.food_reserve
                    )  # Se quita el hambre en base a lo que ha podido comer
                    comida.food_reserve = 0

                if cell.hunger < 0:
                    cell.hunger = 0

                if cell.energy > MAX_ENERGY:
                    cell.energy = MAX_ENERGY

                if comida.food_reserve == 0:
                    cell.shorter_foods[1:]
                    id = comida.id
                    comidas = entorno.food_list
                    index = entorno.find_food_index_by_id(comidas, id)

                    entorno.food_list.pop(index)

                    new_food_probability = 50
                    # Si menor o igual que 50, se crea una. Si mayor que 50 se crean 2 comidas
                    if (
                        random_generator.randint(0, 100) > 50
                    ):
                        for _ in range(2):
                            food = Food_object(
                                position_x=random_generator.randint(0, WIDTH),
                                position_y=random_generator.randint(1, HEIGHT),
                                color=GREEN,
                                food_reserve=200,
                                radius=RADIUS,
                                energy_of_food=10,
                                satiating_value=10,
                            )
                            entorno.food_list.append(food)
                    else:
                        food = Food_object(
                            position_x=random_generator.randint(0, WIDTH),
                            position_y=random_generator.randint(1, HEIGHT),
                            color=GREEN,
                            food_reserve=200,
                            radius=RADIUS,
                            energy_of_food=10,
                            satiating_value=10,
                        )
                        entorno.food_list.append(food)
    # Important actions

    def avoid_collision(self, cell: Cell, entorno: Entorno, *args):
        cells = entorno.cells_list
        for other_cell in cells:
            if other_cell.id != cell.id:
                dx = other_cell.position_x - cell.position_x
                dy = other_cell.position_y - cell.position_y
                distance = math.sqrt(dx**2 + dy**2)
                if distance < cell.radius + other_cell.radius:
                    overlap = cell.radius + other_cell.radius - distance
                    cell.position_x -= dx / distance * overlap / 2
                    cell.position_y -= dy / distance * overlap / 2
                    other_cell.position_x += dx / distance * overlap / 2
                    other_cell.position_y += dy / distance * overlap / 2

        foods = entorno.food_list
        for food in foods:
            if food.id != cell.id:
                dx = food.position_x - cell.position_x
                dy = food.position_y - cell.position_y
                distance = math.sqrt(dx**2 + dy**2)
                if distance < cell.radius + food.radius:
                    overlap = cell.radius + food.radius - distance
                    cell.position_x -= dx / distance * overlap / 2
                    cell.position_y -= dy / distance * overlap / 2

    def check_partner(self, cell: Cell, entorno: Entorno, *args):
        # Comprueba si la pareja está suficientemente cerca como para procrear
        # Devuelve las pareja más cercanas ordenadas por distancia

        distances = []
        cells = entorno.cells_list
        max_distance = cell.perception

        for partner in cells:
            if partner.id != cell.id:
                dx = partner.position_x - cell.position_x
                dy = partner.position_y - cell.position_y
                distance = math.sqrt(
                    dx**2 + dy**2
                )  # Comprobar que la distancia sea menor de un valor
                if distance < max_distance:
                    distances.append(
                        (partner, distance)
                    )  # Guardar el objeto de pareja y su distancia

        # Ordenar las tuplas (food, distance) por la distancia
        sorted_distances = sorted(distances, key=lambda x: x[1])

        # Extraer y devolver las comidas ordenadas por distancia
        sorted_partners = [partner for partner, distance in sorted_distances]

        # Extraer solo las distancias ordenadas
        sorted_distances_only = [
            distance for partner, distance in sorted_distances]

        # Aquí devolvemos las comidas ordenadas, las distancias ordenadas, y la segunda tupla de la lista original
        return sorted_partners, sorted_distances_only

    def check_food(self, cell: Cell, entorno: Entorno, *args):
        # Comprueba si la comida está suficientemente cerca como para comer
        # Devuelve las comidas más cercanas ordenadas por distancia

        distances = []
        foods = entorno.food_list
        max_distance = cell.perception

        for food in foods:
            dx = food.position_x - cell.position_x
            dy = food.position_y - cell.position_y
            distance = math.sqrt(
                dx**2 + dy**2
            )  # Comprobar que la distancia sea menor de un valor
            if distance < max_distance:
                distances.append(
                    (food, distance)
                )  # Guardar el objeto de comida y su distancia

        # Ordenar las tuplas (food, distance) por la distancia
        sorted_distances = sorted(distances, key=lambda x: x[1])

        # Extraer y devolver las comidas ordenadas por distancia
        sorted_foods = [food for food, distance in sorted_distances]

        # Extraer solo las distancias ordenadas
        sorted_distances_only = [
            distance for food, distance in sorted_distances]
        # print("Sorted distances only: ", sorted_distances_only)

        # Aquí devolvemos las comidas ordenadas, las distancias ordenadas, y la segunda tupla de la lista original
        return sorted_foods, sorted_distances_only
