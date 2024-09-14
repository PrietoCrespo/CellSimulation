from abc import abstractmethod
import math
import random
import pygame
import uuid
from vars import *
import numpy as np

class Cell:

    def __init__(self,position_x=None,position_y=None,radius=None,color=None,speed_x=None,speed_y=None,health=None,age=None,food=None,max_food=None,energy=None,libid=None,herencia=None,states_order=None,actions=None):
        self.id = uuid.uuid4()  # Genera un ID único
        #print("Id: "+str(self.id))
        self.position_x = position_x
        self.position_y = position_y
        self.radius = 10
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.last_move_x = None
        self.last_move_y = None
        self.health = health
        self.max_health = health
        self.age = age
        self.food = food
        self.max_food = max_food
        self.energy = energy
        self.libid = libid
        self.states_order = states_order
        self.actions = actions
        self.impulsito = herencia.get("impulsito")
        self.life_expectancy = random.randint(RANGO_EDAD_MAXIMA[0],RANGO_EDAD_MAXIMA[1]) * herencia.get("longevidad") #Quiza meterle algo random tmb
        self.perception = random.randint(RANGO_PERCEPCION[0],RANGO_PERCEPCION[1]) * herencia.get("percepcion")
        self.shorter_foods = list() # Empieza vacio, pues no se le ha pasado aun. Se actualiza por tick
        #Establezco los valores para valores-Estado
        n_estados = len(states_order)
        n_acciones = len(actions)
        lista_valores_estado = []

        for _ in range(n_estados):
            lista_valores_estado.append([0]*n_acciones)
        self.q_table = lista_valores_estado

    def move(self, actions: "Actions"):
        actions.move_random(self)
    
    def get_main_attributes(self):
        return {"health":self.get_health_status,
                "energy":self.get_energy_status,
                "food":self.get_hunger_status}

    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.position_x), int(self.position_y)), self.radius)

    def life_update(self,foods_distance:list,): #Actualiza cada tick
        '''
        Devuelve 'True' si está vivo el individuo.
        Devuelve 'False' si ha muerto.
        '''
        #TODO: que en base a los estados empiecen a tomar decisiones
        #Actualizo edad
        if (self.age + 0.5) < self.life_expectancy:
            self.age += 0.1 #0.1 año por cada tick
        else:
            return False

        #Actualizacion libido
        self.libido()

        #Come
        self.eat_from_food_reserve() 
        
        #Actualizo energia
        if self.energy - 0.2 > 0:
            self.energy -= 0.2
            self.energy = round(self.energy, 2)

        #Si pasa hambre
        if self.food == 0:
            self.health -= 1
            if self.health <= 0:
                return False
        

        self.energy = round(self.energy, 2)
        self.food = round(self.food, 2)
        
        return True

        
    def libido(self):
        age = self.age
        impulsito = self.impulsito
        mu = self.life_expectancy / 3  # Edad en la que la líbido es máxima
        sigma = self.life_expectancy / 6  # Controla el ancho de la campana

        if self.age <= 0.2 * self.life_expectancy: # Si no está en edad fértil
            self.libid = 0 
        else:
            self.libid = 100 * math.exp(-((age - mu) ** 2) / (2 * sigma ** 2)) * impulsito

    def get_states(self,foods_distance:list): 
        """
        Devuelve los estados de vida, comida, energia, sexual y cercania comida de la celula.
        """
        health_status = self.get_health_status()
        hunger_status = self.get_hunger_status()
        energy_status = self.get_energy_status()
        sexual_status = self.get_sexual_status()
        food_proximity = self.get_food_proximity(foods_distance)

        return {"Health_status": health_status,
                "Hunger status": hunger_status,
                "Energy status": energy_status,
                "Sexual status": sexual_status,
                "Food proximity": food_proximity
                }
        


    def get_state(self,states_dict:dict):
        """
        Devuelve, en base al orden de estados que tiene la celula, el estado actual

        """
        for state in self.states_order:
            print("State: ",str(state))
            if state in states_dict.values():
                return state

    def get_best_action(self,puntuaciones:list):
            """
            Devuelve la mejor accion en base de la fila de un estado
            """

            #Valor maximo de las puntuaciones
            valor_max = np.max(puntuaciones)
            #Encuentra todos los indices de valor maximo
            indices_max = np.where(puntuaciones == valor_max)[0] 
            
            if len(indices_max) > 1: 
                indice = random.choice(indices_max)
            else:
                indice = np.argmax(puntuaciones)
            
            return self.actions[indice]


    def get_action_from_state(self,states_dict:dict): 
        """
        Devuelve la accion a realizar basandose en el estado actual.
        Recorre la tabla q y busca el primer estado que coincide con el que tenga la célula
        Una vez encontrado, va a buscar la accion que deberia realizar en base a la tabla q.

        States_dict contiene los estados de la celula de cada uno de los tipos (energia, salud, etc.)
        """
        
        for state in self.states_order:
            print("State: ",str(state))
            if state in states_dict.values(): #TODO comprobar que hace bien esta comprobacion
                #Indice del estado
                index = self.states_order.index(state) 
                #Tabla del estado 
                tabla_puntuaciones = self.q_table[index] 
                return self.get_best_action(tabla_puntuaciones)

    def update_qtable(self, estados_ant, estados_act):
        """
        Realiza la accion. Si mejora el estado del bicho, palante. Si empeora, menos puntos.
        Comprueba la vida, el hambre y la energia
        """        

        #Comparo health
        estado_ant_health = estados_ant['health']
        estado_act_health = estados_act['health']
        valor_health = self.compare_health_status(estado_ant_health,estado_act_health)

        #Comparo energy
        estado_ant_energy = estados_ant['energy']
        estado_act_energy = estados_act['energy']
        valor_energy = self.compare_energy_status(estado_ant_energy,estado_act_energy)
    
        #Comparo food
        estado_ant_hunger = estados_ant['food']
        estado_act_hunger = estados_act['food']
        valor_hunger = self.compare_hunger_status(estado_ant_hunger,estado_act_hunger)

        recompensa = valor_health + valor_health + valor_hunger + valor_energy
        learning_rate = 0.1
        discount_factor = 0.9

        index_estado = self.states_order.index(state) # Indice del estado actual del individuo
        index_accion = self.actions.index(action) # Indice de la accion
        #TODO: terminar de definir como hacer la funcion de la tabla q
        valor_estado_accion = self.q_table[index_estado][index_accion]

        valor_final = valor_estado_accion + learning_rate * (recompensa + discount_factor * ) #TODO: terminar de hacer esto

    def compare_health_status(self,health_status_ant,health_status_act):
        """
            Devuelve el numero de estados de diferencia que hay entre ambos. 
            En caso de empeorar el estado, devuelve un valor negativo.
        """ 
        if health_status_ant == health_status_act:
            return 0
        elif health_status_ant == HEALTH_STATUS["high"] and health_status_act == HEALTH_STATUS["medium"]:
            return -1
        elif health_status_ant == HEALTH_STATUS["high"] and health_status_act == HEALTH_STATUS["low"]:
            return -2
        elif health_status_ant == HEALTH_STATUS["medium"] and health_status_act == HEALTH_STATUS["high"]:
            return 1
        elif health_status_ant == HEALTH_STATUS["low"] and health_status_act == HEALTH_STATUS["high"]:
            return 2
            
    def compare_energy_status(self,energy_status_ant,energy_status_act):
        if energy_status_ant == energy_status_act:
            return 0
        elif energy_status_ant == ENERGY_STATUS["high"] and energy_status_act == ENERGY_STATUS["medium"]:
            return -1
        elif energy_status_ant == ENERGY_STATUS["high"] and energy_status_act == ENERGY_STATUS["low"]:
            return -2
        elif energy_status_ant == ENERGY_STATUS["medium"] and energy_status_act == ENERGY_STATUS["high"]:
            return 1
        elif energy_status_ant == ENERGY_STATUS["low"] and energy_status_act == ENERGY_STATUS["high"]:
            return 2

    def compare_hunger_status(self,hunger_status_ant,hunger_status_act):
        if hunger_status_ant == hunger_status_act:
            return 0
        elif hunger_status_ant == HUNGER_STATUS["high"] and hunger_status_act == HUNGER_STATUS["medium"]:
            return 1
        elif hunger_status_ant == HUNGER_STATUS["high"] and hunger_status_act == HUNGER_STATUS["low"]:
            return 2
        elif hunger_status_ant == HUNGER_STATUS["medium"] and hunger_status_act == HUNGER_STATUS["high"]:
            return -1
        elif hunger_status_ant == HUNGER_STATUS["low"] and hunger_status_act == HUNGER_STATUS["high"]:
            return -2
    
    def get_health_status(self):
        if self.health < 0.3*MAX_HEALTH:
            return HEALTH_STATUS["low"]
        elif self.health < 0.6*MAX_HEALTH: 
            return HEALTH_STATUS["medium"]
        else: 
            return HEALTH_STATUS["high"]  
    

    def get_hunger_status(self):
        if self.food < 0.3*MAX_FOOD:
            return HUNGER_STATUS["high"]
        elif self.food < 0.6*MAX_FOOD: 
            return HUNGER_STATUS["medium"]
        else: 
            return HUNGER_STATUS["low"]  
    
    def get_energy_status(self):
        if self.energy < 0.3*MAX_ENERGY:
            return ENERGY_STATUS["low"]
        elif self.energy < 0.6*MAX_ENERGY: 
            return ENERGY_STATUS["medium"]
        else: 
            return ENERGY_STATUS["high"]
    

    def get_sexual_status(self):
        if self.libid == 0:
            return SEXUAL_STATUS["non"]
        elif self.libid < 0.3*MAX_LIBID:
            return SEXUAL_STATUS["low"]
        elif self.libid < 0.6*MAX_LIBID:
            return SEXUAL_STATUS["medium"]
        else:
            return SEXUAL_STATUS["high"]
    

    def get_food_proximity(self,distances:list): 
        if len(distances) > 0:
            shorter_distance = distances[0]
            if shorter_distance < (self.radius + FOOD_RADIUS):
                return FOOD_STATUS["so_close"]
            elif shorter_distance < (self.perception / 2):
                return FOOD_STATUS["close"]
            elif shorter_distance < self.perception and shorter_distance > (self.perception / 2):
                return FOOD_STATUS["detected"]
        else:
            return FOOD_STATUS["non"]
            

    def eat_from_food_reserve(self):
        if self.food > 0 and self.energy < 80:
            #1 de comida es 4 de energia
            #Cuanto mas hambre, mas come
            
            if self.energy < 100:
                food = 0.2
            elif self.energy < 80:
                food = 1
            elif self.energy < 40:
                food = 3
            elif self.energy < 20:
                food = 5
            elif self.energy == 0:
                food = 8
            
            if self.food - food < 0: #Me como toda la comida restante
                food = self.food

            self.food -= food
            #print("\tCome")
            if self.energy + (food*4) > 100:
                self.energy = 100
            else:
                self.energy += (food*4)

class Entorno:
    def __init__(self, cells_list:list, food_list: list, ) -> None:
        self.cells_list = cells_list
        self.food_list = food_list

    def get_food(self, id):
        
        for food in self.food_list:
            if food.id == id:
                return food
        return None
    
    def find_food_index_by_id(food_list, id):
        for index, food in enumerate(food_list):
            if food.id == id:
                return index
        return None  
    
    def remove_food(self, id): # TODO: implementar o borrar, segun si puedo usarlo
        ...


class Food_object:

    def __init__(self,position_x=None,position_y=None,color=None,food_reserve=None,radius=None):
        self.id = uuid.uuid4()
        self.position_x = position_x
        self.position_y = position_y
        self.color = color
        self.food_reserve = food_reserve
        self.radius = radius

    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.position_x), int(self.position_y)), self.radius)


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

    def move_towards(self, cell: Cell, target_x: int, target_y: int): # TODO: ver como hacer esto
        dx = target_x - cell.position_x
        dy = target_y - cell.position_y
        dist = math.sqrt(dx ** 2 + dy ** 2)
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
        if cell.position_x + cell.speed_x + cell.radius <= WIDTH and cell.position_y - cell.speed_y - cell.radius >= 0:
            cell.position_x += cell.speed_x
            cell.position_y -= cell.speed_y
        cell.last_move_x = +cell.speed_x
        cell.last_move_y = -cell.speed_y

    def move_up_left(self, cell: Cell, *args):
        if cell.position_x - cell.speed_x - cell.radius >= 0 and cell.position_y - cell.speed_y - cell.radius >= 0:
            cell.position_x -= cell.speed_x
            cell.position_y -= cell.speed_y
        cell.last_move_x = -cell.speed_x
        cell.last_move_y = -cell.speed_y

    def move_down_right(self, cell: Cell, *args):
        if cell.position_x + cell.speed_x + cell.radius <= WIDTH and cell.position_y + cell.speed_y + cell.radius <= HEIGHT:
            cell.position_x += cell.speed_x
            cell.position_y += cell.speed_y
        cell.last_move_x = +cell.speed_x
        cell.last_move_y = +cell.speed_y

    def move_down_left(self, cell: Cell, *args):
        if cell.position_x - cell.speed_x - cell.radius >= 0 and cell.position_y + cell.speed_y + cell.radius <= HEIGHT:
            cell.position_x -= cell.speed_x
            cell.position_y += cell.speed_y
        cell.last_move_x = -cell.speed_x
        cell.last_move_y = +cell.speed_y

    def move_random(self, cell: Cell, *args):
        accion = random.randint(0, 7)
        acciones = [self.move_right, self.move_left, self.move_up, self.move_down, self.move_up_right, self.move_up_left,
                    self.move_down_right, self.move_down_left]
        acciones[accion](cell)

    # General actions 

    def search_food(self, cell:Cell, *args):
        ...
    
    def search_partner(self, cell:Cell, *args):
        ...
    
    def move_to_partner(self,cell:Cell, *args):
        ...
    
    def move_to_food(self,cell:Cell, *args):
        ...
    
    def to_breed(self,cell: Cell, *args):
        ...
    
    def rest(self,cell:Cell, *args):
        ...
    
    def run_away(self,cell:Cell, *args):
        ...

    def eat(self, cell: Cell, entorno: Entorno, *args):
        shorter_foods = cell.shorter_foods
        if shorter_foods[0].food_reserve > 10:
            cell.food += 10
            shorter_foods[0].food_reserve -= 10
        elif shorter_foods[0].food_reserve > 0:
            cell.food += shorter_foods[0].food_reserve
            shorter_foods[0].food_reserve = 0
        
        if cell.food > cell.max_food:
            cell.food = cell.max_food
        
        if shorter_foods[0].food_reserve == 0:
            cell.shorter_foods[1:] # TODO: terminar de borrar del entorno la comida
            id = shorter_foods[0].id
            comidas = entorno.food_list
            index = entorno.find_food_index_by_id(id)
            entorno.food_list.pop(index) #TODO: comprobar que lo borra bien

    def search_food(self, cell: Cell = None, *args):
        ...
        
    # Important actions

    def avoid_collision(self, cell: Cell, entorno: Entorno, *args):
        cells = entorno.cells_list
        for other_cell in cells:
            if other_cell.id != cell.id:
                dx = other_cell.position_x - cell.position_x
                dy = other_cell.position_y - cell.position_y
                distance = math.sqrt(dx ** 2 + dy ** 2)
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
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance < cell.radius + food.radius:
                    overlap = cell.radius + food.radius - distance
                    cell.position_x -= dx / distance * overlap / 2
                    cell.position_y -= dy / distance * overlap / 2
    
    def check_food(self, cell: Cell, entorno: Entorno, *args):
        # Comprueba si la comida está suficientemente cerca como para comer
        # Devuelve las comidas más cercanas ordenadas por distancia

        distances = []
        foods = entorno.food_list
        max_distance = cell.perception
        
        for food in foods:
            dx = food.position_x - cell.position_x
            dy = food.position_y - cell.position_y
            distance = math.sqrt(dx ** 2 + dy ** 2)  # Comprobar que la distancia sea menor de un valor
            if distance < max_distance:
                distances.append((food, distance))  # Guardar el objeto de comida y su distancia

        # Ordenar las tuplas (food, distance) por la distancia
        sorted_distances = sorted(distances, key=lambda x: x[1])

        # Extraer y devolver las comidas ordenadas por distancia
        sorted_foods = [food for food, distance in sorted_distances]

        # Extraer solo las distancias ordenadas
        sorted_distances_only = [distance for food, distance in sorted_distances]
        #print("Sorted distances only: ", sorted_distances_only)

        # Aquí devolvemos las comidas ordenadas, las distancias ordenadas, y la segunda tupla de la lista original
        return sorted_foods, sorted_distances_only