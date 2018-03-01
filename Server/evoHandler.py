import random

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

toolbox = base.Toolbox()


# At the moment all it does is generate a random number of layers filled with neurons
def generateInd(icls, maxLayers, maxNeurons):
    genome = list()
    numLayers = random.randint(1, maxLayers)
    for _ in range(numLayers):
        genome.append(random.randint(1, maxNeurons))
    return icls(genome)


def createPop(maxNeurons, numClients):
    creator.create("FitnessMax", base.Fitness, weights=(1.0, ))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox.register("individual", generateInd, creator.Individual, 5, 784)

    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    pop = toolbox.population(n=numClients)
    print("Population Created...")
    return pop


def evalulateInd(gen, ind):
    allResults = [[34.0, 45.0, 22.0], [44.0, 47.0, 39.0], [51.0, 45.0, 41.0]]
    return allResults[gen][ind]


def mutate(ind):
    mutant = toolbox.clone(ind)
    numLayers = mutant[0]
    layers = mutant[1:]
    tempList = []
    lowList = []
    highList = []
    tempList = mutant
    if tempList[0] > 1:
        lowList.append(tempList[0] - 1)
    else:
        lowList.append(1)
    if tempList[0] < 5:
        highList.append(tempList[0] + 1)
    else:
        highList.append(5)

    for x in tempList[1:]:
        if x > 5:
            lowList.append(x - 5)
        else:
            lowList.append(1)
        highList.append(x + 5)

    newNeuron, = tools.mutUniformInt(layers, lowList[1:], highList[1:], 0.5)
    newLayers, other2 = tools.mutUniformInt(numLayers, lowList[0], highList[0], 0.1)
    del mutant.fitness.values
    print("Original:  " + str(ind))
    print("newNeuron: " + str(newNeuron))
    print("newLayers: " + str(newNeuron))
    print("Mutant:    " + str(mutant))



toolbox.register("evaluate", evalulateInd)

population = createPop(784, 20)


for gen in range(3):
    for ind in range(3):
        fitness = evalulateInd(gen, ind)
        population[ind].fitness.value = fitness
        mutate(population[ind])
