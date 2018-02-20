from threading import Thread
from multiprocessing import Queue, Value
import server as server
# import evoHandler as evo
import time


def runServer(threadname, r, flag):
    print(threadname + " running...")
    server.main(r, flag)
    print("Server Thread end")


def runEvo(threadname, r, flag):
    while True:
        
        print(flag.value)
        time.sleep(0.5)
    print("Evo Thread end")


ready = Queue()
initialFlag = Value('i', 1)

serverThread = Thread(name="Server", target=runServer, args=("ServerThread", ready, initialFlag))
evoThread = Thread(name="Evo", target=runEvo, args=("EvoThread", ready, initialFlag))

evoThread.start()
serverThread.start()
serverThread.join()
evoThread.join()


file = open("ready.txt", "w")
file.write("False")
file.close()
time.sleep(1)
print("READY")
file = open("ready.txt", "w")
file.write("True")
file.close()
