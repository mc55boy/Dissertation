import random

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

creator.create("FitnessMax", base.Fitness, weights=(1.0, ))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("num_neurons", random.randint, 10, 784)
toolbox.register("active_layers", random.randint, 1, 4)
toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.active_layers, toolbox.num_neurons, toolbox.num_neurons,
                                                                     toolbox.num_neurons, toolbox.num_neurons))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def createPop(maxNeurons, numClients):
    pop = toolbox.population(n=numClients)
    print("Population Created...")
    return pop


def evalulateInd(gen, ind):
    allResults = [[34.0, 45.0, 22.0], [44.0, 47.0, 39.0], [51.0, 45.0, 41.0]]
    return allResults[gen][ind]


def mutate(ind):
    mutant = toolbox.clone(ind)
    ind2, = tools.mutGaussian(mutant, mu=0.1, sigma=0.2, indpb=0.2)
    del mutant.fitness.values
    print("1: " + str(ind))
    print("2: " + str(ind2))
    print("Mutant: " + str(mutant))
    print()

toolbox.register("evaluate", evalulateInd)



population = createPop(784, 3)


for gen in range(3):
    for ind in range(3):
        fitness = evalulateInd(gen, ind)
        population[ind].fitness.value = fitness
        mutate(population[ind])
