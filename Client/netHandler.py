from __future__ import print_function
import tensorflow as tf
import tensorflow.contrib.slim as slim
from tensorflow.examples.tutorials.mnist import input_data


mnist = None
learning_rate = 0.001
training_epochs = 5
batch_size = 100
display_step = 1

# Network Parameters
n_hidden_1 = 100 # 1st layer number of neurons
n_hidden_2 = 100 # 2nd layer number of neurons
n_input = 784 # MNIST data input (img shape: 28*28)
n_classes = 10 # MNIST total classes (0-9 digits)

# tf Graph input
Y = tf.placeholder("float", [None, n_classes])

# Store layers weight & bias
weights = {
    'h1': tf.Variable(tf.random_normal([n_input, n_hidden_1])),
    'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
    'out': tf.Variable(tf.random_normal([n_hidden_2, n_classes]))
}
biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1])),
    'b2': tf.Variable(tf.random_normal([n_hidden_2])),
    'out': tf.Variable(tf.random_normal([n_classes]))
}

networkStruct = None

def multilayer_perceptron(x):

    # Hidden fully connected layer with 256 neurons
    layer_1 = tf.add(tf.matmul(x, weights['h1']), biases['b1'])
    # Hidden fully connected layer with 256 neurons
    layer_2 = tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])
    # Output fully connected layer with a neuron for each class
    out_layer = tf.matmul(layer_2, weights['out']) + biases['out']
    return out_layer

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

        mnist = input_data.read_data_sets(datasetLocation + "/", one_hot=True)
        existingLayer_Size = netInput["structure"]["inputLayer"]
        inputLayer = tf.placeholder("float", [None, existingLayer_Size])
        logits = buildNet(netInput, inputLayer)
        #logits = multilayer_perceptron(X)
        # Define loss and optimizer

        loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=Y))
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
                                                                    Y: batch_y})
                    # Compute average loss
                    avg_cost += c / total_batch
                # Display logs per epoch step
                if epoch % display_step == 0:
                    print("Epoch:", '%04d' % (epoch+1), "cost={:.9f}".format(avg_cost))
            print("Optimization Finished!")

            # Test model
            pred = tf.nn.softmax(logits)  # Apply softmax to logits
            correct_prediction = tf.equal(tf.argmax(pred, 1), tf.argmax(Y, 1))
            # Calculate accuracy
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
            print("Accuracy:", accuracy.eval({inputLayer: mnist.test.images, Y: mnist.test.labels}))


    def simpleTrain():
        mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
        x = tf.placeholder(tf.float32, [None, 784]) #[None, 784] means a no dimensions and 784 points
        W = tf.Variable(tf.zeros([784,10]))
        b = tf.Variable(tf.zeros([10]))

        y = tf.nn.softmax(tf.matmul(x, W) + b)

        y_ = tf.placeholder(tf.float32, [None, 10])
        cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))

        train_step = tf.train.GradientDescentOptimizer(0.2).minimize(cross_entropy)

        init = tf.global_variables_initializer()

        sess = tf.Session()
        sess.run(init)

        saver = tf.train.Saver()

        iterations = 1000

        print("Training Model...")
        for i in range(iterations):
            percent = i / (iterations / 100)
            print(str.format('{0:.2f}', percent) + "% done \r", sep=' ', end='', flush=True)
            #print("%d complete\r" % percent),
            batch_xs, batch_ys = mnist.train.next_batch(100)
            sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})
        print("Model Trained!")
        save_path = saver.save(sess, "Models/model.ckpt")
        print("Model saved in path: %s" % save_path)

        correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))

        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        print(sess.run(accuracy, feed_dict={x: mnist.test.images, y_: mnist.test.labels}))
