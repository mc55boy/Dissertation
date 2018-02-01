import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIT_data/", one_hot=True)


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

#import tensorflow as tf
#hello = tf.constant('Hello, Tensorflow')
#sess = tf.Session()
#print(sess.run(hello))
#print("Hello")
