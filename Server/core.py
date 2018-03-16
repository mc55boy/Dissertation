from threading import Thread
from multiprocessing import Value, Pipe
# import multiprocessing
# import os
import server as server
import evoHandler as evo
import time
import heapq


def runServer(threadname, evoState, serverState, evo_conn, numClients):
    print(threadname + " running...")
    server.main(evoState, serverState, evo_conn, numClients)


def setupEvo(evoState, datasetInput, numClients, server_conn, maxLayers, maxPop):
    evoState.value = 0
    population = evo.createPop(datasetInput, maxLayers, numClients, maxPop)
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


def runEvo(threadname, evoState, serverState, server_conn, numClients, maxPop, maxLayers):
    numInput = 784
    setupEvo(evoState, numInput, numClients, server_conn, maxLayers, maxPop)
    counter = 0
    pop = list()
    while True:
        if serverState.value == 0:
            counter = coreWait(counter, "Waiting for clients")
        elif serverState.value == 1:
            # evoState.value = 0
            counter = coreWait(counter, "Waiting for clients to process nets")
        elif serverState.value == 2:
            processedPop = evo.transformIntoChrom(server_conn.recv())
            for ind in processedPop:
                # print(ind)
                heapq.heappush(pop, (ind['Result'], ind))
                if len(pop) > maxPop:
                    heapq.heappop(pop)
            '''
            print()
            print("Pop:")
            for ind in pop:
                print(ind)
            print()
            '''
            mutatedPop = evo.nextGen(pop, maxLayers)
            evoState.value = 1
            server_conn.send(mutatedPop)


def setup(numClients):
    maxLayers = 2
    maxPop = 4

    server_conn, evo_conn = Pipe()
    evoState = Value('i', 0)
    serverState = Value('i', 0)

    serverThread = Thread(name="Server", target=runServer, args=("ServerThread", evoState, serverState, evo_conn, numClients))
    evoThread = Thread(name="Evo", target=runEvo, args=("EvoThread", evoState, serverState,  server_conn, numClients, maxPop, maxLayers))

    evoThread.start()
    serverThread.start()
    serverThread.join()
    evoThread.join()


# print(multiprocessing.cpu_count())
# print(len(os.sched_getaffinity(0)))
numClients = 1

setup(numClients)
