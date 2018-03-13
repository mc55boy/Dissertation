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


def setupEvo(evoState, datasetInput, numClients, server_conn):
    evoState.value = 0
    maxLayers = 1
    # createPop(maxNeurons, maxLayers, numClients):
    population = evo.createPop(datasetInput, maxLayers, numClients)
    for ind in population:
        print(ind)
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


def runEvo(threadname, evoState, serverState, server_conn, numClients, maxPop):
    numInput = 784
    originalPop = setupEvo(evoState, numInput, numClients, server_conn)
    counter = 0
    pop = list()
    while True:
        if serverState.value == 0:
            counter = coreWait(counter, "Waiting for clients")
        elif serverState.value == 1:
            evoState.value = 0
            counter = coreWait(counter, "Waiting for clients to process nets")
        elif serverState.value == 2:
            processedPop = server_conn.recv()

            for ind in processedPop:
                if len(pop) > 0:
                    if ind['Result'] > heapq.nsmallest(1, pop)[0][0]:
                        if len(pop) > maxPop:
                            heapq.heappop(pop)
                        heapq.heappush(pop, (ind['Result'], ind['Model']))
                else:
                    heapq.heappush(pop, (ind['Result'], ind['Model']))
                # print(heapq.nlargest(1, pop))

            for ind in pop:
                print(ind)
            newPopulation = evo.getNextGeneration(originalPop, processedPop)
            print()
            # print(newPopulation)
            print()

            server_conn.send(newPopulation)
            evoState.value = 1


def setup(numClients):
    maxPop = 4
    server_conn, evo_conn = Pipe()
    evoState = Value('i', 0)
    serverState = Value('i', 0)

    serverThread = Thread(name="Server", target=runServer, args=("ServerThread", evoState, serverState, evo_conn, numClients))
    evoThread = Thread(name="Evo", target=runEvo, args=("EvoThread", evoState, serverState,  server_conn, numClients, maxPop))

    evoThread.start()
    serverThread.start()
    serverThread.join()
    evoThread.join()


numClients = 1

setup(numClients)
