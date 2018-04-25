from threading import Thread
from multiprocessing import Value, Pipe
import server as server
import evoHandler as evo
import time
import heapq
import csv
import os.path


def runServer(threadname, evoState, serverState, evo_conn, numClients, maxPop):
    print(threadname + " running...")
    server.main(evoState, serverState, evo_conn, numClients, maxPop)


def setupEvo(evoState, datasetInput, server_conn, maxLayers, maxPop, loadPrevious):
    evoState.value = 0
    if loadPrevious == "None":
        population = evo.createPop(datasetInput, maxLayers, maxPop)
    else:
        print("Loading architectures from " + loadPrevious)
        population = evo.loadPop(loadPrevious, maxPop)
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


def convertToCSV(ind):
    row = str(ind[0]) + "," + str(ind[1]["Model"]) + "," + str(ind[1]["Parameters"]["learningRate"]) + "," + str(ind[1]["Parameters"]["trainingEpochs"]) + "," + str(ind[1]["Parameters"]["batchSize"])
    return row


def checkPopIntegrity(loadPrevious, maxPop, datasetInput, maxLayers):
    returnPop = list()
    loadedPop = False
    if os.path.exists("result.csv"):
        returnPop = evo.loadPop("result.csv", maxPop)
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


def runEvo(threadname, evoState, serverState, server_conn, numClients, maxPop, maxLayers, loadPrevious):
    numInput = 784
    setupEvo(evoState, numInput, server_conn, maxLayers, maxPop, loadPrevious)
    counter = 0
    pop = list()
    while True:
        if serverState.value == 0:
            counter = coreWait(counter, "Waiting for clients")
        elif serverState.value == 1:
            counter = coreWait(counter, "Waiting for clients to process nets")
        elif serverState.value == 2:
            receivedPop = server_conn.recv()
            try:
                for ind in receivedPop:
                    heapq.heappush(pop, (ind['Result'], ind))
                    if len(pop) > maxPop:
                        heapq.heappop(pop)

                print()
                for ind in pop:
                    print(str(ind[0]) + " " + str(ind[1]['Model']) + " " + str(ind[1]['Parameters']))
                print()

                with open("result.csv", 'a') as resultsFile:
                    wr = csv.writer(resultsFile, lineterminator='\n')
                    for ind in pop:
                        wr.writerow([convertToCSV(ind)])
                mutationRate = 0.2
                mutatedPop = evo.nextGen(pop, maxLayers, mutationRate)
                evoState.value = 1
                server_conn.send(mutatedPop)
            except TypeError:
                print("Failure. Deleting pop and loading previous saved state")
                pop.clear()
                pop = checkPopIntegrity(loadPrevious, maxPop, numInput, maxLayers)
                evoState.value = 1
                server_conn.send(pop)


def setup(numClients):
    maxLayers = 4
    maxPop = 10

    loadPrevious = "testLoad.csv"

    server_conn, evo_conn = Pipe()
    evoState = Value('i', 0)
    serverState = Value('i', 0)

    serverThread = Thread(name="Server", target=runServer, args=("ServerThread", evoState, serverState, evo_conn, numClients, maxPop))
    evoThread = Thread(name="Evo", target=runEvo, args=("EvoThread", evoState, serverState,  server_conn, numClients, maxPop, maxLayers, loadPrevious))

    evoThread.start()
    serverThread.start()
    serverThread.join()
    evoThread.join()


# print(multiprocessing.cpu_count())
# print(len(os.sched_getaffinity(0)))
numClients = 3

setup(numClients)
