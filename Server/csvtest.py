import csv


def convertToCSV(ind):
    row = str(ind[0]) + "," + str(ind[1]["Model"]) + "," + str(ind[1]["Parameters"]["learningRate"]) + "," + str(ind[1]["Parameters"]["batchSize"]) + "," + str(ind[1]["Parameters"]["trainingEpochs"])
    return row


ind = (0.016544614848553962, {'clientID': 'b48ab761511146b48586f52e64fc67d6', 'Processed': False, 'Model': [577, 600], 'ModelID': '0f618fba611a4679a3739e9ffc5d6a62', 'Result': 0.016544614848553962, 'Parameters': {'learningRate': 0.07739124143430386, 'batchSize': 42, 'trainingEpochs': 5}})
pop = list()
pop.append(ind)


with open("result.csv", 'w') as resultsFile:
    wr = csv.writer(resultsFile, lineterminator='\n')
    for ind in pop:
        wr.writerow([convertToCSV(ind)])
