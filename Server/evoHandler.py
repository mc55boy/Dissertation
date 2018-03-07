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


def getNextGeneration(originalPop, processedPop):
    lenOrg = len(originalPop)
    lenPrc = len(processedPop)
    if lenOrg == lenPrc:
        for p in range(lenPrc):
            for o in range(lenOrg):
                if processedPop[p]['ModelID'] == originalPop[o]['ModelID']:
                    fitness = processedPop[p]['Result']
                    originalPop[o]['Model'].fitness.value = fitness
                    break
    else:
        print("Amount of processed nets doesn't match original population")
    mutatedPop = mutatePopulation(originalPop)
    return originalPop, mutatedPop


def mutatePopulation(population):
    mutatedPop = list()
    print()
    for ind in population:
        print(ind['Model'])
        tempInd = mutate(ind['Model'], 20)
        ind['Model'] = tempInd
        print(tempInd)
        mutatedPop.append(ind)
    print()
    return mutatedPop


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
    del ind2.fitness.values
    return ind2
