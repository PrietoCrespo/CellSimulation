import random

WIDTH=1800
HEIGHT=900
MAX_SPEED=3
MIN_SPEED=0
WHITE=255,255,255
BLACK=0,0,0
RED=255,0,0
BROWN=209,131,53
GREEN=0,255,0
SEMILLA = 1
RADIUS = 10
FOOD_RADIUS = 10
RANGO_EDAD_MAXIMA = [800,950] #ticks
RANGO_PERCEPCION = [100,450]
TAMAÑO_Q_TABLE = 29

#VALORES CELULA
MAX_ENERGY = 100
MAX_HUNGER = 80
MAX_HEALTH = 100
MAX_LIBID = 100
FOOD_FROM_BITE = 10
random_generator = random.Random(1)
PASO_EDAD = 0.1
#--------------

INITIAL_CELLS_NUMBER = 9
INITIAL_FOOD_NUMBER = 20

#States


HUNGER_STATUS = {
    "very_high": "very_high_hunger",
    "high": "high_hunger",
    "medium": "medium_hunger",
    "low": "low_hunger",
    "very_low": "very_low_hunger"
}

HEALTH_STATUS = {
    "very_high": "very_high_health",
    "high": "high_health",
    "medium": "medium_health",
    "low": "low_health",
    "very_low": "very_low_health"
}

ENERGY_STATUS = {
    "very_high": "very_high_energy",
    "high": "high_energy",
    "medium": "medium_energy",
    "low": "low_energy",
    "very_low": "very_low_energy"
}

SEXUAL_STATUS = {
    "non": "non_fertil",
    "very_high": "very_high_fertility",
    "high": "high_fertility",
    "medium": "medium_fertility",
    "low": "low_fertility",
    "very_low": "very_low_fertility"
}

FOOD_STATUS = {
    "non": "no_food",
    "detected": "food_detected",
    "far": "food_far",
    "medium_distance": "food_medium_distance",
    "close": "food_close",
    "very_close": "food_very_close",
    "so_close": "food_so_close",
    "very_far": "food_very_far"
}



