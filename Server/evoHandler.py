import random
from deap import base
from deap import creator
from deap import tools
import uuid
from itertools import repeat
from collections import Sequence
import csv


# DEAP Proprietary data format
globICLS = None
# DEAP toolbox
toolbox = base.Toolbox()

population = list()
newCreator = True


# Generates a custom individual
def generateInd(icls, maxLayers, maxNeurons,):
    global globICLS
    globICLS = icls
    chromosome = list()

    learningRate = random.uniform(0.001, 0.1)
    training_epochs = random.randint(1, 100)
    batch_size = random.randint(10, 1000)

    # add parameters
    chromosome.append(learningRate)
    chromosome.append(training_epochs)
    chromosome.append(batch_size)
    # add random number of layers
    numLayers = random.randint(1, maxLayers)
    for _ in range(numLayers):
        chromosome.append(random.randint(1, maxNeurons))
    return icls(chromosome)


# Read from file and transforms entire population in file into
# chromoomes
def readCSV(loadPrevious):
    pop = list()
    with open(loadPrevious, "r") as resultsFile:
        reader = csv.reader(resultsFile, delimiter=",")
        for row in reader:
            for indString in row:
                model = list()

                paramString = indString[:indString.find(',[')]
                paramStringList = paramString.split(",")
                accuracy = float(paramStringList[0])
                model.append(float(paramStringList[1]))
                model.append(int(paramStringList[2]))
                model.append(int(paramStringList[3]))

                archString = indString[indString.find('[')+1:indString.find(']')]
                archStringList = archString.split(",")

                arch = list()
                for ind in archStringList:
                    arch.append(int(ind))
                model.append(arch)
                ind = list()
                ind.append(accuracy)
                ind.append(model)
                pop.append(ind)
    return pop


# Reads CSV file and outputs population of defined size (maxPop)
def loadPop(loadPrevious, maxPop):
    global population
    global newCreator
    global globICLS

    if newCreator:
        creator.create("FitnessMax", base.Fitness, weights=(1.0, ))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        globICLS = creator.Individual
        newCreator = False

    # Read entire population from file
    pop = readCSV(loadPrevious)
    # Convert chromsome into individuals that can be sent to clients
    for ind in pop[len(pop)-maxPop:]:
        newInd = {"Result": ind[0], "Parameters": {"learningRate": ind[1][0], "trainingEpochs": ind[1][1], "batchSize": ind[1][2]}, "Model": ind[1][3], "ModelID": uuid.uuid4().hex}
        population.append(newInd)
    return population


# Generate new population of defined size using DEAP Library
def createPop(maxNeurons, maxLayers, maxPop):
    global population
    global newCreator

    if newCreator:
        creator.create("FitnessMax", base.Fitness, weights=(1.0, ))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        toolbox.register("individual", generateInd, creator.Individual, maxLayers, maxNeurons)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        newCreator = False
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
        # Convert chromsome into individual that be sent to clients
        newInd = {"Result": 0.0, "Parameters": {"learningRate": parameters[0], "trainingEpochs": parameters[1], "batchSize": parameters[2]}, "Model": model, "ModelID": uuid.uuid4().hex}
        population.append(newInd)
    return population


# Receive population, perform genetic operations on it and retunr next generation
def nextGen(pop, maxLayers, mutationRate):
    nextGen = list()
    percentageChange = 15

    # Crossbreed population
    crossbreadPop = crossbreed(pop)

    # Perform muations on all in new crossbread population
    for ind in crossbreadPop:
        mutatedArch, mutatedParams = mutate(ind, percentageChange, maxLayers, mutationRate)
        modelID = uuid.uuid4().hex
        result = 0.0
        clientID = None
        processed = False
        tempInd = {'Result': result, 'Model': mutatedArch, 'Parameters': mutatedParams, 'ModelID': modelID, 'clientID': clientID, 'Processed': processed}
        nextGen.append(tempInd)
    return nextGen


# Used to return dict key as sorting item for pop list
def fitnessKey(elem):
    return elem[0]


# Selects 10 parent pairs using their fitness to decide chance of being selected
# Higher fitness = higher chance of being chosen
def rouletteSelection(pop):

    chosen = list()
    # Create the same amount of offspring to replace pop
    for i in range(len(pop)):
        twoParents = list()
        sortedPop = sorted(pop, key=fitnessKey)
        # Choose two parents
        for _ in range(2):
            # Calc sum fit for both selections as during the second run a potential
            # parent has been removed
            sumFits = sum(ind[0] for ind in sortedPop)
            u = random.random() * sumFits
            sum_ = 0
            for indNum, ind in enumerate(sortedPop):
                sum_ += ind[0]
                if sum_ > u:
                    twoParents.append(ind)
                    # Delete ind from pop so it can't get chosen again
                    del sortedPop[indNum]
                    break
        chosen.append(twoParents)
    return chosen


# Splits the cross over into two parts:
#   - Parameters: learning rate, batch size and Epochs
#   - Hidden layers
# and performs uniform crossover
def custCrossOver(parents):
    # choose which length of chromosome to work with
    lengthOfChild = len(parents[random.randint(0, 1)][1])
    childChrom = list()

    for i in range(3):
        childChrom.append(parents[random.randint(0, 1)][1][i])

    for i in range(3, lengthOfChild):
        parentChoice = random.randint(0, 1)
        if len(parents[parentChoice][1]) > i:
            childChrom.append(parents[parentChoice][1][i])
        else:
            if parentChoice == 0:
                childChrom.append(parents[1][1][i])
            else:
                childChrom.append(parents[0][1][i])
    return childChrom


def crossbreed(pop):
    editPop = list()
    for ind in pop:
        # add result first to keep data structure
        indData = list()
        indData.append(ind['Result'])

        # add chromosome to indData[1]
        # All chromosome is simply a list to make processing easier
        chromosome = list()
        chromosome.append(ind['Parameters']['learningRate'])
        chromosome.append(ind['Parameters']['trainingEpochs'])
        chromosome.append(ind['Parameters']['batchSize'])
        chromosome.extend(ind['Model'])
        indData.append(chromosome)
        editPop.append(indData)

    parentPairs = rouletteSelection(editPop)

    offspring = list()

    for parents in parentPairs:
        offspring.append(custCrossOver(parents))

    return offspring


# Edited method taken from the DEAP library to handle custom gene
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


# Mutation operation that mutates individuals genes for the
# custom chromsome used
def mutate(chromosome, percChange, maxLayers, mutationRate):
    ind = chromosome
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
        if random.randint(0, 100) < 10 and len(ind2) < (maxLayers + 4):
            # Calculate the average number of neurons in each layer
            totalNeurons = 0
            for i in range(3, len(ind2)):
                totalNeurons += ind2[i]
            avNeurons = totalNeurons / (len(ind2) - 3)

            # Create random size of new layer using normal distr
            newLayerSize = int(random.gauss(avNeurons, 50))
            if newLayerSize < 1:
                newLayerSize = 10
            # Create random insert point
            location = random.randint(3, len(ind2)-1)
            ind2.insert(location, newLayerSize)

        if random.randint(0, 100) < 10 and len(ind2) > 4:
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
