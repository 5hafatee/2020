import numpy as np
import math

# lineStart : start with this symbol, for example (data.pgm), it is '[Event'
# nsTrain   : for example (data.pgm), to obtain 'Event', 'Result', 'WhiteElo' and 'BlackElo',
#             it is [[0, 8, 2], [6, 9, 2], [7, 11, 2], [8, 11, 2]]
# nsTest    : for example (data.pgm), to obtain 'Event', 'Result', 'WhiteElo' and 'BlackElo',
#             it is [[0, 8, 2], [6, 9, 2]]
# trainN    : number of training data, for example (data.pgm), it is 25000
def readPGN(fn, lineStart, nsTrain, nsTest, trainN):

    trainResult = [] # training data
    testResult = [] # test data

    # read *.pgn file
    f = open(fn, 'r')
    fLines = f.readlines()
    lines = len(fLines)
    f.close()

    # for each line
    for i in range(lines):

        # append 'row' in the dataset, to the result array
        if fLines[i][:len(lineStart)] == lineStart:
            
            temp = [] # data to save

            if len(trainResult) < trainN: # training data
                for j in range(len(nsTrain)):
                    index = nsTrain[j][0] # distance from the start line from the file
                    leftN = nsTrain[j][1] # except for left N chars
                    rightN = nsTrain[j][2] # except for right N chars

                    fLines[i+index] = fLines[i+index].split('\n')[0] # remove next-line character
                    value = fLines[i+index] # original value of this line from the file

                    temp.append(value[leftN:len(value)-rightN]) # append to the temp array
                    
            else: # test data
                for j in range(len(nsTest)):
                    index = nsTest[j][0] # distance from the start line from the file
                    leftN = nsTest[j][1] # except for left N chars
                    rightN = nsTest[j][2] # except for right N chars

                    fLines[i+index] = fLines[i+index].split('\n')[0] # remove next-line character
                    value = fLines[i+index] # original value of this line from the file

                    temp.append(value[leftN:len(value)-rightN]) # append to the temp array

            # append to the result array (training/test)
            if len(trainResult) < trainN: trainResult.append(temp) # training data
            else: testResult.append(temp) # test data

    # return the result array
    return (trainResult, testResult)

# save result array
def saveArray(fn, _2dArray):
    
    result = ''
    rows = len(_2dArray) # rows of 2d array
    cols = len(_2dArray[0]) # cols of 2d array

    # append to result
    for i in range(rows):
        for j in range(cols):
            if j < cols-1: result += str(_2dArray[i][j]) + '\t'
            else: result += str(_2dArray[i][j])

        result += '\n'

    # write to file
    f = open(fn, 'w')
    f.write(result)
    f.close()

# load result array
def loadArray(fn):
    
    # read *.pgn file
    f = open(fn, 'r')
    fLines = f.readlines()
    rows = len(fLines)
    f.close()

    result = []

    # append info to the result array
    for i in range(rows):
        thisRow = fLines[i].split('\n')[0].split('\t')
        cols = len(thisRow)

        # add this row
        temp = []
        for j in range(cols): temp.append(thisRow[j])
        result.append(temp)

    # return the result array
    return result

# get loged value
def getLogVal(val):
    try: x = float(val)
    except: x = 0
                
    if x < 0: return -math.log(1-x, 10)
    else: return math.log(1+x, 10)

# test
if __name__ == '__main__':
    # read from original data
    (trainPgn, testPgn) = readPGN('data.pgn', '[Event', [[0, 8, 2], [6, 9, 2], [7, 11, 2], [8, 11, 2]],
                                  [[0, 8, 2], [6, 9, 2]], 25000)

    # read from stockfish.csv
    fs = open('stockfish.csv', 'r')
    fsLines = fs.readlines()
    rows = len(fsLines)
    fs.close()

    for i in range(50000):
        fsLines[i+1] = fsLines[i+1].split('\n')[0] # remove new-line character from the line
        thisLineSplit = fsLines[i+1].split(',')[1].split(' ') # split moveScores
        gameLength = len(thisLineSplit)

        # extract data from moveScores
        gameData = []
        N = 10 # number of points to extract data
        for j in range(N): gameData.append(thisLineSplit[int(gameLength*j/N)])

        # handle NA data
        for j in range(len(gameData)):
            if gameData[j] == 'NA': gameData[j] = gameData[j-1]

        # add this data to trainPgn or testPgn
        if i < 25000: # training data -> add to trainPgn
            for j in range(len(gameData)):
                trainPgn[i].append(getLogVal(gameData[j]))
                
        else: # test data -> add to testPgn
            for j in range(len(gameData)):
                testPgn[i-25000].append(getLogVal(gameData[j]))

    print(np.array(trainPgn))
    print(np.array(testPgn))

    # save array
    saveArray('data_trainPgn.txt', trainPgn)
    saveArray('data_testPgn.txt', testPgn)
    
    print(np.array(loadArray('data_trainPgn.txt')))
    print(np.array(loadArray('data_testPgn.txt')))