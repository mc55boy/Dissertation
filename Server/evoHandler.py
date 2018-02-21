import random

from deap import algorithms
from deap import base
from deap import creator
from deap import tools


def createPop(maxNeurons, numClients):

    creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("num_neurons", random.randint, 0, 784)
    toolbox.register("active_layers", random.randint, 1, 5)
    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.active_layers, toolbox.num_neurons, toolbox.num_neurons,
                                                                         toolbox.num_neurons, toolbox.num_neurons))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    pop = toolbox.population(n=numClients)
    print("Population Created...")
    return pop
