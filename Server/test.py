import heapq
import operator

test = list()

test.append({'Parameters': {'batchSize': 572, 'learningRate': 0.0532682746497597, 'trainingEpochs': 2}, 'Processed': False, 'Model': [472], 'Result': 0.8864})
test.append({'Parameters': {'batchSize': 745, 'learningRate': 0.07499973715235769, 'trainingEpochs': 2}, 'Processed': False, 'Model': [505, 472], 'Result': 0.2822})
test.append({'Parameters': {'batchSize': 785, 'learningRate': 0.03782561058132637, 'trainingEpochs': 12}, 'Processed': False, 'Model': [767], 'Result': 0.379})
test.append({'Parameters': {'batchSize': 109, 'learningRate': 0.07499973715235769, 'trainingEpochs': 8}, 'Processed': False, 'Model': [505], 'Result': 0.8457})
test.append({'Parameters': {'batchSize': 652, 'learningRate': 0.006414251259347479, 'trainingEpochs': 8}, 'Processed': False, 'Model': [16], 'Result': 0.8643})
test.append({'Parameters': {'batchSize': 115, 'learningRate': 0.03782561058132637, 'trainingEpochs': 10}, 'Processed': False, 'Model': [858], 'Result': 0.8624})
test.append({'Parameters': {'batchSize': 607, 'learningRate': 0.07788225999844675, 'trainingEpochs': 13}, 'Processed': False, 'Model': [134], 'Result': 0.7571})
test.append({'Parameters': {'batchSize': 395, 'learningRate': 0.06781567658294421, 'trainingEpochs': 12}, 'Processed': False, 'Model': [159], 'Result': 0.8626})
test.append({'Parameters': {'batchSize': 704, 'learningRate': 0.03782561058132637, 'trainingEpochs': 10}, 'Processed': False, 'Model': [159, 517, 279, 76], 'Result': 0.9793})
test.append({'Parameters': {'batchSize': 411, 'learningRate': 0.014223888595988249, 'trainingEpochs': 12}, 'Processed': False, 'Model': [628, 554, 684, 851], 'Result': 0.8815})

pop = list()
for ind in test:
    pop.append(ind)
    if len(pop) > 5:
        lowest = 1.0
        toReplace = None
        for i, replace in enumerate(pop):
            if replace['Result'] < lowest:
                toReplace = i
                lowest = replace['Result']
        if toReplace is not None:
            del pop[toReplace]

for ind in pop:
    print(ind)
