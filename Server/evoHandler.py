import random
from deap import base
from deap import creator
from deap import tools
import uuid
from itertools import repeat
from collections import Sequence

globICLS = None

toolbox = base.Toolbox()
population = list()


# At the moment all it does is generate a random number of layers filled with neurons
def generateInd(icls, maxLayers, maxNeurons,):
    global globICLS
    globICLS = icls
    genome = list()
    # add parameters

    learningRate = random.uniform(0.001, 0.1)
    training_epochs = random.randint(1, 20)
    batch_size = random.randint(10, 1000)

    genome.append(learningRate)
    genome.append(training_epochs)
    genome.append(batch_size)
    # add layers
    numLayers = random.randint(1, maxLayers)
    for _ in range(numLayers):
        # genome.append(10)
        genome.append(random.randint(1, maxNeurons))
    return icls(genome)


def transformIntoChrom(pop):
    global globICLS
    returnList = list()
    for ind in pop:
        ind['Model'] = globICLS(ind['Model'])
        result = float(ind['Result'])
        ind['Model'].fitness.value = result
        returnList.append(ind)
    return returnList


def createPop(maxNeurons, maxLayers, numClients, maxPop):
    global population
    creator.create("FitnessMax", base.Fitness, weights=(1.0, ))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox.register("individual", generateInd, creator.Individual, maxLayers, maxNeurons)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    pop = toolbox.population(maxPop)
    print("Population Created...")
    for ind in pop:
        # Split parameters and layer chromosomes
        parameters = list()
        model = list()
        for i, chrom in enumerate(ind):
            if i < 3:
                parameters.append(chrom)
            else:
                model.append(chrom)
        newInd = (0.0, {"Parameters": {"learningRate": parameters[0], "trainingEpochs": parameters[1], "batchSize": parameters[2]}, "Model": model, "ModelID": uuid.uuid4().hex})
        population.append(newInd)
    return population


def nextGen(pop, maxLayers, mutationRate):
    mutatedPop = list()
    percentageChange = 20
    for ind in pop:
        mutatedArch, mutatedParams = mutate(ind[1]['Model'], ind[1]['Parameters'], percentageChange, maxLayers, mutationRate)
        modelID = uuid.uuid4().hex
        result = 0.0
        clientID = None
        processed = False
        tempInd = (result, {'Model': mutatedArch, 'Parameters': mutatedParams, 'ModelID': modelID, 'clientID': clientID, 'Processed': processed, 'Result': result})
        mutatedPop.append(tempInd)
    return mutatedPop


# Slightly edited method taken from the DEAP library to handle custom gene
def custMut(individual, low, up, indpb):

    size = len(individual)
    if not isinstance(low, Sequence):
        low = repeat(low, size)
    elif len(low) < size:
        raise IndexError("low must be at least the size of individual: %d < %d" % (len(low), size))
    if not isinstance(up, Sequence):
        up = repeat(up, size)
    elif len(up) < size:
        raise IndexError("up must be at least the size of individual: %d < %d" % (len(up), size))

    for i, xl, xu in zip(range(size), low, up):
        if random.random() < indpb:
            # Edited part of the mutation to handle single float gene (learning rate)
            if i == 0:
                individual[i] = random.uniform(xl, xu)
            else:
                individual[i] = random.randint(xl, xu)

    return individual,


def mutate(architecture, parameters, percChange, maxLayers, mutationRate):
    ind = list()
    ind.append(parameters['learningRate'])
    ind.append(parameters['trainingEpochs'])
    ind.append(parameters['batchSize'])
    ind.extend(architecture)

    global globICLS
    ind = globICLS(ind)

    ind = toolbox.clone(ind)
    tmp = toolbox.clone(ind)
    geneSame = True
    while geneSame:
        # two lists that hold the max and min amount the ind chromosomes can change to
        lowList = []
        highList = []
        for i, chrom in enumerate(ind):
            maxChange = chrom * (percChange / 100)
            if not i == 0:
                maxChange = int(maxChange)
            # Ensure that learning rate is handled seperately

            lowList.append(chrom - maxChange)
            highList.append(chrom + maxChange)

        ind2, = custMut(ind, lowList, highList, mutationRate)
        # Make sure that only the layers are affected by this part as this adds/deletes layers
        if i > 2:
            if random.randint(0, 100) < 10 and len(ind2) < (maxLayers + 1):
                # Calculate the average number of neurons in each layer
                totalNeurons = 0
                for i in range(3, len(ind2)-1):
                    totalNeurons += ind2[i]
                avNeurons = totalNeurons / ((len(ind2)-1) - 3)

                # Create random size of new layer using normal distr
                newLayerSize = int(random.gauss(avNeurons, 1))
                # Create random insert point
                location = random.randint(3, len(ind2)-1)
                ind2.insert(location, newLayerSize)

            if random.randint(0, 100) < 10 and len(ind2) > 1:
                # Make sure that there is at least 1 hidden layer
                if len(ind2) > 4:
                    del ind2[random.randint(3, len(ind2)-1)]

        # Check if the gene has been changed (ensure forced mutation)
        if ind2 != tmp:
            geneSame = False
    del ind2.fitness.values
    mutatedParams = list()
    mutatedArch = list()
    for i, chrom in enumerate(ind2):
        if i < 3:
            mutatedParams.append(chrom)
        else:
            mutatedArch.append(chrom)

    return mutatedArch, {"learningRate": mutatedParams[0], "trainingEpochs": mutatedParams[1], "batchSize": mutatedParams[2]}
