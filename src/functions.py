import networkx as nx
import itertools
import numpy as np
import copy

def getPDCodeFromTxtFile(path):

    pdCode = []

    file = open(path, "r")

    fileLines = file.readlines()
    for line in fileLines:
        # converts the text file lines into a list of chars that are converted to list of ints
        pdCode.append(list(map(int, line.split(","))))

    return pdCode


def getGraphFromPD(pdCode):

    numCrossings = len(pdCode)
    pdGraph = nx.MultiGraph()
    pdGraph.add_nodes_from(range(numCrossings))

    # iterate over all the strands (start from 1 and go to 2n + 1 because range in exclusive on the right side)
    for strand in range(1, 2 * numCrossings + 1):

        firstCrossingPos = 0

        while(strand not in pdCode[firstCrossingPos]):
            firstCrossingPos += 1
            if(firstCrossingPos > numCrossings):
                print("Something wrong in first while loop of generateGraphFromPD")
                print("Current strand" + strand)
                return

        secondCrossingPos = firstCrossingPos + 1
        if(secondCrossingPos > numCrossings):
            print("Something wrong before second while loop of generateGraphFromPD")
            print("Current strand" + strand)
            return
        while(strand not in pdCode[secondCrossingPos]):
            secondCrossingPos += 1
            if(secondCrossingPos > numCrossings):
                print("Something wrong in second while loop of generateGraphFromPD")
                print("Current strand" + strand)
                return

        pdGraph.add_edge(firstCrossingPos, secondCrossingPos)

    return pdGraph


def getAdjMatrixFromPD(pdCode):

    numCrossings = len(pdCode)
    adjMatrix = np.zeros((numCrossings, numCrossings), dtype=int)

    # iterate over all the strands (start from 1 and go to 2n + 1 because range in exclusive on the right side)
    for strand in range(1, 2 * numCrossings + 1):

        firstCrossingPos = 0

        while(strand not in pdCode[firstCrossingPos]):
            firstCrossingPos += 1
            if(firstCrossingPos > numCrossings):
                print("Something wrong in first while loop of generateGraphFromPD")
                print("Current strand" + strand)
                return

        secondCrossingPos = firstCrossingPos + 1
        if(secondCrossingPos > numCrossings):
            print("Something wrong before second while loop of generateGraphFromPD")
            print("Current strand" + strand)
            return
        while(strand not in pdCode[secondCrossingPos]):
            secondCrossingPos += 1
            if(secondCrossingPos > numCrossings):
                print("Something wrong in second while loop of generateGraphFromPD")
                print("Current strand" + strand)
                return

        adjMatrix[firstCrossingPos][secondCrossingPos] += 1
        adjMatrix[secondCrossingPos][firstCrossingPos] += 1

    return adjMatrix


def findNonTrivialFourEdgeCutsFromPD(pdCode):

    graph = getGraphFromPD(pdCode)

    nonTrivialFourEdgeCuts = []

    graphEdges = list(graph.edges())
    for edgeCut in list(itertools.combinations(graphEdges, 4)):

        # check to see if this edge cut is trivial (i.e. all four edges share a common vertex)
        vertexIntersection = set(edgeCut[0])
        for edgePos in range(1, 4):
            vertexIntersection = vertexIntersection.intersection(set(edgeCut[edgePos]))
        if(len(vertexIntersection) > 0):
            continue

        # if it's not trivial, see if it disconnects the graph and add it the return list if it does
        graph.remove_edges_from(edgeCut)
        if not nx.is_connected(graph.to_undirected()):
            nonTrivialFourEdgeCuts.append(edgeCut)

        # add edges back in so I'm not destroying any info about the graph
        graph.add_edges_from(edgeCut)

    return nonTrivialFourEdgeCuts


def getTanglesFromPD(pdCode):

    graph = getGraphFromPD(pdCode)
    nonTrivialFourEdgesCuts = findNonTrivialFourEdgeCutsFromPD(pdCode)

    tangleVertexList = []

    for edgeCut in nonTrivialFourEdgesCuts:
        graph.remove_edges_from(edgeCut)

        # get the components and put them in the list
        # the components are represented as a list of vertices
        # thus, the tangleVertexList is a list of sets where each set contains vertices indicating a tangle in the knot
        connectedComponents = list(nx.connected_components(graph))
        tangleVertexList.append(connectedComponents[0])
        tangleVertexList.append(connectedComponents[1])

        graph.add_edges_from(edgeCut)

    tangleList = []
    for vertexList in tangleVertexList:
        pdList = []
        for vertex in vertexList:
            pdList.append(pdCode[vertex])
        tangleList.append(pdList)

    return tangleList


def getFlypesFromPD(pdCode):

    flypeList = []

    tangleList = getTanglesFromPD(pdCode)

    for tangle in tangleList:
        outstrands = set()

        # get the outstrands
        strandLabelsList = list(itertools.chain(*tangle))
        for strand in strandLabelsList:
            if strandLabelsList.count(strand) == 1:
                outstrands.add(strand)

        # only consider crossings that are not in the pd code
        # if the crossing shares two outstrands with the tangle, append it to the flype list with the tangle
        for crossing in pdCode:
            if crossing not in tangle:
                if len(set(crossing).intersection(outstrands)) == 2:
                    flype = {"tangle": tangle, "crossing": crossing}
                    flypeList.append(flype)

    return flypeList


def getNextStrand(crossing, strand):
    return crossing[ (crossing.index(strand) + 2) % 4 ]

def getInstrands(flype):

    crossing = copy.copy(flype["crossing"])
    tangle = copy.copy(flype["tangle"])

    instrands = []

    for cr in tangle:
        intersect = set(cr).intersection(set(crossing))
        if len(intersect) > 0:
            instrands.extend(intersect)
        if len(intersect) == 2:
            break

    return instrands


def getOutstrands(flype):
    tangle = flype["tangle"]
    instrands = getInstrands(flype)

    outstrands = []
    flatListOfTangle = sum(tangle, [])
    for s in flatListOfTangle:
        if flatListOfTangle.count(s) == 1 and s not in instrands:
            outstrands.append(s)

    return outstrands


# expects flype in the form of {"crossing": crossing, "tangle": tangle}
def isFlypeParallel(flype):

    instrands = getInstrands(flype)

    crossing = flype["crossing"]

    diff1 = instrands[0] - getNextStrand(crossing, instrands[0])
    if diff1 > 1: diff1 = -1
    if diff1 < -1: diff1 = 1

    diff2 = instrands[1] - getNextStrand(crossing, instrands[1])
    if diff2 > 1: diff2 = -1
    if diff2 < -1: diff2 = 1

    return diff1 == diff2


def isPositiveCrossing(crossing):
    return ( crossing[1] - crossing[3] == 1 or crossing[1] - crossing[3] < -1 )

# expects flype in the form of {"crossing": crossing, "tangle": tangle}
def parallelFlype(pdCode, flype):

    n = len(pdCode)

    instrands = getInstrands(copy.copy(flype))
    outstrands = getOutstrands(copy.copy(flype))

    tangle = copy.copy(flype["tangle"])
    crossing = copy.copy(flype["crossing"])

    if crossing[0] in instrands:
        a = crossing[0]
        reverse = True
    else:
        a = crossing[2]
        reverse = False

    if crossing[1] in instrands:
        b = crossing[1]
    else:
        b = crossing[3]

    negative = not isPositiveCrossing(crossing)

    # print a
    # print b
    # print negative

    # get all the stuff that isn't in the tangle or crossing
    newKnot = []
    for cr in pdCode:
        if cr not in tangle and cr != crossing:
            newKnot.append(copy.copy(cr))

    # print newKnot

    newTangle = []
    for cr in tangle:
        if isPositiveCrossing(cr):
            # [a, b, c, d] -> [d, c, b, a]
            newTangle.append(list(reversed(copy.copy(cr))))
        else:
            # [a, b, c, d] -> [b, a, d, c]
            newTangle.append(list(reversed(copy.copy(cr[2:] + cr[:2]))))

    # print newTangle

    for cr in newTangle:
        for i in range(4):
            if reverse:
                cr[i] = cr[i] + 1
            else:
                cr[i] = cr[i] - 1

            # if out of range
            if cr[i] == 0:
                cr[i] = 2 * n

            if cr[i] == 2 * n + 1:
                cr[i] = 1

    # print newTangle

    if abs(a - outstrands[0]) + abs(b - outstrands[1]) == 2 * len(tangle):
        c = outstrands[0]
        d = outstrands[1]
    else:
        c = outstrands[1]
        d = outstrands[0]

    # print [c, d]

    if abs(a - c) % 2 == 1:
        # |a - c| is ODD => parity 1
        if reverse:
            # REVERSED
            if negative:
                newCrossing = [d, c, d + 1, c + 1]
            else:
                newCrossing = [d, c + 1, d + 1, c]
        else:
            # NOT REVERSED
            if negative:
                newCrossing = [d - 1, c - 1, d, c]
            else:
                newCrossing = [d - 1, c, d, c - 1]
    else:
        # |a - c| is EVEN => parity 0
        if reverse:
            # REVERSED
            if negative:
                newCrossing = [c, d, c + 1, d + 1]
            else:
                newCrossing = [c, d + 1, c + 1, d]
        else:
            # NOT REVERSED
            if negative:
                newCrossing = [c - 1, d - 1, c, d]
            else:
                newCrossing = [c - 1, d, c, d - 1]

    for i in range(4):
        if newCrossing[i] == 0:
            newCrossing[i] = 2 * n
        if newCrossing[i] == 2 * n + 1:
            newCrossing[i] = 1

    # print newCrossing

    return sorted(newKnot + newTangle + [newCrossing])


def isBoundaryInCode(code, n):
    for crossing in code:
        if 2 * n in crossing and 1 in crossing:
            return True
    return False


def ensureStrandIsInBounds(s, n):
    newS = s
    while newS <= 0:
        newS += 2 * n
    while newS > 2 * n:
        newS -= 2 * n
    return newS


def incrementCode(code, incVal, n):
    newCode = copy.copy(code)
    for cr in newCode:
        for i in range(len(cr)):
            cr[i] += incVal
            cr[i] = ensureStrandIsInBounds(cr[i], n)
    return newCode


def getNextStrand(cr, s):
    return cr[(cr.index(s) + 2) % 4]

# expects flype in the form of {"crossing": crossing, "tangle": tangle}
def antiparallelFlype(pdCode, flype):

    n = len(pdCode)

    oldTangle = copy.copy(flype["tangle"])
    oldCrossing = copy.copy(flype["crossing"])

    oldKnot = []
    for cr in pdCode:
        if cr not in oldTangle and cr != oldCrossing:
            oldKnot.append(copy.copy(cr))

    # print oldTangle
    # print oldCrossing
    # print

    count = 0

    while isBoundaryInCode(oldTangle + [oldCrossing], n) and count <= 2 * n:
        oldKnot = incrementCode(oldKnot, 1, n)
        oldTangle = incrementCode(oldTangle, 1, n)
        oldCrossing = incrementCode([oldCrossing], 1, n)[0]

        count += 1

    # print oldTangle
    # print oldCrossing

    instrands = getInstrands({"tangle": oldTangle, "crossing": oldCrossing})
    outstrands = getOutstrands({"tangle": oldTangle, "crossing": oldCrossing})

    if instrands[0] - getNextStrand(oldCrossing, instrands[0]) == 1:
        a = instrands[0]
        b = instrands[1]
    else:
        a = instrands[1]
        b = instrands[0]

    inAndOutstrands = sorted(instrands + outstrands)

    if (inAndOutstrands[0] == a and inAndOutstrands[1] == b) or (inAndOutstrands[2] == a and inAndOutstrands[3] == b):
        isParityInf = True
    else:
        isParityInf = False

    if isParityInf:
        # is parity infinity
        if outstrands[0] < outstrands[1]:
            c = outstrands[0]
            d = outstrands[1]
        else:
            c = outstrands[1]
            d = outstrands[0]
    else:
        # is NOT parity infinity
        if abs(a - outstrands[0]) + abs(b - outstrands[1]) == 2 * len(oldTangle):
            c = outstrands[0]
            d = outstrands[1]
        else:
            c = outstrands[1]
            d = outstrands[0]

    # print [a, b, c, d]

    for cr in oldTangle:
        if c in cr:
            if cr[1] == c or cr[3] == c:
                cIsOverPass = True
            else:
                cIsOverPass = False

    positive = isPositiveCrossing(oldCrossing)

    newTangle = []
    for cr in oldTangle:
        if isPositiveCrossing(cr):
            # [a, b, c, d] -> [d, c, b, a]
            newTangle.append(list(reversed(cr)))
        else:
            # [a, b, c, d] -> [b, a, d, c]
            newTangle.append(list(reversed(cr[2:] + cr[:2])))

    newKnot = oldKnot

    if isParityInf:
        # TRUE tangle is parity infinity
        if a < c:
            # TRUE a < c
            newTangle = incrementCode(newTangle, -1, n)
            for i in range(len(newKnot)):
                for j in range(4):
                    if b < newKnot[i][j] and newKnot[i][j] <= c:
                        newKnot[i][j] = ensureStrandIsInBounds(newKnot[i][j] - 2, n)
        else:
            # FALSE a > c
            newTangle = incrementCode(newTangle, 1, n)
            for i in range(len(newKnot)):
                for j in range(4):
                    if d <= newKnot[i][j] and newKnot[i][j] <= a:
                        newKnot[i][j] = ensureStrandIsInBounds(newKnot[i][j] + 2, n)

    else:
        # FALSE tangle is NOT parity infinity
        for i in range(len(newTangle)):
            for j in range(4):
                if a <= newTangle[i][j] and newTangle[i][j] <= c:
                    newTangle[i][j] = ensureStrandIsInBounds(newTangle[i][j] - 1, n)
                if d <= newTangle[i][j] and newTangle[i][j] <= b:
                    newTangle[i][j] = ensureStrandIsInBounds(newTangle[i][j] + 1, n)


    if isParityInf:
        # TRUE tangle is parity infinity
        if a < c:
            # a < c
            if positive:
                # crossing was POSITIVE
                if cIsOverPass:
                    newCrossing = [d - 1, c - 1, d, c - 2]
                else:
                    newCrossing = [c - 2, d, c - 1, d - 1]
            else:
                # crossing was NEGATIVE
                if cIsOverPass:
                    newCrossing = [d - 1, c - 2, d, c - 1]
                else:
                    newCrossing = [c - 2, d - 1, c - 1, d]
        else:
            # a > c
            if positive:
                # crossing was POSITIVE
                if cIsOverPass:
                    newCrossing = [d + 1, c + 1, d + 2, c]
                else:
                    newCrossing = [c, d + 2, c + 1, d + 1]
            else:
                # crossing was NEGATIVE
                if cIsOverPass:
                    newCrossing = [d + 1, c, d + 2, c + 1]
                else:
                    newCrossing = [c, d + 1, c + 1, d + 2]
    else:
        # FALSE tangle is not parity infinity
        if positive:
            # crossing was POSITIVE
            if cIsOverPass:
                newCrossing = [d, c, d + 1, c - 1]
            else:
                newCrossing = [c - 1, d + 1, c, d]
        else:
            # crossing was NEGATIVE
            if cIsOverPass:
                newCrossing = [d, c - 1, d + 1, c]
            else:
                newCrossing = [c - 1, d, c, d + 1]

    # ensures that every strand is within bounds
    newCrossing = incrementCode([newCrossing], 0, n)[0]

    return sorted(newKnot + newTangle + [newCrossing])


def performFlype(pdCode, flype):
    if isFlypeParallel(flype):
        return parallelFlype(pdCode, flype)
    else:
        return antiparallelFlype(pdCode, flype)


def performAllFlypes(pdCode):
    allFlypes = []
    count = 0
    for flype in getFlypesFromPD(pdCode):
        flypePerformed = performFlype(copy.deepcopy(pdCode), copy.deepcopy(flype))
        # if count == 2:
        #     print flypePerformed
        #     print isFlypeParallel(flype)
        #     print flype
            # print performFlype(copy.deepcopy(pdCode), copy.deepcopy(flype))
        # allFlypes.append(performFlype(pdCode, flype))
        allFlypes.append(flypePerformed)
        count += 1
    return allFlypes

########################################################################################################################

pdCode = getPDCodeFromTxtFile("../knot_txt_files/knot_8_14.txt")

########################################################################################################################

def listToCSVString(list):
    retStr = ""
    for val in list:
        retStr += str(val) + ","
    return retStr[0:len(retStr) - 1]


def writeKnotListToCSV(filename, knotList, numCrossings):

    f = open(filename, "w")
    f.write(str(numCrossings) + "\n")

    for knot in knotList:
        for cr in knot:
            f.write(listToCSVString(cr) + "\n")

    f.close()


allFlypesPerformed = performAllFlypes(pdCode)
writeKnotListToCSV("demofile.csv", allFlypesPerformed, len(pdCode))