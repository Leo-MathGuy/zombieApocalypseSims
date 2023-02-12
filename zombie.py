# IMPORTS
import os
import json



# FILE
try:
    os.makedirs(os.path.dirname(__file__) + "/saves/")
except FileExistsError:
    pass

# CONSTANTS
WIDTH = 10
HEIGHT = 10

CHANCE_TO_TRANSFER_VIRUS = 0.1
CHANCE_TO_DIE_OF_VIRUS = 0.08
CHANCE_TO_EXCHANGE_ORTH = 0.15
CHANCE_TO_PLANE = 0.001

IMMUNITY_PER_DAY_MIN = 0
IMMUNITY_PER_DAY_MAX = 0.015

