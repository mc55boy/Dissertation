from threading import Thread
from multiprocessing import Value, Pipe
import server as server
import evoHandler as evo
import time


def runServer(threadname, evoReady, serverReady, evo_conn):
    print(threadname + " running...")
    server.main(evoReady, evo_conn)
    print("Server Thread end")


def runEvo(threadname, evoReady, serverReady, server_conn):
    evoReady.value = 0
    population = evo.createPop(784, 2)
    for ind in population:
        print(ind)
    time.sleep(10)
    evoReady.value = 1
    server_conn.send(population)


def setup():

    server_conn, evo_conn = Pipe()
    evoReady = Value('i', 0)
    serverReady = Value('i', 0)

    serverThread = Thread(name="Server", target=runServer, args=("ServerThread", evoReady, serverReady, evo_conn))
    evoThread = Thread(name="Evo", target=runEvo, args=("EvoThread", evoReady, serverReady,  server_conn))

    evoThread.start()
    serverThread.start()
    serverThread.join()
    evoThread.join()


setup()
