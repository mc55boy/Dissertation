from threading import Thread
from multiprocessing import Value, Pipe
import server as server
import evoHandler as evo
import time
import heapq


def runServer(threadname, evoState, serverState, evo_conn, numClients):
    print(threadname + " running...")
    server.main(evoState, serverState, evo_conn, numClients)
    print("Server Thread end")


def setupEvo(evoState, datasetInput, numClients, server_conn, maxLayers):
    evoState.value = 0
    # createPop(maxNeurons, maxLayers, numClients):
    population = evo.createPop(datasetInput, maxLayers, numClients)
    server_conn.send(population)
    evoState.value = 1
    return population


def coreWait(counter, message):
    b = message + "." * counter
    print(b, end="\r")
    counter += 1
    if counter == 5:
        counter = 0
    time.sleep(0.5)
    print(" " * 50, end="\r")
    return counter


def runEvo(threadname, evoState, serverState, server_conn, numClients, maxPop, maxLayers):
    numInput = 784
    originalPop = setupEvo(evoState, numInput, numClients, server_conn, maxLayers)
    counter = 0
    pop = list()
    while True:
        if serverState.value == 0:
            counter = coreWait(counter, "Waiting for clients")
        elif serverState.value == 1:
            evoState.value = 0
            counter = coreWait(counter, "Waiting for clients to process nets")
        elif serverState.value == 2:
            processedPop = evo.transformIntoChrom(server_conn.recv())
            for ind in processedPop:
                print()
                print(ind)
                print()
                heapq.heappush(pop, (ind['Result'], ind))
                if len(pop) > maxPop:
                    heapq.heappop(pop)
            evo.nextGen(pop, maxLayers)
            newPopulation = evo.getNextGeneration(originalPop, processedPop, maxLayers)
            print()

            server_conn.send(newPopulation)
            evoState.value = 1


def setup(numClients):
    maxLayers = 4
    maxPop = 5
    server_conn, evo_conn = Pipe()
    evoState = Value('i', 0)
    serverState = Value('i', 0)

    serverThread = Thread(name="Server", target=runServer, args=("ServerThread", evoState, serverState, evo_conn, numClients))
    evoThread = Thread(name="Evo", target=runEvo, args=("EvoThread", evoState, serverState,  server_conn, numClients, maxPop, maxLayers))

    evoThread.start()
    serverThread.start()
    serverThread.join()
    evoThread.join()


numClients = 1

setup(numClients)
