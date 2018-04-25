import csv
import re

with open("test_edit.csv", "r") as resultsFile:
    reader = csv.reader(resultsFile, delimiter=",")
    for row in reader:
        for indString in row:
            model = list()
            paramString = indString[indString.find('],')+2:]
            paramStringList = paramString.split(",")
            model.append(float(paramStringList[0]))
            model.append(int(paramStringList[1]))
            model.append(int(paramStringList[2]))
            modelStringList = re.findall(r'\[(.*?)\]', indString)
            tmp = modelStringList[0].split(",")
            for ind in tmp:
                model.append(int(ind))
            print(model)
