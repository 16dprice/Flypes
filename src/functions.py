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


pdCode = getPDCodeFromTxtFile("/Users/dj/Flypes/knot_txt_files/knot_8_14.txt")
#
# graph = getGraphFromPD(pdCode)
# nonTrivialFourEdgesCuts = findNonTrivialFourEdgeCutsFromPD(pdCode)
#
# tangleList = getTanglesFromPD(pdCode)
# 
# flypeList = getFlypesFromPD(pdCode)

print getAdjMatrixFromPD(pdCode)

########################################################################################################################