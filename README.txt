### PRE-INSTALLATION SETUP ###

The system was developed, tested and run on Ubuntu 16.04.2.

Ensure you are installing this system on a version of linux that supports:
    - Python3
    - Tensorflow
        - This requires a 64-bit installation. TENSORFLOW WILL NOT WORK ON A 32-BIT INSTALLATION.

That when using seperate client machines that the client is able to address the Server over a network connection e.g.:
    - Ping the IP address of the Server from the Client

### INSTALLATION PROCEEDURE ###

# Installing Server:

1. Navigate to the Server/ folder
2. chmod +x setup.sh
3. sudo ./setup.sh

# Installing Client:

1. Navigate to the Client/ folder
2. chmod +x setup.sh
3. sudo ./setup.sh


### RUN SYSTEM ###

# Single Machine use:

1. Open a terminal window and navigate to Client/ folder and run:

2. python3 main.py -i <IP Address of Server> -p <Port to connect to>

Default Settings:
- localhost:9000

As running on local machine, the above values are suggested to be left set to default

2.1 (Optional) Open more more terminal windows and repeat 2 to match the number of clients needed run on machine

3. Open a terminal window and navigate to Server/ folder and run:

4. python3 core.py -l <Number of Layers> -p <Max Pop> -e <Max Epoch>  -m <Mutation Rate> -c <Num Clients> -f <Load File>

Default Settings:
- 5 Layers
- 10 Pop
- 0.1 Mutation Rate
- 1 Client
- New population

4.1 (If multiple clients are run) The number of clients the server is expecting has to match the number of clients running



# Multiple Machine use:

1. Open a terminal window on Client Machine and navigate to Client/ folder and run:

2. python3 main.py -i <IP Address of Server> -p <Port to connect to>
    - Ensure that the IP Address given to the client matches that of the Server
    - Only change the port address if port forwarding is needed

2.1 Continue this until all clients have been instantiated across all installed machines

3. Open a terminal window aon Server Machine and navigate to Server/ folder and run:

4. python3 core.py -l <Number of Layers> -p <Max Pop> -e <Max Epoch> -m <Mutation Rate> -c <Num Clients> -f <Load File>
    - Making sure that the number of clients given matches the number of main.py run NOT the number of physical machines connected
