#! /usr/bin/python2.7

import sys
import functions

# numCrossings = sys.argv[1]
# knotType = sys.argv[2]
numCrossings = 6
knotType = 1

pdCode = functions.getPDCodeFromTxtFile("../knot_txt_files/knot_" + str(numCrossings) + "_" + str(knotType) + ".txt")

allFlypes = functions.getFlypesFromPD(pdCode)

# functions.writeKnotListToTxtFile("output.txt", allFlypes, 8)
for flype in allFlypes:
    print functions.performFlype(pdCode, flype)
