from __future__ import print_function
import tensorflow as tf
import time
import numpy as np
from tqdm import trange


totalDataSet = list()
lastDataSet = None


# Load MNIST Dataset from file and convert to numpy array
def loadMNIST(datasetLocation):
    global totalDataSet
    MNIST_Files = ["train-images.idx3-ubyte", "train-labels.idx1-ubyte", "t10k-images.idx3-ubyte", "t10k-labels.idx1-ubyte"]
    MNIST_Headers = [4, 2, 4, 2]
    totalDataSet = []
    for datasetNum in range(len(MNIST_Files)):
        dataLocation = datasetLocation + "/" + MNIST_Files[datasetNum]
        print("Reading " + MNIST_Files[datasetNum] + "...")
        with open(dataLocation, "rb") as f:
            metaData = []
            currData = []
            for i in range(MNIST_Headers[datasetNum]):
                metaData.append(int.from_bytes(f.read(4), byteorder='big'))
            if MNIST_Headers[datasetNum] == 2:
                numBytes = 1
            else:
                numBytes = metaData[2] * metaData[3]
            rawBytes = f.read(numBytes)
            while rawBytes:
                currData.append(list(rawBytes))
                rawBytes = f.read(numBytes)
            totalDataSet.append(currData)
        print("Done")

    labelSets = [1, 3]
    for setNum in labelSets:
        tempList = []
        for sublist in totalDataSet[setNum]:
            flat_list = [0] * 10
            flat_list[sublist[0]] = 1.0
            tempList.append(flat_list)
        totalDataSet[setNum] = tempList
    print("Converting to numpy array...")
    return np.array(totalDataSet[0], dtype=np.uint8), np.array(totalDataSet[1], dtype=np.uint8), np.array(totalDataSet[2], dtype=np.uint8), np.array(totalDataSet[3], dtype=np.uint8)


def buildNet(inputNet, inputLayer):
    # initiliase Input layer for loop use
    existingLayer_Size = inputNet["structure"]["inputLayer"]
    print("INPUT: " + str(existingLayer_Size))

    existingLayer = inputLayer

    for newLayer_Size in inputNet['structure']['hiddenLayers']:
        # Create new hidden layer
        newLayer = tf.placeholder("float", [None, newLayer_Size])
        # Build weights/connections between prev and new layer
        newLayer_Weights = tf.Variable(tf.random_normal([existingLayer_Size, newLayer_Size]))
        # Build biases for new layer
        newLayer_Bias = tf.nn.dropout(tf.random_normal([newLayer_Size]), 0.9)
        # connect new layer to prev layer using the created connections and biases
        newLayer = tf.add(tf.matmul(existingLayer, newLayer_Weights), newLayer_Bias)

        existingLayer = newLayer
        existingLayer_Size = newLayer_Size

    outputClasses = inputNet["structure"]["outputLayer"]
    outputWeights = tf.Variable(tf.random_normal([existingLayer_Size, outputClasses]))
    outputBias = tf.Variable(tf.random_normal([outputClasses]))
    outputLayer = tf.matmul(existingLayer, outputWeights) + outputBias
    saver = tf.train.Saver()
    return saver, outputLayer


class neuralNet:

    def multilayerTrain(datasetLocation, layerInput, parameters):

        netInput = {"structure": {"outputLayer": 10, "inputLayer": 784, "hiddenLayers": layerInput}}
        global lastDataSet
        if lastDataSet is None or not lastDataSet == datasetLocation:
            lastDataSet = datasetLocation
            train_x, train_y, test_x, test_y = loadMNIST(datasetLocation)
        else:
            global totalDataSet
            train_x = np.array(totalDataSet[0], dtype=np.uint8)
            train_y = np.array(totalDataSet[1], dtype=np.uint8)
            test_x = np.array(totalDataSet[2], dtype=np.uint8)
            test_y = np.array(totalDataSet[3], dtype=np.uint8)

        learning_rate = parameters["learningRate"]
        # learning_rate = 0.005
        training_epochs = parameters["trainingEpochs"]
        # training_epochs = 10
        batch_size = parameters["batchSize"]
        # batch_size = 100
        # display_step = 1
        inputSize = netInput["structure"]["inputLayer"]
        outputClassNum = netInput["structure"]["outputLayer"]

        print()
        print("Learning Rate: " + str(learning_rate))
        print("Epochs:        " + str(training_epochs))
        print("Batch Size:    " + str(batch_size))
        print(layerInput)
        print()

        inputLayer = tf.placeholder("float", [None, inputSize])
        outputLayer = tf.placeholder("float", [None, outputClassNum])
        #logits = multilayer_perceptron(X)
        # Define loss and optimizer

        loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=outputLayer))
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        # change "optimizer" potentially to decay learning rate (simulated annealing) in future
        train_op = optimizer.minimize(loss_op)
        # Initializing the variables
        init = tf.global_variables_initializer()

        total_batch = int(len(train_x) / batch_size)

        batchedData = np.empty(shape=(total_batch, batch_size, inputSize), dtype=np.uint8)
        batchedLabel = np.empty(shape=(total_batch, batch_size, outputClassNum), dtype=np.uint8)

        for i in range(total_batch):
            np.copyto(batchedData[i], train_x[(i*batch_size):((i+1)*batch_size)])
            np.copyto(batchedLabel[i], train_y[(i*batch_size):((i+1)*batch_size)])

        start = time.time()
        with tf.Session() as sess:
            sess.run(init)

            # Training cycle
            for epoch in trange(training_epochs, desc='Training'):
                avg_cost = 0.
                # Loop over all batches
                for batch in trange(total_batch, desc='Batch', leave=False):

                    batch_x = batchedData[batch]
                    batch_y = batchedLabel[batch]
                    _, c = sess.run([train_op, loss_op], feed_dict={inputLayer: batch_x, outputLayer: batch_y})
                    # Compute average loss
                    avg_cost += c / total_batch
                    i += batch_size
            print("Optimization Finished!")
            end = time.time()
            print("TIME: " + str(end - start))
            print("Model saved under " + save_path)
            # Test model
            pred = tf.nn.softmax(logits)  # Apply softmax to logits
            correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(outputLayer, 1))
            # Calculate accuracy
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
            accuracyOutput = accuracy.eval({inputLayer: test_x, outputLayer: test_y})
            print("Accuracy:", accuracyOutput)
            return accuracyOutput


#neuralNet.multilayerTrain("Data/MNIST_data/", [2], {"learningRate": 0.01, "trainingEpochs": 1, "batchSize": 1000})
