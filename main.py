import sys
import pygame
from clases import Actions, Cell, Entorno, Food_object
from vars import *
import random
# Cargar las variables de entorno del archivo .env

# Inicializar Pygame
pygame.init()

# Dimensiones de la ventana
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Células")

# Crear una lista de células y de comida
cells = []
foods = []
all_states_values = list(HUNGER_STATUS.values()) + list(HEALTH_STATUS.values()) + list(ENERGY_STATUS.values()) + list(SEXUAL_STATUS.values()) + list(FOOD_STATUS.values())
acciones = [Actions.search_food,Actions.search_partner,Actions.move_to_food,Actions.eat,Actions.move_to_partner,Actions.to_breed,Actions.rest,Actions.run_away]

# Lista células
for _ in range(INITIAL_CELLS_NUMBER):
    multiplicadores = {
        "impulsito": 1.05,
        "longevidad": 1.05,
        "percepcion": 1.05,
    }
    random.shuffle(all_states_values)
    print("Orden estados: "+str(all_states_values))
    cell = Cell(position_x=random.randint(0, WIDTH),
                position_y=random.randint(1, HEIGHT),
                radius=RADIUS,
                color=RED,
                speed_x=3,
                speed_y=3,
                health=100,
                age=0,  
                food=80,  # Saciado
                max_food = 80,
                energy=100,
                libid=0,
                states_order=all_states_values,
                herencia=multiplicadores,
                actions=acciones
                )
    cells.append(cell)

#Lista comida
for _ in range(INITIAL_FOOD_NUMBER):
    food = Food_object(position_x=random.randint(0, WIDTH),
                    position_y=random.randint(1, HEIGHT),
                    color=GREEN,
                    food_reserve=200,
                    radius=RADIUS
                    )
    foods.append(food)

entorno = Entorno(cells_list=cells, food_list=foods)

# Bucle principal
running = True
while running:
    pygame.time.delay(30)  # Controlar la velocidad del bucle

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Mover y dibujar las células
    win.fill(BROWN)
    if len(cells) > 0:
        for cell in cells:
            # Mover la célula hacia la comida más cercana
            #--------------------------------------------
            shorter_foods, food_distances = Actions().check_food(cell,foods,300)
            estados = cell.get_states(food_distances)
            print(estados)

            if estados['Food proximity'] == 'food_so_close':
                ...
                #Actions().eat(cell,shorter_foods,foods)
            if shorter_foods:
                target_food = shorter_foods[0]
                Actions().move_towards(cell, target_food.position_x, target_food.position_y)
            else:
                Actions().move_random(cell)
            #--------------------------------------------
            shorter_foods, food_distances = Actions().check_food(cell,foods,300)
            cell.shorter_foods = shorter_foods #Actualizo shorter foods del bicho

            estados_ant = cell.get_states(food_distances) # Se obtiene estados actuales celula
            estado_ant = cell.get_state(estados) # Obtiene el estado en el que se encuentra antes de realizar la accion
            
            accion = cell.get_action_from_state(estado_ant)
            # TODO: Realizo la accion

            estados_act = cell.get_states(food_distances) # Se obtiene estados actuales celula
            estado_ant = cell.get_state(estados) # Obtiene el estado en el que se encuentra antes de realizar la accion


            best_action = cell.return_action(estados)
            print(best_action)
            sys.exit()
            
            #Evita colision con otros objetos
            Actions().avoid_collision(cell, cells,foods)
            cell.draw(win)
            if not cell.life_update(food_distances):
                cells.remove(cell)
    else:
        break

    # Dibujar la comida
    if len(foods) > 0:
        for food in foods:
            food.draw(win)

    pygame.display.update()

# Salir de Pygame
pygame.quit()
