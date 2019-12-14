#! /usr/bin/python2.7

import functions as functions
import copy
import os
import sys


# crNum = sys.argv[1]
# ordering = sys.argv[2]
# pid = sys.argv[3]


dfsAllMinimalDiagrams = []


def hasPDCodeBeenFound(pdCode):

    allMinimalDiagrams = copy.deepcopy(dfsAllMinimalDiagrams)

    # functions.writeKnotListToTxtFile("p" + str(pid) + "/pdcodes.txt", allMinimalDiagrams, len(allMinimalDiagrams))
    # os.system("/home/src/example /home/src/p" + str(pid) + "/")
    # oldSize = len(functions.getPDCodesFromFile("p" + str(pid) + "/reduced_codes.txt"))

    functions.writeKnotListToTxtFile("pdcodes.txt", allMinimalDiagrams, len(allMinimalDiagrams))
    os.system("/home/src/example /home/src/")
    oldSize = len(functions.getPDCodesFromFile("reduced_codes.txt"))

    allMinimalDiagrams.append(pdCode)

    # functions.writeKnotListToTxtFile("p" + str(pid) + "/pdcodes.txt", allMinimalDiagrams, len(allMinimalDiagrams))
    # os.system("/home/src/example /home/src/p" + str(pid) + "/")
    # newSize = len(functions.getPDCodesFromFile("p" + str(pid) + "/reduced_codes.txt"))

    functions.writeKnotListToTxtFile("pdcodes.txt", allMinimalDiagrams, len(allMinimalDiagrams))
    os.system("/home/src/example /home/src/")
    newSize = len(functions.getPDCodesFromFile("reduced_codes.txt"))

    return oldSize == newSize


def getAllPDCodesDFS(pdCode):

    global dfsAllMinimalDiagrams

    if hasPDCodeBeenFound(pdCode):
        return

    dfsAllMinimalDiagrams.append(copy.deepcopy(pdCode))

    diagramsOneFlypeAway = functions.performAllFlypes(pdCode)

    for code in diagramsOneFlypeAway:
        getAllPDCodesDFS(code)


def runGetAllPDCodesDFS(crNum, ordering):
    global dfsAllMinimalDiagrams

    dfsAllMinimalDiagrams = []

    txtFileName = "knot_" + str(crNum) + "_" + str(ordering) + ".txt"
    pdCode = functions.getPDCodeFromTxtFile("../knot_txt_files/" + txtFileName)

    getAllPDCodesDFS(pdCode)

    functions.writeKnotListToTxtFile("../flype_output/" + "knot_" + str(crNum) + "_" + str(ordering) + "_output.txt", dfsAllMinimalDiagrams, len(dfsAllMinimalDiagrams))

    print("done with knot " + str(crNum) + " " + str(ordering) + "\n")

    return dfsAllMinimalDiagrams

txtFileName = "knot_12_499.txt"
pdCode = functions.getPDCodeFromTxtFile("../knot_txt_files/" + txtFileName)

print functions.writeCount
getAllPDCodesDFS(pdCode)
print functions.writeCount

functions.writeKnotListToTxtFile("../flype_output/knot_12_499_output.txt", dfsAllMinimalDiagrams, len(dfsAllMinimalDiagrams))
