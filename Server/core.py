from threading import Thread
from multiprocessing import Value
import server as server
import evoHandler as evo
import time


def runServer(threadname, evoReady, population):
    print(threadname + " running...")
    server.main(evoReady)
    print("Server Thread end")


def runEvo(threadname, evoReady):
    evoReady.value = 0
    for ind in population:
        print(ind)
    time.sleep(10)
    isReady.value = 1


def setup():

    evoReady = Value('i', 0)
    serverReady = Value('i', 0)
    population = evo.createPop(784, 2)

    serverThread = Thread(name="Server", target=runServer, args=("ServerThread", evoReady, serverReady, population))
    evoThread = Thread(name="Evo", target=runEvo, args=("EvoThread", evoReady, serverReady,  population))

    evoThread.start()
    serverThread.start()
    serverThread.join()
    evoThread.join()


setup()
