from __future__ import print_function
import tensorflow as tf
import time
import sys
import array


def loadMNIST(datasetLocation):

    MNIST_Files = ["train-images.idx3-ubyte", "train-labels.idx1-ubyte", "t10k-images.idx3-ubyte", "t10k-labels.idx1-ubyte"]
    MNIST_Headers = [4, 2, 4, 2]
    totalDataSet = []
    for datasetNum in range(len(MNIST_Files)):
        dataLocation = datasetLocation + MNIST_Files[datasetNum]
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

    '''
    labelSets = [1, 3]
    for setNum in labelSets:
        flat_list = []
        for sublist in totalDataSet[setNum]:
            for item in sublist:
                flat_list.append(item)
        totalDataSet[setNum] = flat_list
    '''

    labelSets = [1, 3]
    for setNum in labelSets:
        tempList = []
        for sublist in totalDataSet[setNum]:
            flat_list = [0] * 10
            flat_list[sublist[0]] = 1.0
            tempList.append(flat_list)
        totalDataSet[setNum] = tempList
    print(str(len(totalDataSet[0])) + " " + str(len(totalDataSet[1])) + " " + str(len(totalDataSet[2])) + " " + str(len(totalDataSet[3])))
    return totalDataSet[0], totalDataSet[1], totalDataSet[2], totalDataSet[3]


def buildNet(inputNet, inputLayer):
    # initiliase Input layer for loop use
    existingLayer_Size = inputNet["structure"]["inputLayer"]
    print("INPUT: " + str(existingLayer_Size))

    existingLayer = inputLayer

    for newLayer_Size in inputNet["structure"]["hiddenLayers"]:
        # Create new hidden layer
        # newLayer = tf.placeholder("float", [None, newLayer_Size])
        newLayer = tf.placeholder("float", [None, newLayer_Size])
        # Build weights/connections between prev and new layer
        newLayer_Weights = tf.Variable(tf.random_normal([existingLayer_Size, newLayer_Size]))
        # Build biases for new layer
        newLayer_Bias = tf.Variable(tf.random_normal([newLayer_Size]))
        # connect new layer to prev layer using the created connections and biases
        newLayer = tf.add(tf.matmul(existingLayer, newLayer_Weights), newLayer_Bias)

        existingLayer = newLayer
        existingLayer_Size = newLayer_Size

    outputClasses = inputNet["structure"]["outputLayer"]
    outputWeights = tf.Variable(tf.random_normal([existingLayer_Size, outputClasses]))
    outputBias = tf.Variable(tf.random_normal([outputClasses]))
    outputLayer = tf.matmul(existingLayer, outputWeights) + outputBias
    return outputLayer



class neuralNet:

    def multilayerTrain(datasetLocation, layerInput):

        netInput = {"structure": {"outputLayer": 10, "inputLayer": 784, "hiddenLayers": [10, 10]}}
        train_x, train_y, test_x, test_y = loadMNIST(datasetLocation)

        # learning_rate = netInput["parameters"]["learningRate"]
        learning_rate = 0.005
        # training_epochs = netInput["parameters"]["training_epochs"]
        training_epochs = 1
        # batch_size = netInput["parameters"]["batch_size"]
        batch_size = 100
        display_step = 1
        inputSize = netInput["structure"]["inputLayer"]
        outputClassNum = netInput["structure"]["outputLayer"]

        inputLayer = tf.placeholder("float", [None, inputSize])
        outputLayer = tf.placeholder("float", [None, outputClassNum])
        logits = buildNet(netInput, inputLayer)
        print(logits)
        #logits = multilayer_perceptron(X)
        # Define loss and optimizer

        loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=outputLayer))
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        train_op = optimizer.minimize(loss_op)
        # Initializing the variables
        init = tf.global_variables_initializer()

        total_batch = int(len(train_x) / batch_size)
        batchedData = [[], []]
        for i in range(total_batch):
            batchedData[0].append(train_x[(i*batch_size):((i+1)*batch_size)])
            batchedData[1].append(train_y[(i*batch_size):((i+1)*batch_size)])

        start = time.time()

        with tf.Session() as sess:
            sess.run(init)

            # Training cycle
            for epoch in range(training_epochs):
                avg_cost = 0.
                # Loop over all batches
                # for i in range(total_batch):
                for batch in range(total_batch):
                    batch_x = batchedData[0][batch]
                    batch_y = batchedData[1][batch]
                    # print(batch)
                    '''
                    i = 0
                    while i < len(train_x):
                        start = i
                        end = i + batch_size
                        batch_x = train_x[start:end]
                        batch_y = train_y[start:end]
                    '''
                    #batch_x, batch_y = mnist.train.next_batch(batch_size)
                    # Run optimization op (backprop) and cost op (to get loss value)
                    _, c = sess.run([train_op, loss_op], feed_dict={inputLayer: batch_x,
                                                                    outputLayer: batch_y})
                    # Compute average loss
                    avg_cost += c / total_batch
                    print("Batch " + str(batch) + "/" + str(total_batch) + "  cost: " + str(avg_cost))
                    i += batch_size
                # Display logs per epoch step
                if epoch % display_step == 0:
                    print("Epoch:", '%04d' % (epoch+1), "cost={:.9f}".format(avg_cost))
            print("Optimization Finished!")
            end = time.time()
            print("TIME: " + str(end - start))
            # Test model
            pred = tf.nn.softmax(logits)  # Apply softmax to logits
            correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(outputLayer, 1))
            # Calculate accuracy
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
            accuracyOutput = accuracy.eval({inputLayer: test_x, outputLayer: test_y})
            print("Accuracy:", accuracyOutput)
            return accuracyOutput


neuralNet.multilayerTrain("Data/MNIST_data/", [2, 784, 392, 191, 90])
