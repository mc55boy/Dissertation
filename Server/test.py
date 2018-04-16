def fitnessKey(elem):
    return elem[0]


testList = [[0, {"Hello"}], [3, {"There"}], [2, {"My"}], [4, {"Dog"}]]

sortedList = sorted(testList, key=fitnessKey)

for x in sortedList:
    print(x)
