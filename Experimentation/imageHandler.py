from PIL import Image
import os
from os import listdir
from os.path import isfile, join
from resizeimage import resizeimage

baseDirectory = "/home/coopy/Downloads/101_ObjectCategories"
targetDest = "/home/coopy/Downloads/resized/"


def changeAllImages(fileDictionary, minWidth, minHeight, target):
    for currDir in fileDictionary.items():
        filesInDic = currDir[1]
        for currImg in filesInDic:
            loadLoc = "/home/coopy/Downloads/101_ObjectCategories/" + currDir[0] + "/" + currImg
            if not os.path.exists(target + currDir[0]):
                os.makedirs(target + currDir[0])
            with open(loadLoc, 'r+b') as f:
                with Image.open(f) as image:
                    cover = resizeimage.resize_cover(image, [minWidth, minHeight])
                    cover.save(target + currDir[0] + "/" + currImg, image.format)
    print("Done")


def imagePreprocessing(baseDir):

    directoryDictionary = {}

    dirs = os.listdir(baseDir)
    minWidth = 800000
    minHeight = 800000

    for directoryName in dirs:
        fullDirLoc = baseDirectory + "/" + directoryName
        onlyfiles = [f for f in listdir(fullDirLoc) if isfile(join(fullDirLoc, f))]
        directoryDictionary.update({directoryName: onlyfiles})
        for fileName in onlyfiles:
            im = Image.open(fullDirLoc + "/" + fileName)
            currWidth, currHeight = im.size
            if currWidth < minWidth:
                minWidth = currWidth
            if currHeight < minHeight:
                minHeight = currHeight
    print(str(minWidth) + " " + str(minHeight))

    changeAllImages(directoryDictionary, minWidth, minHeight, targetDest)


imagePreprocessing(baseDirectory)
