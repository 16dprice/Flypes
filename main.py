import functions

runInfo = {
    3:"1",
    4:"1",
    5:"2",
    6:"3",
    7:"7",
    8:"18",
    9:"41",
    10:"123",
    11:"367",
    12:"1288"
}

totalDiagrams = []
for crNum in range(3, 13):
    ordering = int(runInfo[crNum])

    totalPDCodesForCrNum = 0

    for i in range(ordering):
        txtFileName = "knot_" + str(crNum) + "_" + str(i + 1) + ".txt"
        pdCode = functions.getPDCodeFromTxtFile("../knot_txt_files/" + txtFileName)

        # print pdCode
        allMinimalDiagrams = functions.runGetAllPDCodesDFS(pdCode)

        totalPDCodesForCrNum += len(allMinimalDiagrams)

        functions.writeKnotListToTxtFile("../flype_output/" + "knot_" + str(crNum) + "_" + str(i + 1) + "_output.txt", allMinimalDiagrams, len(allMinimalDiagrams))

        print("done with knot " + str(crNum) + " " + str(i + 1) + "\n")

    print(str(crNum) + " - " + str(totalPDCodesForCrNum))
    totalDiagrams.append((crNum, totalPDCodesForCrNum))

for (crNum, totalPDCodesForCrNum) in totalDiagrams:
    print "Number of Minimal Diagrams for crossing number " + str(crNum) + " = " + str(totalPDCodesForCrNum)