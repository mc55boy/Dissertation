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
    population = evo.createPop(datasetInput, numClients)
    for ind in population:
        print(ind)
    server_conn.send(population)
    evoState.value = 1


def runEvo(threadname, evoState, serverState, server_conn, numClients):
    numInput = 784
    setupEvo(evoState, numInput, numClients, server_conn)

    while True:
        if serverState.value == 0:
            print("Waiting for clients to connect...")
            time.sleep(0.5)
        elif serverState.value == 1:
            print("Waiting for clients to process nets...")
            time.sleep(0.5)
        elif serverState.value == 2:
            print("Other")

    print("All clients Connected!")


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


numClients = 2

setup(numClients)
