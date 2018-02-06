from __future__ import print_function
import tensorflow as tf
import tensorflow.contrib.slim as slim
from tensorflow.examples.tutorials.mnist import input_data





def buildNet(inputNet, inputLayer):

    #initiliase Input layer for loop use
    existingLayer_Size = inputNet["structure"]["inputLayer"]
    print("INPUT: " + str(existingLayer_Size))

    existingLayer = inputLayer

    for newLayer_Size in inputNet["structure"]["hiddenLayers"]:
        #Create new hidden layer
        newLayer = tf.placeholder("float", [None, newLayer_Size])
        #Build weights/connections between prev and new layer
        newLayer_Weights = tf.Variable(tf.random_normal([existingLayer_Size, newLayer_Size]))
        #Build biases for new layer
        newLayer_Bias = tf.Variable(tf.random_normal([newLayer_Size]))
        #connect new layer to prev layer using the created connections and biases
        newLayer = tf.add(tf.matmul(existingLayer, newLayer_Weights), newLayer_Bias)

        existingLayer = newLayer
        existingLayer_Size = newLayer_Size


    outputClasses = inputNet["structure"]["outputLayer"]
    print("OUTPUT: " + str(outputClasses))
    outputWeights = tf.Variable(tf.random_normal([existingLayer_Size, outputClasses]))
    outputBias = tf.Variable(tf.random_normal([outputClasses]))
    outputLayer = tf.matmul(existingLayer, outputWeights) + outputBias
    return outputLayer


class neuralNet:

    def multilayerTrain(datasetLocation, netInput):

        #Get all parameters for the dataset
        learning_rate = netInput["parameters"]["learningRate"]
        training_epochs = netInput["parameters"]["training_epochs"]
        batch_size = netInput["parameters"]["batch_size"]
        display_step = 1
        inputSize = netInput["structure"]["inputLayer"]
        outputClassNum = netInput["structure"]["outputLayer"]

        mnist = input_data.read_data_sets(datasetLocation + "/", one_hot=True)
        existingLayer_Size = netInput["structure"]["inputLayer"]
        inputLayer = tf.placeholder("float", [None, inputSize])
        outputLayer = tf.placeholder("float", [None, outputClassNum])
        logits = buildNet(netInput, inputLayer)
        #logits = multilayer_perceptron(X)
        # Define loss and optimizer

        loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=outputLayer))
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        train_op = optimizer.minimize(loss_op)
        # Initializing the variables
        init = tf.global_variables_initializer()

        with tf.Session() as sess:
            sess.run(init)

            # Training cycle
            for epoch in range(training_epochs):
                avg_cost = 0.
                total_batch = int(mnist.train.num_examples/batch_size)
                # Loop over all batches
                for i in range(total_batch):
                    batch_x, batch_y = mnist.train.next_batch(batch_size)
                    # Run optimization op (backprop) and cost op (to get loss value)
                    _, c = sess.run([train_op, loss_op], feed_dict={inputLayer: batch_x,
                                                                    outputLayer: batch_y})
                    # Compute average loss
                    avg_cost += c / total_batch
                # Display logs per epoch step
                if epoch % display_step == 0:
                    print("Epoch:", '%04d' % (epoch+1), "cost={:.9f}".format(avg_cost))
            print("Optimization Finished!")

            # Test model
            pred = tf.nn.softmax(logits)  # Apply softmax to logits
            correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(outputLayer, 1))
            # Calculate accuracy
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
            print("Accuracy:", accuracy.eval({inputLayer: mnist.test.images, outputLayer: mnist.test.labels}))
