from threading import Thread
from multiprocessing import Value
import server as server
# import evoHandler as evo
import time


def runServer(threadname, isReady):
    print(threadname + " running...")
    server.main(isReady)
    print("Server Thread end")


def runEvo(threadname, isReady):
    isReady.value = 0
    time.sleep(10)
    print("READY")
    isReady.value = 1


initialFlag = Value('i', 0)

serverThread = Thread(name="Server", target=runServer, args=("ServerThread", initialFlag))
evoThread = Thread(name="Evo", target=runEvo, args=("EvoThread", initialFlag))

evoThread.start()
serverThread.start()
serverThread.join()
evoThread.join()
