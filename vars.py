WIDTH=1800
HEIGHT=900
MAX_SPEED=3
MIN_SPEED=0
WHITE=255,255,255
BLACK=0,0,0
RED=255,0,0
BROWN=209,131,53
GREEN=0,255,0

RADIUS = 10
FOOD_RADIUS = 10
RANGO_EDAD_MAXIMA = [200,250] #ticks
RANGO_PERCEPCION = [100,450]

MAX_ENERGY = 100
MAX_FOOD = 80
MAX_HEALTH = 100
MAX_LIBID = 100

INITIAL_CELLS_NUMBER = 1
INITIAL_FOOD_NUMBER = 4

#States


HUNGER_STATUS = {
    "high": "high_hunger",
    "medium": "medium_hunger",
    "low": "low_hunger"
}

HEALTH_STATUS = {
    "high": "high_health",
    "medium": "medium_health",
    "low": "low_health"
}

ENERGY_STATUS = {
    "high": "high_energy",
    "medium": "medium_energy",
    "low": "low_energy"
}

SEXUAL_STATUS = {
    "non": "non_fertil",
    "high": "high_fertility",
    "medium": "medium_fertility",
    "low": "low_fertility"
}

FOOD_STATUS = {
    "non": "no_food",
    "detected": "food_detected",
    "close": "food_close",
    "so_close": "food_so_close"
}
