import random
from deap import base
from deap import creator
from deap import tools
import uuid

toolbox = base.Toolbox()
population = list()


# At the moment all it does is generate a random number of layers filled with neurons
def generateInd(icls, maxLayers, maxNeurons):
    genome = list()
    numLayers = random.randint(1, maxLayers)
    for _ in range(numLayers):
        genome.append(random.randint(1, maxNeurons))
    return icls(genome)


def createPop(maxNeurons, maxLayers, numClients):
    global population
    creator.create("FitnessMax", base.Fitness, weights=(1.0, ))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox.register("individual", generateInd, creator.Individual, maxLayers, maxNeurons)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    pop = toolbox.population(numClients)
    print("Population Created...")
    for ind in pop:
        population.append({"Model": ind, "ModelID": uuid.uuid4().hex})
    return population


def getNextGeneration(inputPop):
    inputGeneration = list()
    for ind in inputPop:
        inputGeneration.append(ind['Model'])
        print(ind['Result'])


def evalulateInd(gen, ind):
    allResults = [[34.0, 45.0, 22.0], [44.0, 47.0, 39.0], [51.0, 45.0, 41.0]]
    return allResults[gen][ind]


def assignFitness(pop, fitness):
    for ind in range(len(pop)):
        pop[ind].fitness.value = fitness[ind]
    return pop


def mutate(ind, maxChange):
    ind = toolbox.clone(ind)
    lowList = []
    highList = []
    for x in ind:
        if x > maxChange:
            lowList.append(x - maxChange)
        else:
            lowList.append(1)
        highList.append(x + maxChange)

    ind2, = tools.mutUniformInt(ind, lowList, highList, 0.5)
    # del mutant.fitness.values
    print("newNeuron: " + str(ind2))
    print()
    return ind2


toolbox.register("evaluate", evalulateInd)

# population = createPop(784, 5, 3)

'''
for gen in range(3):
    for ind in range(3):
        fitness = evalulateInd(gen, ind)
        print("Original:  " + str(population[ind]))
        population[ind].fitness.value = fitness
        population[ind] = mutate(population[ind], 20)
'''
