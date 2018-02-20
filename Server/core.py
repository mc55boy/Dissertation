from threading import Thread
from multiprocessing import Queue
import server as server
# import evoHandler as evo
import time


def runServer(threadname, r):
    print(threadname + " running...")
    server.main(r)
    for x in range(10):
        if x < 8:
            r.put(True)
        else:
            r.put(False)
        time.sleep(0.5)
    print("Server Thread end")


def runEvo(threadname, r):
    while r.get():
        print(threadname + " True")
    print("Evo Thread end")


ready = Queue()

serverThread = Thread(name="Server", target=runServer, args=("ServerThread", ready))
evoThread = Thread(name="Evo", target=runEvo, args=("EvoThread", ready))

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
