import networkx as nx
import itertools
import numpy as np

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

    crossing = flype["crossing"]
    tangle = flype["tangle"]

    instrands = []

    for c in tangle:
        intersect = set(c).intersection(set(crossing))
        if len(intersect) > 0:
            instrands.extend(intersect)
        if len(intersect) == 2:
            break

    return instrands


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


def parallelFlype(pdCode, flype):

    n = len(pdCode)

    tangle = flype["tangle"]
    crossing = flype["crossing"]

    instrands = getInstrands(flype)

    outstrands = []
    flatListOfTangle = sum(tangle, [])
    for s in flatListOfTangle:
        if flatListOfTangle.count(s) == 1 and s not in instrands:
            outstrands.append(s)

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

    negative = True
    if isPositiveCrossing(crossing):
        negative = False

    # print a
    # print b
    # print negative

    # get all the stuff that isn't in the tangle or crossing
    newKnot = []
    for c in pdCode:
        if c not in tangle and c != crossing:
            newKnot.append(c)

    # print newKnot

    newTangle = []
    for c in tangle:
        if isPositiveCrossing(c):
            # [a, b, c, d] -> [d, c, b, a]
            newTangle.append(list(reversed(c)))
        else:
            # [a, b, c, d] -> [b, a, d, c]
            newTangle.append(list(reversed(c[2:] + c[:2])))

    # print newTangle

    for c in newTangle:
        for i in range(4):
            if reverse:
                c[i] = c[i] + 1
            else:
                c[i] = c[i] - 1

            # if out of range
            if c[i] == 0:
                c[i] = 2 * n

            if c[i] == 2 * n + 1:
                c[i] = 1

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



########################################################################################################################

pdCode = getPDCodeFromTxtFile("../knot_txt_files/knot_8_14.txt")
#
# graph = getGraphFromPD(pdCode)
# nonTrivialFourEdgesCuts = findNonTrivialFourEdgeCutsFromPD(pdCode)
#
# tangleList = getTanglesFromPD(pdCode)
#
flypeList = getFlypesFromPD(pdCode)

print flypeList
print parallelFlype(pdCode, flypeList[0])

# testTangle = flypeList[0]["tangle"]
# testCrossing = flypeList[0]["crossing"]
# print testTangle
# print testCrossing

# print getAdjMatrixFromPD(pdCode)

########################################################################################################################