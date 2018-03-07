from threading import Thread
from multiprocessing import Value, Pipe
import server as server
import evoHandler as evo
import time


def runServer(threadname, evoState, serverState, evo_conn, numClients):
    print(threadname + " running...")
    server.main(evoState, serverState, evo_conn, numClients)
    print("Server Thread end")


def setupEvo(evoState, datasetInput, numClients, server_conn):
    evoState.value = 0
    maxLayers = 20
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


def runEvo(threadname, evoState, serverState, server_conn, numClients):
    numInput = 784
    originalPop = setupEvo(evoState, numInput, numClients, server_conn)
    counter = 0
    while True:
        if serverState.value == 0:
            counter = coreWait(counter, "Waiting for clients")
        elif serverState.value == 1:
            counter = coreWait(counter, "Waiting for clients to process nets")
        elif serverState.value == 2:
            processedPop = server_conn.recv()
            originalPop, population = evo.getNextGeneration(originalPop, processedPop)
            print(population)
            server_conn.send(population)
            evoState.value = 1


def setup(numClients):

    server_conn, evo_conn = Pipe()
    evoState = Value('i', 0)
    serverState = Value('i', 0)

    serverThread = Thread(name="Server", target=runServer, args=("ServerThread", evoState, serverState, evo_conn, numClients))
    evoThread = Thread(name="Evo", target=runEvo, args=("EvoThread", evoState, serverState,  server_conn, numClients))

    evoThread.start()
    serverThread.start()
    serverThread.join()
    evoThread.join()


numClients = 1

setup(numClients)
