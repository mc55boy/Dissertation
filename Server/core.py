import threading
import server as server
import time

def runServer():
    server.main()



t = threading.Thread(target=runServer)
t.start()
file = open("ready.txt", "w")
file.write("False")
file.close()
time.sleep(5)
print("READY")
file = open("ready.txt", "w")
file.write("True")
file.close()
