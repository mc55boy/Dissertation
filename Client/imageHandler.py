import numpy as np
import random
from collections import Counter
from PIL import Image
import os, sys
from os import listdir
from os.path import isfile, join

baseDirectory = "/home/coopy/Downloads/101_ObjectCategories"


def changeAllImages(allFiles, minWidth, minHeight):


def imagePreprocessing(baseDir):
    dirs = os.listdir(baseDir)
    minWidth = 800000
    minHeight = 800000
    fullFileLoc = []
    counter = 0
    for directoryName in dirs:
        fullDirLoc = baseDirectory + "/" + directoryName
        onlyfiles = [f for f in listdir(fullDirLoc) if isfile(join(fullDirLoc, f))]
        for fileName in onlyfiles:
            fullFileLoc.append(fullDirLoc + "/" + fileName)
            im = Image.open(fullFileLoc[counter])
            counter += 1
            currWidth, currHeight = im.size
            if currWidth < minWidth:
                minWidth = currWidth
            if currHeight < minHeight:
                minHeight = currHeight
    print(str(minWidth) + " " + str(minHeight))
    changeAllImages(fullFileLoc, minWidth, minHeight)





imagePreprocessing(baseDirectory)
