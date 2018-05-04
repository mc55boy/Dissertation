from threading import Thread
from multiprocessing import Value, Pipe
import server as server
import evoHandler as evo
import time
import csv
import os.path
import sys
import getopt

pop = list()

'''
SERVER STATES:
0 = Waiting for clients to register with server
1 = Waiting for clients to process networks
2 = Networks have been processed and next generation is being processed

EVO STATES:
0 = Population not generate
1 = Population ready to use
'''


# Start Server thread
def runServer(threadname, evoState, serverState, evo_conn, numClients, maxPop, datasetLocation):
    print(threadname + " running...")
    server.main(evoState, serverState, evo_conn, numClients, maxPop, datasetLocation)


# Create population from either file or from evolutionary creator
def setupEvo(evoState, datasetInput, server_conn, maxLayers, maxPop, loadPrevious):
    evoState.value = 0
    if loadPrevious == "None":
        population = evo.createPop(datasetInput, maxLayers, maxPop)
    else:
        print("Loading architectures from " + loadPrevious)
        returnPop = evo.loadPop(loadPrevious, maxPop)
        global pop
        for ind in returnPop:
            print(str(ind['Result']) + " " + str(ind['Model']) + " " + str(ind['Parameters']))
            pop.append(ind)
        population = evo.nextGen(returnPop, maxLayers, 0.1)
    server_conn.send(population)
    evoState.value = 1


def coreWait(counter, message):
    b = message + "." * counter
    print(b, end="\r")
    counter += 1
    if counter == 5:
        counter = 0
    time.sleep(0.5)
    print(" " * 50, end="\r")
    return counter


# Converts population parameters to CSV String Row
def convertToCSV(ind):
    row = str(ind['Result']) + "," + str(ind["Parameters"]["learningRate"]) + "," + str(ind["Parameters"]["trainingEpochs"]) + "," + str(ind["Parameters"]["batchSize"]) + "," + str(ind["Model"])
    return row


# If there is a population error try to (in order):
#   - Load from most recent file containing most recent resultsFile
#   - Load from most load file
#   - Generate new population and start proessing new population
# This may not be needed anymore as system is more robust
def checkPopIntegrity(loadPrevious, maxPop, datasetInput, maxLayers):
    returnPop = list()
    loadedPop = False
    if os.path.exists(str(maxPop) + "p-" + str(maxLayers) + "l-result.csv"):
        returnPop = evo.loadPop(str(maxPop) + "p-" + str(maxLayers) + "l-result.csv", maxPop)
        if len(returnPop) == 0:
            if os.path.exists(loadPrevious):
                print("Results file contains no entries. Attempting to load from original load file...")
                returnPop = evo.loadPop(loadPrevious, maxPop)
                if len(returnPop) > 0:
                    loadedPop = True
    else:
        print("No results file found... Attempting to load original load file")
        if os.path.exists(loadPrevious):
            returnPop = evo.loadPop(loadPrevious, maxPop)
            if len(returnPop) > 0:
                loadedPop = True

        if not loadedPop:
            print("Loading failed. Restarting system...")
            returnPop.clear()
            returnPop = evo.createPop(datasetInput, maxLayers, maxPop)
        return returnPop


# Used to return dict key as sorting item for pop list
def sort_key(d):
    return d['Result']


# Write population to CSV file
def saveToCSV(maxPop, maxLayers):
    with open(str(maxPop) + "p-" + str(maxLayers) + "l-result.csv", 'a') as resultsFile:
        wr = csv.writer(resultsFile, lineterminator='\n')
        for ind in pop:
            wr.writerow([convertToCSV(ind)])


# Main loop of the core functionality
#   - Sets up evolution and generates Population
#   - Waits for clients to register
#   - Waits for clients to process networks
#   - Prints out most succesful population after mutated pop is processed
def runEvo(threadname, evoState, serverState, server_conn, numClients, maxPop, maxLayers, loadPrevious, mutationRate):
    global pop

    numInput = 784
    setupEvo(evoState, numInput, server_conn, maxLayers, maxPop, loadPrevious)

    counter = 0
    printMessage = True
    while True:
        if serverState.value == 0:
            counter = coreWait(counter, "Waiting for clients")
        elif serverState.value == 1:
            if printMessage:
                print("0/" + str(maxPop) + " processed...", end="\r")
                printMessage = False
        elif serverState.value == 2:
            printMessage = True
            # Receive processed population from server
            receivedPop = server_conn.recv()
            try:
                # Insert processed population into successful population
                lowest = 1.0
                for ind in receivedPop:
                    pop.append(ind)
                    if len(pop) > maxPop:
                        toReplace = None
                        for i, replace in enumerate(pop):
                            if replace['Result'] < lowest:
                                toReplace = i
                                lowest = replace['Result']
                        if toReplace is not None:
                            lowest = 1.0
                            del pop[toReplace]
                # Print out sorted population
                print()
                pop = sorted(pop, key=sort_key, reverse=True)
                for ind in pop:
                    print(str(ind['Result']) + " " + str(ind['Model']) + " " + str(ind['Parameters']))
                print()

                # Save population CSV file
                saveToCSV(maxPop, maxLayers)

                # Generate next generation
                mutatedPop = evo.nextGen(pop, maxLayers, mutationRate)
                evoState.value = 1

                # Send mutated pop to server
                server_conn.send(mutatedPop)

            # If something goes wrong somehow try to recover by loading from file
            except TypeError:
                print("Failure. Deleting pop and loading previous saved state")
                # Delete bad population
                pop.clear()
                pop = checkPopIntegrity(loadPrevious, maxPop, numInput, maxLayers)
                mutatedPop = evo.nextGen(pop, maxLayers, mutationRate)
                evoState.value = 1
                server_conn.send(mutatedPop)


def setup(numClients, maxLayers, maxPop, datasetLocation, mutationRate, loadPrevious):

    # Set up threading pipe and flags
    server_conn, evo_conn = Pipe()
    evoState = Value('i', 0)
    serverState = Value('i', 0)

    # Setup threads
    serverThread = Thread(name="Server", target=runServer, args=("ServerThread", evoState, serverState, evo_conn, numClients, maxPop, datasetLocation))
    evoThread = Thread(name="Evo", target=runEvo, args=("EvoThread", evoState, serverState,  server_conn, numClients, maxPop, maxLayers, loadPrevious, mutationRate))

    # Start and join threads
    evoThread.start()
    serverThread.start()
    serverThread.join()
    evoThread.join()


if __name__ == "__main__":
    maxLayers = 5
    maxPop = 10
    datasetLocation = "MNIST_data"
    mutationRate = 0.1
    numClients = 1
    loadPrevious = "None"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:p:m:c:f:")
    except getopt.GetoptError:
        print('core.py -l <Number of Layers> -p <Max Pop> -m <Mutation Rate> -c <Num Clients> -f <Load File>\nDefault:\n - 5 Layers\n - 10 Pop\n - 0.1 Mutation Rate\n - 1 Client\n - New population')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -i <IP Address of Server> -p <Port to connect to>\nDefault: "localhost:9000"')
            sys.exit()
        elif opt in ("-l"):

            if arg.isdigit():
                maxLayers = int(arg)
            else:
                print("Max Layer must be integer")
                sys.exit()
        elif opt in ("-p"):
            if arg.isdigit():
                maxPop = arg
            else:
                print("Map Pop must be integer")
                sys.exit()
        elif opt in ("-m"):
            try:
                mutationRate = float(arg)
                if mutationRate > 1.0:
                    print("Mutatation rate cannot be set to higher than 1.0")
                    sys.exit()
            except ValueError:
                print("Mutation rate must be float. E.g. 0.1")
                sys.exit()
        elif opt in ("-c"):
            if arg.isdigit():
                numClients = arg
            else:
                print("Num Clients must be integer")
                sys.exit()
        elif opt in ("-f"):
                loadPrevious = arg
                if not os.path.isfile(loadPrevious):
                    print("File not found. Please check file name and location")
                    sys.exit()
    setup(numClients, maxLayers, maxPop, datasetLocation, mutationRate, loadPrevious)
